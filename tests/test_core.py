"""CPU tests: formats, outline rendering, thresholds and verdicts, Detector records (with a fake backend)."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

import idealens.detector as D
from idealens import formats as F
from idealens.outline import Outline, as_text
from idealens.thresholds import Thresholds

DATA = Path(__file__).parent / "data"


@pytest.fixture
def th():
    return Thresholds(json.loads((DATA / "idealens_thresholds.json").read_text()), source="test")


# ---------------------------------------------------------------- formats
@pytest.mark.parametrize("v,want", [("News Article", "News Article"), ("news_article", "News Article"),
                                    ("NEWS ARTICLE", "News Article"), ("About (Pers.)", "Personal About Page"),
                                    ("User Review", "User Reviews"), ("personal-blog", "Personal Blog")])
def test_resolve(v, want):
    assert F.resolve(v) == want


@pytest.mark.parametrize("v", ["Product Page", "Transcript / Interview", "faqs", "Audio Transcript"])
def test_out_of_scope(v):
    with pytest.raises(F.OutOfScopeFormat):
        F.resolve(v)


def test_unknown_format():
    with pytest.raises(F.FormatError) as e:
        F.resolve("Poem")
    assert not isinstance(e.value, F.OutOfScopeFormat)


def test_user_format_records_original():
    a = F.user_format("news_article")
    assert (a.format, a.method, a.forced, a.original) == ("News Article", "user", False, "news_article")


# ---------------------------------------------------------------- outlines
def test_render_matches_training_rendering():
    items = [{"role_name": "Central Development", "content": " A thing happened. ", "verbatim": False},
             {"role_name": "Open Question", "content": "Whether it lasts.", "verbatim": False}]
    want = "[Central Development] A thing happened.\n[Open Question] Whether it lasts."
    assert Outline(items).render() == want
    assert as_text({"items": items}) == want
    assert as_text(json.dumps({"items": items})) == want
    assert as_text(want) == want


# ---------------------------------------------------------------- thresholds
def test_strict_rule(th):
    c = th.cut("global", 0.01)
    assert th.verdict(c, 0.01)["ai"] is False          # exactly at the cut is not flagged
    assert th.verdict(np.nextafter(c, 0), 0.01)["ai"] is True


def test_global_verdict_values(th):
    v = th.verdict(0.1, 0.01)
    assert v["ai"] is True and math.isclose(v["cut"], 0.13711697951409052)


def test_per_format_and_no_fallback(th):
    ok = th.verdict(0.2, 0.01, "per_format", format="News Article")
    assert ok["ai"] is False and math.isclose(ok["cut"], th.data["per_format"]["0.01"]["News Article"])
    assert th.verdict(0.2, 0.001, "per_format", format="News Article")["ai"] is None   # no per-format cut at 0.1%
    assert th.verdict(0.0, 0.01, "per_format")["ai"] is None                            # no format given
    forced = th.verdict(0.0, 0.01, "per_format", format="News Article", forced_format=True)
    assert forced["ai"] is None and forced["reason"] == "forced_format"


def test_verdicts_block(th):
    v = th.verdicts(0.05, format="Creative Writing", topic="Games")
    assert set(v) == {"global", "per_format", "per_topic"}
    assert set(v["global"]) == {"0.001", "0.005", "0.01", "0.02", "0.05", "0.1", "0.2"}
    assert v["per_format"]["0.01"]["ai"] is True
    assert th.verdicts(0.05, format="News Article", forced_format=True)["per_format"] == {"unavailable": "forced_format"}
    assert th.verdicts(0.05)["per_topic"] == {"unavailable": "no topic"}


def test_group_scheme():
    t = Thresholds({"model": "x/IdeaLens", "global": {"0.01": 0.2},
                    "per_group": {"course": {"0.01": {"CS101": 0.3}}}}, "test")
    assert t.verdict(0.25, 0.01, "group:course", groups={"course": "CS101"})["ai"] is True
    assert t.verdict(0.25, 0.01, "group:course", groups={"course": "BIO"})["ai"] is None
    assert t.verdicts(0.25, groups={"course": "BIO"})["group:course"] == {"unavailable": "no cut for 'BIO'"}


def test_profiles_roundtrip(tmp_path, monkeypatch, th):
    monkeypatch.setenv("IDEALENS_HOME", str(tmp_path))
    th.save_profile("essays")
    back = Thresholds.load("essays")
    assert back.data == th.data and back.source == "profile:essays"
    with pytest.raises(FileExistsError):
        th.save_profile("essays")


def test_check(th):
    with pytest.raises(ValueError):
        th.check("ProseLens", {})
    assert th.check("IdeaLens", {"extractor_model": "gemini-3.7-flash", "few_shot": True}) == []
    w = th.check("IdeaLens", {"extractor_model": "gpt-5.5", "few_shot": False})
    assert len(w) == 2


# ---------------------------------------------------------------- detector (fake backend)
class FakeBackend:
    name = "fake"

    def __init__(self, logprobs):
        self.lp = logprobs

    def encode(self, text):
        return list(range(len(text.split())))

    def score_ids(self, id_lists):
        return np.array(self.lp[:len(id_lists)], dtype=float)


def test_detector_records(th):
    lp = [[math.log(0.05), math.log(0.95)], [math.log(0.9), math.log(0.1)], [np.nan, np.nan]]
    det = D.Detector("IdeaLens", backend=FakeBackend(lp), thresholds=th)
    out = det.score_outlines(["[A] x", {"items": [{"role_name": "B", "content": "y"}], "format": "news_article"},
                              "[C] z"], format=["Creative Writing", None, None], ids=["a", "b", "c"])
    a, b, c = out
    assert a["id"] == "a" and math.isclose(a["p_human"], 0.05) and a["verdict"]["ai"] is True
    assert a["format"] == "Creative Writing" and a["format_method"] == "user"
    assert b["format"] == "News Article" and b["verdict"]["ai"] is False       # outline's own format used
    assert c["p_human"] is None and "error" in c
    assert det.score_outline("[A] x", format="Creative Writing")["verdicts"]["per_format"]["0.01"]["ai"] is True


def test_detector_rejects_document_for_outline_model(th):
    det = D.Detector("IdeaLens", backend=FakeBackend([[0.0, 0.0]]), thresholds=th)
    with pytest.raises(ValueError):
        det.score_documents(["some text"])


def test_long_input_warning(th):
    det = D.Detector("IdeaLens", backend=FakeBackend([[0.0, -1.0]]), thresholds=th)
    r = det.score_outline("w " * 5000)
    assert any("outside the validated range" in w for w in r["warnings"])


def test_bad_user_format_raises(th):
    det = D.Detector("IdeaLens", backend=FakeBackend([[0.0, 0.0]]), thresholds=th)
    with pytest.raises(F.OutOfScopeFormat):
        det.score_outline("[A] x", format="Product Page")


def test_registry_and_input_kinds(th):
    from idealens import registry
    assert len(registry.MODELS) == 12 and all(m.implemented for m in registry.MODELS.values())
    with pytest.raises(KeyError):
        registry.get("NoSuchModel")

    class Echo(FakeBackend):
        """logit_human = 0, logit_ai = -(number of words), so P(human) falls with length; records what it saw."""
        def __init__(self):
            self.seen = []

        def encode(self, text):
            self.seen.append(text)
            return text.split()

        def score_ids(self, id_lists):
            return np.array([[0.0, -float(len(x))] for x in id_lists])

    outline = {"items": [{"role_name": "A", "content": "one two"}, {"role_name": "B", "content": "three"}]}
    thr = lambda name: Thresholds(th.data | {"model": f"x/{name}"}, "test")
    roles = D.Detector("IdeaLens-ModernBERT-L-RolesOnly", backend=Echo(), thresholds=thr("IdeaLens-ModernBERT-L-RolesOnly"))
    roles.score_outline(outline)
    assert roles.backend.seen == ["[A]\n[B]"]
    items = D.Detector("IdeaLens-ModernBERT-L-PerItem", backend=Echo(), thresholds=thr("IdeaLens-ModernBERT-L-PerItem"))
    r = items.score_outline(outline)
    assert items.backend.seen == ["[A] one two", "[B] three"] and r["pooling"] == "logit_mean"
    p1, p2 = 1 / (1 + math.exp(-3)), 1 / (1 + math.exp(-2))       # items of 3 and 2 words
    want = 1 / (1 + math.exp(-(math.log(p1 / (1 - p1)) + math.log(p2 / (1 - p2))) / 2))
    assert math.isclose(r["p_human"], want) and len(r["item_p_human"]) == 2
    full = D.Detector("IdeaLens-ModernBERT-L", backend=Echo(), thresholds=thr("IdeaLens-ModernBERT-L"))
    full.score_outlines([outline, "[A] one two\n[B] three"])
    assert full.backend.seen == ["[A] one two\n[B] three"] * 2
    items.backend.seen.clear()
    items.score_outline("[A] one two\n[B] three")                  # a rendered string is split into items
    assert items.backend.seen == ["[A] one two", "[B] three"]


def test_resume_retries_provider_failures(tmp_path):
    """A rerun keeps finished records and out-of-scope results, and redoes records whose provider call failed."""
    import json
    from types import SimpleNamespace as NS
    from idealens import cli
    inp, out = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    inp.write_text("".join(json.dumps({"id": i, "text": "t"}) + "\n" for i in "abcd"))
    recs = [{"id": "a", "format": "News Article"},
            {"id": "b", "format": None, "format_error": "out_of_scope"},
            {"id": "c", "format": None, "format_error": "missing from batch output"},
            {"id": "d", "format": "News Article", "outline": {"meta": {"error": "no reply"}}}]
    out.write_text("".join(json.dumps(r) + "\n" for r in recs))
    a = NS(input=str(inp), output=str(out))
    assert [r["id"] for r in cli._todo(NS(**vars(a)), cli._classify_failed)] == ["c"]
    out.write_text("".join(json.dumps(r) + "\n" for r in recs))
    recs[2]["outline"] = {"meta": {"error": "document has no usable format (missing from batch output)"}}
    out.write_text("".join(json.dumps(r) + "\n" for r in recs))
    todo = cli._todo(a, cli._extract_failed)
    assert [r["id"] for r in todo] == ["c", "d"]
    assert [json.loads(l)["id"] for l in out.read_text().splitlines()] == ["a", "b"]
    assert [json.loads(l)["id"] for l in (tmp_path / "out.jsonl.failed.jsonl").read_text().splitlines()] == ["c", "c", "d"]


def test_vllm_fit_check(monkeypatch, tmp_path):
    """The vLLM backend refuses weights that cannot fit before starting the engine."""
    import pytest
    torch = pytest.importorskip("torch")
    from idealens.backends import vllm as V
    (tmp_path / "model.safetensors").write_bytes(b"")
    monkeypatch.setattr(V, "_weight_bytes", lambda w: 59 * 2 ** 30)
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.cuda, "get_device_properties", lambda i: type("P", (), {"total_memory": 44 * 2 ** 30}))
    with pytest.raises(RuntimeError, match="80 GB GPU"):
        V._check_fits(str(tmp_path), 0.9, 1)
    V._check_fits(str(tmp_path), 0.9, 2)   # two 44 GiB GPUs hold it
    monkeypatch.setattr(torch.cuda, "get_device_properties", lambda i: type("P", (), {"total_memory": 80 * 2 ** 30}))
    V._check_fits(str(tmp_path), 0.9, 1)


def test_cli_backend_defaults_to_the_models_own(monkeypatch):
    """`idealens score --model <non-Nemotron>` must not force the vLLM backend."""
    from idealens import cli, detector
    seen = {}
    monkeypatch.setattr(detector, "Detector", lambda **kw: seen.update(kw) or "det")
    a = cli.build_parser().parse_args(["score", "x.jsonl", "-o", "y.jsonl", "--model", "IdeaLens-LogisticClassifier"])
    cli._detector(a)
    assert seen["backend"] is None


def test_dry_run_scoring_estimate_backends():
    """`run --dry-run` must work when --backend is left to the model, and price Tinker scoring in dollars."""
    from idealens import cli, cost
    docs = ["word " * 400] * 10
    for argv, want in ((["run", "x.jsonl", "-o", "y.jsonl"], "vllm"),
                       (["run", "x.jsonl", "-o", "y.jsonl", "--model", "IdeaLens-ModernBERT-L"], "hf"),
                       (["run", "x.jsonl", "-o", "y.jsonl", "--backend", "tinker"], "tinker")):
        a = cli.build_parser().parse_args(argv)
        assert cli._scoring_backend(a) == want
    r = cost.estimate(docs, ["News Article"] * 10, scoring_backend="tinker")
    assert r["scoring"]["backend"] == "tinker" and 0 < r["scoring"]["usd"] < 0.1
    r = cost.estimate(docs, ["News Article"] * 10, scoring_backend=None, detector_input="document")
    assert r["scoring"]["gpu_minutes_one_a100"] > 0
    assert "on Tinker" in cost.format_report(cost.estimate(docs, ["News Article"] * 10, scoring_backend="tinker"))


def test_public_tinker_checkpoints():
    from idealens import registry
    assert registry.get("IdeaLens").extra["tinker_path"].startswith("tinker://")
    assert registry.get("ProseLens").extra["tinker_path"].startswith("tinker://")
    assert not registry.get("IdeaLens-NoParaphrase").extra.get("tinker_path")


def test_help_and_package_carry_the_citation():
    import idealens
    from idealens import cli
    assert "arXiv:2610.06778" in idealens.CITATION and "Rajendhran" in idealens.CITATION
    help_text = cli.build_parser().format_help()
    assert "https://arxiv.org/abs/2610.06778" in help_text and "@article{idealens2026" in help_text
