# Glossary

Terms that carry a specific meaning in this project, where the everyday reading
would be misleading.

**Idea-level / conceptual authorship.** Attributing a document to whoever
conceived it rather than whoever rendered its sentences. The task this project
defines; not a synonym for AI-text detection.

**The labelling rule.** Human ideas make a document human, however much of its
surface a model wrote. Everything about how sets are labelled follows from it.

**Outline.** The role-labelled decomposition of a document into atomic ideas.
What the classifier sees instead of prose. Three parts, of which only `items`
reaches the classifier.

**Item.** One atomic idea, with a role label and one sentence of content. The
unit of the item-level arms and of item-level feature discovery.

**Role.** An item's rhetorical function, drawn from a per-format vocabulary of
roughly 40-60 names discovered separately for each format. Assigned by the
extractor — which is why extractor sensitivity is load-bearing.

**Stage 1 / extraction.** Document to outline. Format-conditioned, few-shot.

**Stage 2 / de-leak.** Outline to outline, re-expressed by a model that sees only
the outline and never the source. Strips the source's wording, which is what
leaks authorship into an outline.

**Lifting.** The share of outline text sitting in verbatim runs copied from the
source. The mechanism behind outline leakage, and the quantity a better
extraction prompt should reduce.

**Untreated / raw outline.** Stage-1 output that has not been de-leaked. Scores
from it are an upper bound and not comparable with de-leaked scores. Flagged as
`deleak_status: not_run`.

**Setting / arm input.** Which rendering a trained model consumes: `full`,
`items`, `roles`, `docs`, `rawout`. Must match what the checkpoint was trained on.

**The counterfactual.** An arm trained on the same corpus with the same recipe
but reading raw documents. Present so the central claim is falsifiable: if it
tracks prose where the outline arms track ideas, the representation is doing the
work.

**Fires.** The detector calls a document AI. It fires *below* the threshold,
because the score is P(human).

**Deployed threshold.** One cut per model, fitted on the human-only calibration
split and carried onto every eval unchanged. The primary convention.

**In-set threshold.** The cut re-derived from an eval's own humans. Secondary,
out-of-domain only, always reported beside the deployed number and labelled.

**Realised FPR.** The false-positive rate a cut actually produces on the set
being reported, as against the nominal target it was fitted for. Printed beside
every TPR because out of domain the two come apart.

**Estimable.** A target FPR is estimable when `q x n_humans >= 25`. Below that a
cut rests on too few documents to report.

**Fire rate.** The share of documents flagged, with no labels involved. The right
reading for a set where every row carries the same true label.

**Rung / ladder.** A sequence of arms varying how much of the idea came from the
model while holding prose constant. Read as a shape, not a level.

**Quadrant.** The 2x2 of ideas {human, AI} x prose {human, AI}. The
human-ideas/AI-prose and AI-ideas/human-prose cells are where surface detection
and idea attribution come apart, and the second is the scarce one.

**Saha levels.** An external five-level taxonomy of AI assistance (AI-BP, AI-EP,
AI-HI, H-AI, H) that our conditions are mapped onto, so results are comparable
with published rows.

**Format.** A WebOrganizer category. Nine of their 24 map onto a role vocabulary
we possess; the rest are out of scope and filtered.

**Contrast set.** A balanced, role-matched pair of example sets handed to a model
for feature discovery.

**Corpus labels vs model labels.** Two feature-discovery label sources answering
different questions: what distinguishes the classes, versus what our current
detectors key on. Their outputs are never merged.
