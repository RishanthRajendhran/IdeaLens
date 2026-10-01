"""Document formats: the WebOrganizer taxonomy, our subset, and slug conventions.

The extraction prompt is format-conditioned — it carries that format's role
vocabulary and its few-shot exemplars — so nothing can be extracted before a
format is assigned. Running one format's prompt over another's documents
silently extracts with the wrong role vocabulary and produces outlines that look
fine and score wrong.

**Never assert a format for a new corpus.** Run the classifier
(`scripts/pipeline/classify_format.py`) even when the corpus "obviously" is all
peer reviews or all short fiction. Several published caveats in this project
trace to an asserted format.
"""
from __future__ import annotations

#: The eight formats the detector is trained on, canonical display names.
#: Transcript / Interview is deliberately absent: it had 2,439 training rows at
#: 94.3% human and zero test rows, so a model could learn "reads like a
#: transcript -> human" with no eval able to catch it, and the source pool is
#: exhausted so it cannot be rebalanced.
TRAIN_FORMATS = (
    "Academic Writing",
    "Creative Writing",
    "Knowledge Article",
    "News Article",
    "Nonfiction Writing",
    "Personal About Page",
    "Personal Blog",
    "User Reviews",
)

#: Formats with a role vocabulary on disk but excluded from training.
EXTRA_FORMATS = ("Transcript / Interview",)

ALL_FORMATS = TRAIN_FORMATS + EXTRA_FORMATS

#: WebOrganizer's own label -> our display name. WebOrganizer has 24 format
#: categories; only these nine map onto a role vocabulary we possess. Documents
#: in the other fifteen are DROPPED rather than forced into a nearby label.
WEBORGANIZER_TO_FORMAT = {
    "Academic Writing": "Academic Writing",
    "Creative Writing": "Creative Writing",
    "Knowledge Article": "Knowledge Article",
    "News Article": "News Article",
    "Nonfiction Writing": "Nonfiction Writing",
    "About (Pers.)": "Personal About Page",
    "Personal About Page": "Personal About Page",   # LLM classifier phrasing
    "Personal Blog": "Personal Blog",
    "Audio Transcript": "Transcript / Interview",
    "User Review": "User Reviews",
    "User Reviews": "User Reviews",                  # LLM classifier phrasing
}

#: One-line descriptions injected into the extraction prompt as {{FORMAT_DESCRIPTION}}.
FORMAT_DESCRIPTIONS = {
    "Academic Writing": "scholarly or research writing: papers, reviews, theses, technical reports",
    "Creative Writing": "fiction, poetry, scripts, and other imaginative prose",
    "Knowledge Article": "encyclopaedic or reference writing that explains a topic neutrally",
    "News Article": "journalistic reporting of events, written for a general readership",
    "Nonfiction Writing": "essays, opinion, analysis and long-form nonfiction argument",
    "Personal About Page": "a first-person page introducing a person, their work and background",
    "Personal Blog": "an individual's blog post, personal in voice and often anecdotal",
    "Transcript / Interview": "a transcribed conversation, interview or spoken exchange",
    "User Reviews": "first-person reviews of products, places, media or services",
}


def slug(fmt: str) -> str:
    """Display name -> the filesystem/config slug, e.g. 'Transcript / Interview'
    -> 'transcript_interview'. Stable: role vocabularies and prompt files are
    named by it."""
    return (fmt.lower().replace(" / ", "_").replace("/", "_")
            .replace(" ", "_").replace("-", "_"))


#: slug -> display name, the inverse of `slug`.
FROM_SLUG = {slug(f): f for f in ALL_FORMATS}


def canonical(name: str) -> str:
    """Best-effort normalisation of any format spelling we might be handed.

    Accepts a display name, a slug, or a WebOrganizer label. Raises rather than
    guessing, because a silently wrong format is the most expensive mistake in
    the pipeline.
    """
    if name in ALL_FORMATS:
        return name
    if name in FROM_SLUG:
        return FROM_SLUG[name]
    if name in WEBORGANIZER_TO_FORMAT:
        return WEBORGANIZER_TO_FORMAT[name]
    s = slug(str(name))
    if s in FROM_SLUG:
        return FROM_SLUG[s]
    raise KeyError(
        f"unknown format {name!r}. Known: {sorted(ALL_FORMATS)}. "
        f"If this is a WebOrganizer label outside our nine, the document is out "
        f"of scope and should be filtered, not remapped.")


def is_trainable(fmt: str) -> bool:
    return canonical(fmt) in TRAIN_FORMATS
