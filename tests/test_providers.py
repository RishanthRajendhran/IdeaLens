"""Provider request shapes and reply parsing with fake SDK clients (no network), and the cost arithmetic."""
import math
from types import SimpleNamespace as NS

import pytest

from idealens import prompts, cost
from idealens.providers import make

EX = prompts.extraction_prompt("A document.", "News Article")
CL = prompts.classification_prompt("A document.")


# ---------------------------------------------------------------- OpenAI-style
class FakeCompletions:
    def __init__(self, text="{}", provider=None, cost_usd=None):
        self.calls, self.text, self.provider, self.cost_usd = [], text, provider, cost_usd

    def create(self, **kw):
        self.calls.append(kw)
        usage = NS(prompt_tokens=100, completion_tokens=40, prompt_tokens_details={"cached_tokens": 60},
                   completion_tokens_details={"reasoning_tokens": 30}, model_extra={"cost": self.cost_usd},
                   model_dump=lambda: {"prompt_tokens": 100, "completion_tokens": 40,
                                       "prompt_tokens_details": {"cached_tokens": 60},
                                       "completion_tokens_details": {"reasoning_tokens": 30}})
        return NS(choices=[NS(message=NS(content=self.text), finish_reason="stop")], usage=usage,
                  model_extra={"provider": self.provider} if self.provider else {})


def _openai(monkeypatch, kind="openai", **kw):
    pytest.importorskip("openai")
    prov = make(kind, kw.pop("model", "gpt-5.5"), **kw)
    fake = FakeCompletions(provider="SomeHost" if kind == "openrouter" else None,
                           cost_usd=0.01 if kind == "openrouter" else None)
    prov.client = NS(chat=NS(completions=fake))
    return prov, fake


def test_openai_request_and_reply(monkeypatch):
    prov, fake = _openai(monkeypatch)
    r = prov.generate(EX)
    kw = fake.calls[0]
    assert kw["model"] == "gpt-5.5" and kw["reasoning_effort"] == "high" and kw["seed"] == prompts.SEED
    assert kw["max_completion_tokens"] == 64000 and kw["response_format"]["json_schema"]["strict"] is False
    assert kw["messages"][0] == {"role": "system", "content": EX.system}
    assert r.text == "{}" and r.usage == {"input": 100, "cached_input": 60, "output": 40, "reasoning": 30}
    prov.generate(CL)
    assert "reasoning_effort" not in fake.calls[1] and "response_format" not in fake.calls[1]


def test_compatible_defaults(monkeypatch):
    prov, fake = _openai(monkeypatch, kind="compatible", model="my-model", base_url="http://localhost:8000/v1")
    prov.generate(EX)
    kw = fake.calls[0]
    assert "max_tokens" in kw and "reasoning_effort" not in kw and "response_format" not in kw


def test_openrouter(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "x")
    import idealens.providers.openai_compat as oc
    monkeypatch.setattr(oc, "catalog_entry", lambda m: {"context_length": 131072,
                                                        "top_provider": {"max_completion_tokens": 16000}})
    prov, fake = _openai(monkeypatch, kind="openrouter", model="org/model", strict_json=True, full_precision=True)
    r = prov.generate(EX)
    body = fake.calls[0]["extra_body"]
    assert body["reasoning"] == {"effort": "high"} and body["usage"] == {"include": True}
    assert body["provider"]["require_parameters"] is True and "bf16" in body["provider"]["quantizations"]
    assert fake.calls[0]["max_tokens"] <= 16000
    assert r.host == "SomeHost" and r.cost_usd == 0.01


def test_openrouter_refuses_prompt_that_cannot_fit(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "x")
    import idealens.providers.openai_compat as oc
    monkeypatch.setattr(oc, "catalog_entry", lambda m: {"context_length": 32768, "top_provider": {}})
    prov, fake = _openai(monkeypatch, kind="openrouter", model="org/small")
    r = prov.generate(EX)
    assert r.text is None and "context" in r.error and not fake.calls


# ---------------------------------------------------------------- Anthropic
class FakeStream:
    def __init__(self, msg): self.msg = msg
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def get_final_message(self): return self.msg


def _claude_msg(text="{}", stop="end_turn", model="claude-opus-5-5"):
    return NS(content=[NS(type="thinking", thinking=""), NS(type="text", text=text)], stop_reason=stop, model=model,
              stop_details=NS(category="cyber") if stop == "refusal" else None,
              usage=NS(input_tokens=10, cache_read_input_tokens=50000, cache_creation_input_tokens=0, output_tokens=900))


def _claude(monkeypatch, msg, **kw):
    pytest.importorskip("anthropic")
    prov = make("anthropic", kw.pop("model", None), **kw)
    calls = []

    def stream(**k):
        calls.append(k)
        return FakeStream(msg)
    prov.client = NS(messages=NS(stream=stream), beta=NS(messages=NS(stream=stream)))
    return prov, calls


def test_claude_request(monkeypatch):
    prov, calls = _claude(monkeypatch, _claude_msg())
    r = prov.generate(EX)
    kw = calls[0]
    assert kw["model"] == "claude-opus-5-5" and kw["thinking"] == {"type": "adaptive"}
    assert kw["output_config"] == {"effort": "high"} and kw["max_tokens"] == 64000
    assert kw["system"][0]["cache_control"] == {"type": "ephemeral"} and kw["system"][0]["text"] == EX.system
    assert kw["fallbacks"] == "default" and kw["betas"] == ["server-side-fallback-2026-07-01"]
    assert "temperature" not in kw and "seed" not in kw
    assert r.text == "{}" and r.usage == {"input": 50010, "cached_input": 50000, "cache_write": 0, "output": 900}
    prov.generate(CL)
    assert calls[1]["output_config"] == {"effort": "low"} and calls[1]["max_tokens"] >= 4096


def test_claude_refusal_and_fallback_host(monkeypatch):
    prov, _ = _claude(monkeypatch, _claude_msg(stop="refusal"))
    r = prov.generate(EX)
    assert r.text is None and "refused (cyber)" in r.error
    prov, _ = _claude(monkeypatch, _claude_msg(model="claude-opus-4-8"))
    assert prov.generate(EX).host == "served by claude-opus-4-8"


def test_claude_haiku_budget_and_no_fallbacks(monkeypatch):
    prov, calls = _claude(monkeypatch, _claude_msg(), model="claude-haiku-4-5", fallbacks=True)
    prov.generate(EX)
    kw = calls[0]
    assert kw["thinking"]["type"] == "enabled" and kw["thinking"]["budget_tokens"] < kw["max_tokens"]
    assert "output_config" not in kw and "fallbacks" not in kw


# ---------------------------------------------------------------- cost arithmetic
def test_cost_math():
    e = cost.StageEstimate("x", requests=10, input_tokens=1_000_000, shared_prefix_tokens=800_000,
                           output_tokens=100_000, output_tokens_p90=200_000, groups=1)
    p = {"in": 1.0, "cached_in": 0.1, "out": 10.0, "batch": True}
    c = cost._cost(e, p, batch=False)
    assert math.isclose(c["no_cache"], 1.0 + 1.0)
    # 80,000 prefix tokens of the first request at full price, 720,000 cached
    assert math.isclose(c["cached"], (1_000_000 - 720_000) * 1e-6 + 720_000 * 0.1e-6 + 1.0)
    assert math.isclose(cost._cost(e, p, batch=True)["no_cache"], 1.0)
    pw = p | {"cache_write": 1.25}
    cw = cost._cost(e, pw, batch=False)
    assert math.isclose(cw["cached"], (1_000_000 - 720_000 - 80_000) * 1e-6 + 80_000 * 1.25e-6 + 720_000 * 0.1e-6 + 1.0)


def test_estimate_and_actual():
    r = cost.estimate(["w " * 800] * 20, formats=["News Article"] * 10 + [None] * 10, provider="vertex",
                      model="gemini-3.7-flash", mode="batch")
    names = [s["stage"] for s in r["stages"]]
    assert names[0] == "classify" and names[-1] == "extract" and r["total_usd"]["cached"] < r["total_usd"]["no_cache"]
    none = cost.estimate(["w"], formats=["News Article"], provider="openai", model="unknown-model")
    assert none["total_usd"] == {} and any("no price" in n for n in none["notes"])
    recs = [{"outline": {"meta": {"provider": "vertex", "model": "gemini-3.7-flash",
                                  "usage": {"input": 1_000_000, "cached_input": 0, "output": 100_000,
                                            "reasoning": 400_000}}}}]
    a = cost.actual(recs)
    assert math.isclose(a["cost_usd_online"], 0.75 + 0.5 * 3.75) and math.isclose(a["cost_usd_batch"], a["cost_usd_online"] / 2)


def test_openai_batch_rejected_as_a_whole_raises(monkeypatch):
    """A batch OpenAI fails at validation (here: a model the Batch API does not serve) must raise, not come back as
    per-record errors that a resumed run would then skip."""
    prov, _ = _openai(monkeypatch, model="gpt-6.1-sol")
    err = NS(code="model_not_found", message="The provided model 'gpt-6.1-sol' is not supported by the Batch API.")
    failed = NS(id="batch_x", status="failed", errors=NS(data=[err, err]), request_counts=NS(completed=0, failed=0),
                output_file_id=None, error_file_id=None)
    prov.client.files = NS(create=lambda **kw: NS(id="file_x"), content=lambda fid: NS(text=""))
    prov.client.batches = NS(create=lambda **kw: failed, retrieve=lambda bid: failed)
    with pytest.raises(RuntimeError, match="not supported by the Batch API"):
        prov.run_batch({"0": EX}, log=lambda *a: None)


def test_vertex_without_credentials_fails_at_construction(monkeypatch):
    """Missing credentials must stop the run before any request, not come back as an error on every record."""
    import subprocess
    google_auth = pytest.importorskip("google.auth")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "p")
    monkeypatch.delenv("VERTEX_API_KEY", raising=False)
    monkeypatch.setattr(google_auth, "default", lambda **kw: (_ for _ in ()).throw(RuntimeError("no ADC")))
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: (_ for _ in ()).throw(FileNotFoundError("gcloud")))
    with pytest.raises(RuntimeError, match="no Vertex credentials.*no ADC"):
        make("vertex", "gemini-3.7-flash")
