#!/usr/bin/env python3
"""Recover a Vertex batch job's results into stage files after the local poller died.

    python scripts/pipeline/recover_batch.py --eval test13_meld \
        --job <id> --stage extract --config extraction_flash38_6shot

WHY THIS EXISTS. `run_pipeline.py` holds a job's results in memory and only
writes the per-document files once `run_batch` returns, so its advertised
resumability begins at the NEXT run, not mid-job: if the local process dies at
90%, every finished row is discarded even though Vertex has them. The job itself
is server-side and keeps running, and its output lands in GCS either way, so the
work is recoverable and re-submitting is pure waste.

Polls the job to completion, downloads whatever it produced, and writes the same
files `run_pipeline` would have, with the same provenance stamped on them.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import _bootstrap  # noqa: F401

import google.auth
import google.auth.transport.requests as gtr
import requests

from ideadet import config as C
from ideadet import registry
from ideadet.io import load_jsonl, write_jsonl
from ideadet.llm import vertex_batch as VB
from ideadet.pipeline import outline_pipeline as OP


def creds():
    c, proj = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    c.refresh(gtr.Request())
    return c, proj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", required=True)
    ap.add_argument("--job", required=True, help="numeric batchPredictionJobs id")
    ap.add_argument("--stage", default="extract", choices=["extract", "deleak"])
    ap.add_argument("--config", default="extraction_flash38_6shot")
    ap.add_argument("--poll", type=int, default=60)
    a = ap.parse_args()

    ev = registry.get_eval(a.eval)
    cfg = C.load(a.config, kind="pipeline")
    rows = {r["id"]: r for r in load_jsonl(ev.corpus)}
    out_dir = ev.stage_dir(a.stage)

    c, proj = creds()
    url = (f"https://aiplatform.googleapis.com/v1beta1/projects/{proj}"
           f"/locations/global/batchPredictionJobs/{a.job}")
    t0 = time.time()
    while True:
        c.refresh(gtr.Request())
        j = requests.get(url, headers={"Authorization": f"Bearer {c.token}"}).json()
        state = j.get("state")
        st = j.get("completionStats") or {}
        print(f"  [{(time.time()-t0)/60:.1f}m] {state}  ok={st.get('successfulCount','?')} "
              f"incomplete={st.get('incompleteCount','?')} fail={st.get('failedCount','0')}",
              flush=True)
        if state in ("JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED",
                     "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"):
            break
        time.sleep(a.poll)

    dest = (j.get("outputInfo") or {}).get("gcsOutputDirectory")
    if not dest:
        raise SystemExit(f"job ended {state} with no gcsOutputDirectory; nothing to recover")
    print("  output:", dest, flush=True)

    got, diag, usage = VB.parse_outputs(VB._download_output(dest), want_json=True)
    print(f"  parsed {len(got)} payloads; diagnostics "
          f"{ {k: len(v) for k, v in diag.items()} }", flush=True)

    n = 0
    for doc_id, payload in got.items():
        row = rows.get(doc_id)
        if row is None:
            print(f"  ! {doc_id} not in corpus, skipped", flush=True)
            continue
        OP.write_outline(out_dir, doc_id, payload, row, stage=a.stage,
                         extractor=cfg["model"], prompt_version=cfg.get("template", ""),
                         n_shots=cfg.get("n_shots"))
        n += 1
    if usage:
        write_jsonl(ev.path / f"usage_{a.stage}.jsonl",
                    [{"id": k, "stage": f"recovered_{a.job}", "model": cfg["model"],
                      "usage": v} for k, v in usage.items()], append=True)

    missing = [i for i in rows if not (out_dir / f"{i}.json").exists()]
    print(f"\nwrote {n} outlines to {out_dir}")
    print(f"missing {len(missing)} of {len(rows)}"
          + (f": {missing[:6]}" if missing else "")
          + ("\n  rerun run_pipeline.py to fill them; it resumes from disk." if missing else ""))
    OP.audit(out_dir, len(rows))


if __name__ == "__main__":
    sys.exit(main())
