"""Idea-level authorship detection.

The detector attributes a document to whoever conceived it, not to whoever wrote
its sentences. It does this by construction: the classifier never sees prose,
only a role-labelled outline that has been paraphrased to strip the source's
wording.

    document -> format classification -> role-labelled outline
             -> de-leak paraphrase -> binary classifier

The labelling rule that follows from that framing: **a document with human ideas
and AI prose is human**, however much of its surface an AI produced.

Start at `README.md`; `docs/CONVENTIONS.md` lists the rules that must not drift.
"""
__version__ = "0.1.0"

from . import calibration, config, formats, io, metrics, outlines, paths, prompts, registry, report, schema  # noqa: F401
