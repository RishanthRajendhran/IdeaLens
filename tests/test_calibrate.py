"""calibrate: the project's rules, profiles, provenance, and (dev) a reproduction of the published IdeaLens cuts."""
import json
import os
import math
from pathlib import Path

import numpy as np
import pytest

import idealens as il
from idealens.calibrate import derive
from idealens.thresholds import Thresholds


def test_rules():
    rng = np.random.default_rng(0)
    p = rng.uniform(size=3000)
    fmt = ["A"] * 2500 + ["B"] * 400 + ["C"] * 100
    d = derive(p, {"format": fmt})
    assert math.isclose(d["global"]["0.01"], float(np.quantile(p, 0.01)))
    assert {"0.001", "0.005"} <= set(d["not_estimable"]) and "0.01" in d["global"]   # 3000 * 0.005 = 15 < 25
    pa = p[:2500]
    w = 2500 / (2500 + 2500)
    assert math.isclose(d["per_format"]["0.01"]["A"], d["global"]["0.01"] + w * (np.quantile(pa, 0.01) - d["global"]["0.01"]))
    assert "B" not in d["per_format"]["0.01"]            # 400 * 0.01 = 4 below the cut: not estimable
    assert "B" in d["per_format"]["0.1"] and "C" not in d["per_format"]["0.1"]   # C has < 200 documents


def test_not_estimable_message():
    d = derive(np.linspace(0, 1, 1000))
    assert d["not_estimable"]["0.01"] == "needs 2,500 human documents"


def _recs(n=4000, ai=500, seed=0):
    rng = np.random.default_rng(seed)
    meta = {"provider": "vertex", "model": "gemini-3.7-flash", "few_shot": True}
    h = [{"id": i, "model": "IdeaLens", "backend": "vllm", "format_method": "llm", "outline_meta": meta,
          "p_human": float(rng.beta(8, 1)), "format": "News Article", "course": "X" if i % 2 else "Y", "y": "human"}
         for i in range(n)]
    a = [{"id": n + i, "model": "IdeaLens", "backend": "vllm", "format_method": "llm", "outline_meta": meta,
          "p_human": float(rng.beta(1, 8)), "format": "News Article", "course": "X", "y": "ai"} for i in range(ai)]
    return h + a


def test_calibrate_profile_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("IDEALENS_HOME", str(tmp_path))
    th = il.calibrate(_recs(), "IdeaLens", save_as="essays", group_by=["course"], label_field="y")
    back = Thresholds.load("essays")
    assert back.data == th.data and back.data["calibration"]["n_humans"] == 4000
    assert back.data["provenance"]["extractor_model"] == "gemini-3.7-flash" and back.data["provenance"]["backend"] == "vllm"
    assert set(back.data["per_group"]["course"]["0.05"]) == {"X", "Y"}
    rep = back.data["report"]["detection_rate_at_global_cut"]["0.01"]
    assert rep["tpr"] > 0.9 and rep["ci95"][0] <= rep["tpr"] <= rep["ci95"][1]
    # the profile works in a verdict and checks the run that uses it
    assert back.verdict(0.0, 0.05, "group:course", groups={"course": "X"})["ai"] is True
    assert back.verdict(0.0, 0.01, "group:course", groups={"course": "X"})["ai"] is None   # 2,000 humans: 20 < 25
    assert back.check("IdeaLens", {"extractor_model": "gpt-5.5"})[0].startswith("extractor_model is 'gpt-5.5'")
    with pytest.raises(FileExistsError):
        il.calibrate(_recs(), "IdeaLens", save_as="essays")


def test_calibrate_refuses_mixed_inputs():
    r = _recs(n=3000, ai=0)
    r[0]["outline_meta"] = {"provider": "openai", "model": "gpt-5.5", "few_shot": True}
    with pytest.raises(ValueError, match="mix"):
        il.calibrate(r, "IdeaLens")
    with pytest.raises(ValueError, match="scored by"):
        il.calibrate(_recs(n=3000, ai=0), "ProseLens")


CAL = Path(os.environ.get("IDEALENS_CALIBRATION_DIR", "/nonexistent"))   # the project's calibration outputs


@pytest.mark.skipif(not (CAL / "thresholds.json").exists(), reason="project data not here")
def test_reproduces_published_idealens_cuts():
    """Refit IdeaLens's cuts from the stored calibration scores; they must equal the canonical thresholds.json."""
    canon = json.load(open(CAL / "thresholds.json"))["models"]["nemotron_1m_full"]
    z = np.load(CAL / "nemotron_1m_full__imported.npz", allow_pickle=True)
    d = derive(z["p_human"], {"format": z["fmt"], "topic": z["topic"]})
    for k, v in canon["global"].items():
        assert math.isclose(d["global"][str(float(k))], v, rel_tol=1e-12)
    for scheme in ("format", "topic"):
        for k, cells in canon[scheme].items():
            mine = d[f"per_{scheme}"].get(str(float(k)), {})
            assert set(mine) == set(cells), (scheme, k)
            for g, v in cells.items():
                assert math.isclose(mine[g], v, rel_tol=1e-12), (scheme, k, g)
