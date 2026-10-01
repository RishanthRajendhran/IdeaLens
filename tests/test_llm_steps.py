"""Classification, force-fitting, extraction (with repair), the pipeline and the CLI, with a fake provider."""
import json
import math

import numpy as np
import pytest

import idealens as il
from idealens import cli, formats as F
from idealens.providers import Provider, Reply

LABELS = il.classify.__globals__["F"]  # noqa (keeps flake quiet)


def good_outline(fmt):
    role = sorted(il.extract.__globals__["prompts"].assets.extraction()["formats"][fmt]["role_names"])[0]
    return json.dumps({"document_description": "d", "global_themes": ["t"],
                       "items": [{"role_name": role, "content": "an idea", "verbatim": False}]})


class FakeLLM(Provider):
    """Replies by prompt kind. script: {doc_text: {"classify": str, "force_fit": str, "extract": [replies...]}}"""
    name, model = "fake", "fake-1"

    def __init__(self, script):
        self.script, self.calls = script, []

    def generate(self, p):
        doc = p.user.split("Content: ```\n", 1)[-1].split("\n```", 1)[0] if p.kind != "extract" else \
            p.user[len("<document>\n"):-len("\n</document>")]
        self.calls.append((p.kind, doc, len(p.extra_user)))
        s = self.script[doc]
        if p.kind == "extract":
            r = s["extract"][len(p.extra_user) // 2]
            return Reply(None, error="HTTP 500") if r is None else Reply(r, {"input": 10, "output": 5})
        return Reply(s[p.kind], {"input": 3, "output": 1})


def test_classify_llm_paths():
    llm = FakeLLM({"news": {"classify": "K"}, "shop": {"classify": "Q", "force_fit": "D"},
                   "blog": {"classify": "Personal Blog"}, "junk": {"classify": "??"}})
    out = il.classify(["news", "shop", "blog", "junk"], provider=llm)
    assert out[0].format == "News Article" and not out[0].forced
    assert out[1].format == "News Article" and out[1].forced and out[1].original == "Product Page"
    assert out[2].format == "Personal Blog"
    assert out[3].format is None and "unreadable" in out[3].error
    nf = il.classify(["shop"], provider=FakeLLM({"shop": {"classify": "Q"}}), force_fit=False)[0]
    assert nf.format is None and nf.error == "out_of_scope" and nf.original == "Product Page"


def test_extract_repair_and_failures():
    fmt = "News Article"
    llm = FakeLLM({"ok": {"extract": [good_outline(fmt)]},
                   "fixed": {"extract": ["not json", '```json\n' + good_outline(fmt) + '\n```']},
                   "bad": {"extract": ['{"items": []}'] * 3},
                   "down": {"extract": [None]}})
    out = il.extract(["ok", "fixed", "bad", "down"], fmt, provider=llm, max_repairs=2)
    assert out[0].items and out[0].meta["repairs"] == 0 and out[0].meta["few_shot"] is True
    assert out[1].items and out[1].meta["repairs"] == 1
    assert not out[2].items and out[2].meta["error"].startswith("invalid reply")
    assert out[3].meta["error"] == "HTTP 500"
    assert out[1].meta["usage"] == {"input": 20, "output": 10}   # summed over the repair
    assert out[0].meta["prompt_version"] == "train_v391+excerpts+en"


def test_extract_rejects_unknown_role():
    fmt = "News Article"
    bad = json.dumps({"document_description": "d", "global_themes": [],
                      "items": [{"role_name": "Made Up Role", "content": "x", "verbatim": False}]})
    out = il.extract(["d"], fmt, provider=FakeLLM({"d": {"extract": [bad]}}), max_repairs=0)[0]
    assert "not one of the allowed roles" in out.meta["error"]


def test_extract_needs_format():
    out = il.extract(["d"], [None], provider=FakeLLM({}))[0]
    assert "needs a format" in out.meta["error"]
    oos = il.extract(["d"], [F.FormatAssignment(None, "llm", error="out_of_scope")], provider=FakeLLM({}))[0]
    assert "out_of_scope" in oos.meta["error"]


class FakeBackend:
    name = "fake"

    def encode(self, text):
        return list(range(len(text.split())))

    def score_ids(self, id_lists):
        return np.array([[math.log(0.05), math.log(0.95)]] * len(id_lists))


@pytest.fixture
def det():
    from pathlib import Path
    th = il.Thresholds(json.loads((Path(__file__).parent / "data/idealens_thresholds.json").read_text()), "test")
    return il.Detector("IdeaLens", backend=FakeBackend(), thresholds=th)


def test_run_pipeline(det):
    fmt = "News Article"
    llm = FakeLLM({"given": {"extract": [good_outline(fmt)], "classify": "K"},
                   "unlabelled": {"classify": "K", "extract": [good_outline(fmt)]},
                   "shop": {"force_fit": "D", "extract": [good_outline(fmt)]},
                   "fails": {"classify": "K", "extract": ['{"x": 1}'] * 3}})
    recs = il.run(["given", "unlabelled", "shop", "fails"], det, formats=["news_article", None, "Product Page", None],
                  force_fit=True, check_format=True, provider=llm)
    g, u, s, f = recs
    assert g["format_method"] == "user" and g["verdict"]["ai"] is True and g["format_check"]["agrees"] is True
    assert u["format_method"] == "llm" and u["outline"]["items"]
    assert s["forced_format"] and s["original_format"] == "Product Page"
    assert s["verdicts"]["per_format"] == {"unavailable": "forced_format"}
    assert f["p_human"] is None and "invalid reply" in f["error"]
    assert not any(c[0] == "classify" and c[1] == "shop" for c in llm.calls)   # force-fit only, no first pass


def test_run_given_out_of_scope_without_force_fit(det):
    recs = il.run(["shop"], det, formats=["Product Page"], provider=FakeLLM({}))
    assert recs[0]["p_human"] is None and recs[0]["format"] is None


def test_run_unknown_format_is_an_error(det):
    with pytest.raises(F.FormatError):
        il.run(["x"], det, formats=["Poem"], provider=FakeLLM({}))


def test_cli_classify_extract_resume(tmp_path, monkeypatch):
    fmt = "News Article"
    script = {"a": {"classify": "K", "extract": [good_outline(fmt)]},
              "b": {"classify": "Q", "force_fit": "D", "extract": [good_outline(fmt)]}}
    llm = FakeLLM(script)
    monkeypatch.setattr(cli, "_provider", lambda a: llm)
    src = tmp_path / "docs.jsonl"
    src.write_text("".join(json.dumps({"id": k, "text": k, "keep": 1}) + "\n" for k in script))
    cli.main(["classify", str(src), "-o", str(tmp_path / "fmt.jsonl")])
    cli.main(["classify", str(src), "-o", str(tmp_path / "fmt.jsonl")])       # resume: nothing new
    rows = [json.loads(l) for l in open(tmp_path / "fmt.jsonl")]
    assert len(rows) == 2 and rows[0]["keep"] == 1 and rows[1]["forced_format"] is True
    cli.main(["extract", str(tmp_path / "fmt.jsonl"), "-o", str(tmp_path / "out.jsonl")])
    outs = [json.loads(l) for l in open(tmp_path / "out.jsonl")]
    assert all(o["outline"]["items"] for o in outs) and outs[1]["format_method"] == "llm"
