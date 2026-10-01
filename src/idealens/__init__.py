"""idealens: detect whether a document's ideas came from a person or an AI model.

Pipeline: format -> outline -> score.

    import idealens as il
    fmts = il.classify(texts)                              # or give formats yourself
    outlines = il.extract(texts, fmts)                     # gemini-3.7-flash, six worked examples
    with il.Detector("IdeaLens") as det:                   # vLLM; the repo's published thresholds
        records = det.score_outlines(outlines, format=fmts)
    # or all at once: il.run(texts, det, formats=None)
"""
from .classify import classify, force_fit
from .detector import Detector
from .extract import extract
from .pipeline import run
from .cost import estimate as estimate_cost
from .calibrate import calibrate
from .formats import FORMATS, FormatAssignment, FormatError, OutOfScopeFormat
from .outline import Outline
from .registry import MODELS, DEFAULT_MODEL
from .thresholds import Thresholds

__version__ = "0.1.1"
__all__ = ["calibrate", "estimate_cost", "classify", "force_fit", "extract", "run", "Detector", "Outline", "Thresholds", "FORMATS", "FormatAssignment", "FormatError", "OutOfScopeFormat",
           "MODELS", "DEFAULT_MODEL"]
