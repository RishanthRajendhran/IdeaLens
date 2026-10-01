"""Document formats: WebOrganizer's 24-label taxonomy, the eight formats the detectors were trained on, and how a
user-supplied format is resolved.

A format does two jobs. Outline extraction needs it to pick the role vocabulary and worked examples, and per-format
thresholds are indexed by it. A value we cannot resolve is rejected rather than guessed, because an outline extracted
with the wrong format's vocabulary looks fine and scores wrong.
"""
from __future__ import annotations

from dataclasses import dataclass

#: The eight formats in the training corpus, canonical display names.
FORMATS = (
    "Academic Writing",
    "Creative Writing",
    "Knowledge Article",
    "News Article",
    "Nonfiction Writing",
    "Personal About Page",
    "Personal Blog",
    "User Reviews",
)

#: WebOrganizer's format taxonomy, as the LLM classifier prompt lists it.
WEBORGANIZER_LABELS = (
    "Academic Writing", "Content Listing", "Creative Writing", "Customer Support Page",
    "Discussion Forum / Comment Section", "FAQs", "Incomplete Content", "Knowledge Article", "Legal Notices",
    "Listicle", "News Article", "Nonfiction Writing", "Organizational About Page", "Organizational Announcement",
    "Personal About Page", "Personal Blog", "Product Page", "Q&A Forum", "Spam / Ads", "Structured Data",
    "Technical Writing", "Transcript / Interview", "Tutorial / How-To Guide", "User Reviews",
)

#: WebOrganizer label spellings (classifier model and LLM prompt) -> our display name. Labels not listed here are
#: outside the eight. Transcript / Interview has a role vocabulary but was left out of training, so it is out of scope.
WEBORGANIZER_TO_FORMAT = {
    "Academic Writing": "Academic Writing",
    "Creative Writing": "Creative Writing",
    "Knowledge Article": "Knowledge Article",
    "News Article": "News Article",
    "Nonfiction Writing": "Nonfiction Writing",
    "About (Pers.)": "Personal About Page",
    "Personal About Page": "Personal About Page",
    "Personal Blog": "Personal Blog",
    "User Review": "User Reviews",
    "User Reviews": "User Reviews",
}


def slug(name: str) -> str:
    """'Personal About Page' -> 'personal_about_page'; 'Transcript / Interview' -> 'transcript_interview'."""
    return (str(name).strip().lower().replace(" / ", "_").replace("/", "_")
            .replace(" ", "_").replace("-", "_"))


_BY_SLUG = {slug(f): f for f in FORMATS}
_OUT_OF_SCOPE = {slug(l): l for l in WEBORGANIZER_LABELS if l not in WEBORGANIZER_TO_FORMAT}
_OUT_OF_SCOPE.update({slug("Audio Transcript"): "Audio Transcript"})


class FormatError(ValueError):
    """A format value that is not one of the eight and not a known out-of-scope label."""


class OutOfScopeFormat(FormatError):
    """A known format label outside the eight (e.g. 'Product Page'). Force-fitting maps it to the closest of the
    eight; without force-fitting the document cannot be scored by an outline model."""

    def __init__(self, label: str):
        self.label = label
        super().__init__(f"format {label!r} is outside the eight the detectors were trained on "
                         f"({', '.join(FORMATS)}). Pass force_fit=True (CLI: --force-fit) to assign the closest of "
                         f"the eight, or give one of them explicitly.")


@dataclass(frozen=True)
class FormatAssignment:
    """The format a document is scored under, and how it was chosen.

    method: "user" (given by the caller), "llm" or "weborganizer" (classified).
    forced: True when the document's own label was outside the eight and it was assigned the closest of them.
    original: the label before force-fitting (or before mapping, for a user-given WebOrganizer spelling).
    probabilities: the classifier's label probabilities, when the method provides them.
    """
    format: str | None                # None: out of scope and not force-fitted, or classification failed
    method: str
    forced: bool = False
    original: str | None = None
    probabilities: dict | None = None
    error: str | None = None
    meta: dict | None = None          # classifier provenance: model, prompt version, usage, raw reply

    def to_dict(self) -> dict:
        d = {"format": self.format, "format_method": self.method, "forced_format": self.forced,
             "original_format": self.original}
        if self.probabilities is not None:
            d["format_probabilities"] = self.probabilities
        if self.error:
            d["format_error"] = self.error
        if self.meta:
            d["format_meta"] = self.meta
        return d


def resolve(value: str) -> str:
    """Resolve a format spelling to one of the eight display names.

    Accepts a display name, a slug, or a WebOrganizer label that maps to one of the eight, case-insensitively.
    Raises OutOfScopeFormat for a known label outside the eight, and FormatError for anything else.
    """
    v = str(value).strip()
    if v in FORMATS:
        return v
    if v in WEBORGANIZER_TO_FORMAT:
        return WEBORGANIZER_TO_FORMAT[v]
    s = slug(v)
    if s in _BY_SLUG:
        return _BY_SLUG[s]
    for label, fmt in WEBORGANIZER_TO_FORMAT.items():
        if slug(label) == s:
            return fmt
    if s in _OUT_OF_SCOPE:
        raise OutOfScopeFormat(_OUT_OF_SCOPE[s])
    raise FormatError(f"unknown format {value!r}. Use one of: {', '.join(FORMATS)} "
                      f"(slugs such as 'news_article' and WebOrganizer labels are also accepted).")


def user_format(value: str) -> FormatAssignment:
    """A caller-supplied format, validated. Out-of-scope labels raise OutOfScopeFormat; force-fitting them needs a
    classifier and happens in idealens.classify."""
    fmt = resolve(value)
    return FormatAssignment(format=fmt, method="user", original=None if str(value).strip() == fmt else str(value))
