"""Command line. Every command reads and writes JSONL, keeps the input record's fields, and appends to its output;
records whose id is already in the output are skipped, so an interrupted run resumes by re-running the command.
classify, extract and run also retry records whose provider call failed (moving them to <output>.failed.jsonl).

    idealens models
    idealens classify docs.jsonl -o fmt.jsonl        [--method llm|weborganizer] [--no-force-fit]
    idealens extract  fmt.jsonl  -o outlines.jsonl   [--format F] [--no-few-shot]
    idealens score    outlines.jsonl -o scores.jsonl [--model IdeaLens] [--backend vllm|hf|logistic]
    idealens run      docs.jsonl -o scores.jsonl     [--format F] [--force-fit] [--check-format]

Fields: `text` (document), `url` (optional), `format` (optional; a record's own format wins over --format), `topic`,
`id`, and `outline` (written by extract, read by score). LLM options: --provider
gemini|vertex|openai|anthropic|openrouter|compatible, --llm-model,
--mode online|batch (batch needs a provider with a batch API; Vertex also needs --gcs-bucket), --workers.
Scoring options: --model, --backend, --weights, --fpr, --scheme, --thresholds FILE|PROFILE, --group-by FIELD ...
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _read_jsonl(path):
    f = sys.stdin if path == "-" else open(path)
    for n, line in enumerate(f):
        if line.strip():
            rec = json.loads(line)
            rec.setdefault("id", n)
            yield rec


def _classify_failed(r):
    """No format for a reason a rerun can fix (no reply, unreadable reply, failed batch); out_of_scope is a result."""
    return r.get("format") is None and r.get("format_error") not in (None, "out_of_scope")


def _extract_failed(r):
    """No outline. Redoing it costs nothing when the input still has no format (extract stops before any request),
    and picks the record up once `classify` has been rerun."""
    o = r.get("outline") or {}
    return bool((o.get("meta") or {}).get("error"))


def _todo(a, failed=None):
    """Records of the input not yet in the output. With `failed`, output records it flags are moved to
    <output>.failed.jsonl and redone, so a rerun retries provider failures instead of keeping them."""
    out = Path(a.output)
    kept = [json.loads(l) for l in out.open() if l.strip()] if out.exists() else []
    if failed is not None:
        bad = [r for r in kept if failed(r)]
        if bad:
            kept = [r for r in kept if not failed(r)]
            with Path(str(out) + ".failed.jsonl").open("a") as fh:
                fh.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in bad)
            with out.open("w") as fh:
                fh.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in kept)
            print(f"retrying {len(bad)} failed record(s) (moved to {out}.failed.jsonl)", file=sys.stderr)
    done = {r["id"] for r in kept}
    todo = [r for r in _read_jsonl(a.input) if r["id"] not in done]
    print(f"{len(todo)} to do, {len(done)} already in {out}", file=sys.stderr)
    return todo


def _chunks(todo, a):
    size = len(todo) if getattr(a, "mode", "online") == "batch" else a.chunk  # one job per batch run
    for s in range(0, len(todo), max(1, size)):
        yield todo[s:s + size]


def _write(a, recs):
    with Path(a.output).open("a") as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def _provider(a):
    from .providers import make
    kw = {}
    if a.provider == "vertex":
        kw = {k: v for k, v in (("project", a.project), ("location", a.location), ("gcs_bucket", a.gcs_bucket)) if v}
    elif a.provider == "openrouter":
        kw = {"strict_json": a.strict_json, "full_precision": a.full_precision,
              "providers": a.route_to.split(",") if a.route_to else None}
    elif a.provider == "compatible":
        kw = {"base_url": a.base_url, "api_key": a.api_key}
    elif a.provider == "anthropic":
        kw = {"fallbacks": not a.no_fallbacks}
    if a.max_output_tokens and a.provider in ("openai", "openrouter", "compatible", "anthropic"):
        kw["max_output_tokens"] = a.max_output_tokens
    return make(a.provider, a.llm_model, **kw)


def _default_model(a):
    from .providers.gemini import DEFAULT_MODEL
    from .providers.anthropic import DEFAULT_MODEL as CLAUDE
    return a.llm_model or {"gemini": DEFAULT_MODEL, "vertex": DEFAULT_MODEL, "anthropic": CLAUDE}.get(a.provider)


def _dry_run(a, records, need_classify, extract=True):
    from .cost import estimate, format_report
    from . import formats as F, prompts
    texts = [r[a.text_field] for r in records]
    fmts = []
    for r, need in zip(records, need_classify):
        f = None if need else _fmt(r, getattr(a, "format", None))
        f = f.format if isinstance(f, F.FormatAssignment) else (F.resolve(f) if f else None)
        fmts.append(f)
    # build every request exactly as a real run would (validates formats and inputs), then estimate
    for t, f in zip(texts, fmts):
        if f and extract:
            prompts.extraction_prompt(t, f, not getattr(a, "no_few_shot", False))
        elif not f:
            prompts.classification_prompt(t)
    r = estimate(texts, fmts, need_classify=need_classify, provider=a.provider, model=_default_model(a) or "?",
                 few_shot=not getattr(a, "no_few_shot", False), mode=a.mode, extract=extract,
                 price_in=a.price_in, price_out=a.price_out, price_cached=a.price_cached,
                 scoring_backend=getattr(a, "backend", "vllm"))
    print(format_report(r))
    if a.dry_run_json:
        Path(a.dry_run_json).write_text(json.dumps(r, indent=1))


def _detector(a):
    from .detector import Detector
    kw = {"model": a.model, "backend": a.backend, "fpr": a.fpr, "scheme": a.scheme, "thresholds": a.thresholds}
    if a.weights:
        kw["weights"] = a.weights
    if a.backend == "hf" and a.hf_mode:
        kw["mode"] = a.hf_mode
    return Detector(**kw)


def _fmt(r: dict, default=None):
    """A record's format: the FormatAssignment a classify step wrote (method, forced, original kept), else the given
    format string, else the default."""
    from .formats import FormatAssignment
    if r.get("format_method"):
        return FormatAssignment(r.get("format"), r["format_method"], bool(r.get("forced_format")),
                                r.get("original_format"), error=r.get("format_error"))
    return r.get("format") or default


def _log(msg):
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------------------------------------------------- commands
def cmd_models(a):
    from .registry import MODELS
    for m in MODELS.values():
        status = "supported" if m.implemented else "not yet supported"
        print(f"{m.name:38s} reads {m.input:9s} backends {','.join(m.backends):16s} {status}")


def cmd_classify(a):
    from .classify import classify
    todo = _todo(a, _classify_failed)
    if a.dry_run:
        return _dry_run(a, todo, [True] * len(todo), extract=False) if a.method == "llm" else \
            print(f"weborganizer runs locally: no API cost ({len(todo):,} documents)")
    prov = _provider(a) if a.method == "llm" else None
    for chunk in _chunks(todo, a):
        res = classify([r[a.text_field] for r in chunk], [r.get(a.url_field, "") or "" for r in chunk], a.method,
                       force_fit=not a.no_force_fit, provider=prov, mode=a.mode, workers=a.workers, device=a.device,
                       log=_log)
        _write(a, [r | f.to_dict() for r, f in zip(chunk, res)])


def cmd_extract(a):
    from .extract import extract
    todo = _todo(a, _extract_failed)
    if a.dry_run:
        return _dry_run(a, todo, [False] * len(todo))
    prov = _provider(a)
    for chunk in _chunks(todo, a):
        # a classify record whose format is None (out of scope, not force-fitted) must not fall back to --format
        fmts = [_fmt(r, a.format) for r in chunk]
        outs = extract([r[a.text_field] for r in chunk], fmts, provider=prov, few_shot=not a.no_few_shot,
                       mode=a.mode, workers=a.workers, log=_log)
        _write(a, [r | {"outline": o.to_dict()} for r, o in zip(chunk, outs)])


def cmd_score(a):
    from . import formats as F
    if a.format:
        F.resolve(a.format)  # fail before loading any weights
    todo = _todo(a)
    if not todo:
        return
    with _detector(a) as det:
        doc = det.spec.input == "document"
        field = a.input_field or ("text" if doc else "outline")
        for chunk in _chunks(todo, a):
            common = dict(format=[_fmt(r, a.format) for r in chunk], topic=[r.get("topic") for r in chunk],
                          groups=[{g: r.get(g) for g in a.group_by} for r in chunk], ids=[r["id"] for r in chunk])
            if doc:
                res = det.score_documents([r[field] for r in chunk], **common)
            else:
                res = det.score_outlines([r[field] for r in chunk], **common)
            _write(a, [_merge(r, s) for r, s in zip(chunk, res)])


def cmd_run(a):
    from . import formats as F
    from .pipeline import run
    if a.format:
        try:
            F.resolve(a.format)
        except F.OutOfScopeFormat:
            if not a.force_fit:
                raise
    todo = _todo(a, lambda r: _classify_failed(r) or _extract_failed(r))
    if not todo:
        return
    if a.dry_run:
        from .registry import get
        doc = get(a.model).input == "document"
        need = [not doc and not (r.get("format") or a.format) for r in todo]
        return _dry_run(a, todo, need, extract=not doc)
    prov = _provider(a)
    with _detector(a) as det:
        for chunk in _chunks(todo, a):
            res = run([r[a.text_field] for r in chunk], det, formats=[r.get("format") or a.format for r in chunk],
                      urls=[r.get(a.url_field, "") or "" for r in chunk], ids=[r["id"] for r in chunk],
                      topics=[r.get("topic") for r in chunk], groups=[{g: r.get(g) for g in a.group_by} for r in chunk],
                      classify_method=a.method, force_fit=a.force_fit, check_format=a.check_format, provider=prov,
                      mode=a.mode, few_shot=not a.no_few_shot, workers=a.workers, log=_log)
            _write(a, [_merge(r, s) for r, s in zip(chunk, res)])


def cmd_calibrate(a):
    """Fit cuts from human documents: scored records are used as they are; outlines are scored first; raw
    documents go through the whole pipeline first (a --dry-run estimates that cost)."""
    from .calibrate import calibrate
    recs = list(_read_jsonl(a.input))
    if not recs:
        raise SystemExit("no records")
    if all(r.get("p_human") is not None for r in recs):
        scored = recs
    else:
        if a.dry_run:
            from .registry import get
            doc = get(a.model).input == "document"
            need = [not doc and not (r.get("format") or a.format) and not r.get("outline") for r in recs]
            return _dry_run(a, [r for r in recs if not r.get("outline")], need, extract=not doc)
        from .pipeline import run
        with _detector(a) as det:
            if all(r.get("outline") for r in recs) and det.spec.input != "document":
                res = det.score_outlines([r["outline"] for r in recs], format=[_fmt(r, a.format) for r in recs],
                                         topic=[r.get("topic") for r in recs], ids=[r["id"] for r in recs])
            else:
                res = run([r[a.text_field] for r in recs], det, formats=[r.get("format") or a.format for r in recs],
                          urls=[r.get(a.url_field, "") or "" for r in recs], ids=[r["id"] for r in recs],
                          topics=[r.get("topic") for r in recs], classify_method=a.method, force_fit=a.force_fit,
                          provider=_provider(a), mode=a.mode, few_shot=not a.no_few_shot, workers=a.workers, log=_log)
        scored = [_merge(r, s) for r, s in zip(recs, res)]
        if a.scored_out:
            Path(a.scored_out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in scored))
    th = calibrate(scored, a.model, save_as=a.save_as, out=a.out, group_by=a.group_by, label_field=a.label_field,
                   human_value=a.human_value, overwrite=a.overwrite)
    g = th.data["global"]
    print(f"fitted on {th.data['calibration']['n_humans']:,} human documents: " +
          ", ".join(f"{float(k):.1%} FPR -> {v:.5f}" for k, v in g.items()), file=sys.stderr)
    if th.data.get("not_estimable"):
        print("not estimable: " + ", ".join(f"{float(k):.1%} ({v})" for k, v in th.data["not_estimable"].items()),
              file=sys.stderr)
    if th.data.get("report"):
        print(json.dumps(th.data["report"], indent=1))
    print(f"saved: {th.source if a.save_as else a.out}", file=sys.stderr)


def cmd_cost(a):
    from .cost import actual
    recs = list(_read_jsonl(a.input))
    r = actual(recs, a.provider, a.llm_model)
    print(json.dumps(r, indent=1))


def _merge(inp: dict, rec: dict) -> dict:
    """Input fields first, then the result (result fields win); a scored outline object stays as `outline`."""
    return {**inp, **rec}


# ---------------------------------------------------------------------------------------------------------- parser
def build_parser():
    ap = argparse.ArgumentParser(prog="idealens", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models", help="list the detectors").set_defaults(fn=cmd_models)

    def io(p):
        p.add_argument("input", help="JSONL file, or - for stdin")
        p.add_argument("-o", "--output", required=True)
        p.add_argument("--chunk", type=int, default=500, help="records per call batch and per output flush (online)")

    def llm(p):
        p.add_argument("--provider", default="gemini",
                       choices=["gemini", "vertex", "openai", "anthropic", "openrouter", "compatible"])
        p.add_argument("--llm-model", help="default gemini-3.7-flash (the extractor the published cuts assume); "
                                           "claude-opus-5-5 for anthropic; required for the others")
        p.add_argument("--base-url", help="compatible: the endpoint, e.g. http://localhost:8000/v1")
        p.add_argument("--api-key", help="compatible: the endpoint's key, if it needs one")
        p.add_argument("--strict-json", action="store_true", help="openrouter: only hosts that enforce the JSON schema")
        p.add_argument("--route-to", help="openrouter: comma-separated hosts to use, in order, with no fallback")
        p.add_argument("--full-precision", action="store_true", help="openrouter: exclude quantised hosts")
        p.add_argument("--no-fallbacks", action="store_true", help="anthropic: no server-side refusal fallback")
        p.add_argument("--max-output-tokens", type=int, help="cap the reply length (default 64,000 for extraction)")
        p.add_argument("--dry-run", action="store_true", help="estimate tokens and cost; send nothing")
        p.add_argument("--dry-run-json", help="also write the estimate as JSON")
        p.add_argument("--price-in", type=float, help="USD per 1M input tokens (for models not in the price table)")
        p.add_argument("--price-out", type=float, help="USD per 1M output tokens")
        p.add_argument("--price-cached", type=float, help="USD per 1M cached input tokens")
        p.add_argument("--mode", default="online", choices=["online", "batch"])
        p.add_argument("--workers", type=int, default=8, help="concurrent online requests")
        p.add_argument("--project"); p.add_argument("--location"); p.add_argument("--gcs-bucket")
        p.add_argument("--text-field", default="text"); p.add_argument("--url-field", default="url")

    def classify_opts(p):
        p.add_argument("--method", default="llm", choices=["llm", "weborganizer"])
        p.add_argument("--device", default="cpu", help="weborganizer only")

    def scoring(p):
        p.add_argument("--model", default="IdeaLens")
        p.add_argument("--backend", default=None, choices=["vllm", "hf", "logistic"],
                       help="default: the model's own (vllm for the Nemotron models, hf for ModernBERT and Qwen)")
        p.add_argument("--hf-mode", choices=["merged", "adapter"])
        p.add_argument("--weights", help="local weights directory instead of the model repo")
        p.add_argument("--fpr", type=float, default=0.01)
        p.add_argument("--scheme", default="global", help="global, per_format, per_topic or group:<field>")
        p.add_argument("--thresholds", help="thresholds JSON file or saved profile name (default: the model repo's)")
        p.add_argument("--group-by", nargs="*", default=[], help="record fields that have their own cuts in --thresholds")

    p = sub.add_parser("classify", help="assign each document one of the eight formats")
    io(p); llm(p); classify_opts(p)
    p.add_argument("--no-force-fit", action="store_true", help="leave out-of-scope documents without a format")
    p.set_defaults(fn=cmd_classify)

    p = sub.add_parser("extract", help="extract role-labelled outlines")
    io(p); llm(p)
    p.add_argument("--format", help="format for records without their own")
    p.add_argument("--no-few-shot", action="store_true", help="drop the six worked examples from the prompt")
    p.set_defaults(fn=cmd_extract)

    p = sub.add_parser("score", help="score outlines (or documents, for ProseLens)")
    io(p); scoring(p)
    p.add_argument("--input-field", help="field holding the input (default: outline, or text for document models)")
    p.add_argument("--format", help="format for records without their own")
    p.set_defaults(fn=cmd_score)

    p = sub.add_parser("run", help="classify (where needed), extract and score")
    io(p); llm(p); classify_opts(p); scoring(p)
    p.add_argument("--format", help="format for records without their own; skips classification for them")
    p.add_argument("--force-fit", action="store_true", help="map a given format outside the eight to the closest one")
    p.add_argument("--check-format", action="store_true", help="also classify given formats and report disagreement")
    p.add_argument("--no-few-shot", action="store_true")
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser("calibrate", help="fit thresholds on your own human documents and save them")
    p.add_argument("input", help="JSONL: scored records (p_human), outlines, or documents (text)")
    p.add_argument("--save-as", help="save as a named profile, used later with --thresholds NAME")
    p.add_argument("--out", help="also (or instead) write the thresholds JSON here")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--label-field", help="field marking human vs AI; AI rows give a detection-rate report")
    p.add_argument("--human-value", default="human")
    p.add_argument("--scored-out", help="keep the scored records here, for reuse")
    p.add_argument("--format"); p.add_argument("--force-fit", action="store_true")
    p.add_argument("--no-few-shot", action="store_true"); p.add_argument("--chunk", type=int, default=500)
    llm(p); classify_opts(p); scoring(p)
    p.set_defaults(fn=cmd_calibrate, output="/dev/null")

    p = sub.add_parser("cost", help="tokens and cost of a finished classify/extract/run output")
    p.add_argument("input")
    p.add_argument("--provider"); p.add_argument("--llm-model")
    p.set_defaults(fn=cmd_cost)

    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
