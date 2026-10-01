# Extractor and format-gate stochasticity (trial)

42 documents (in-domain test split), 5 independent runs each, production settings (gemini-3.7-flash, 6 exemplars, thinking HIGH). IdeaLens reads each raw outline; fire at the global 1% cut (P(human) <= 0.137).

Documents with all 5 extractions scored: 33 of 42.

| Set | Draw | Condition | documents | same verdict in all 5 runs | pairwise agreement | mean per-document SD of P(AI) | TPR range over runs | FPR range over runs |
|---|---|---|---|---|---|---|---|---|
| in-domain | random | (a) extractor | 33 | 100.0% | 100.0% | 0.003 | 94.4–94.4 | 0.0–0.0 |
| all sets | random | (a) extractor | 33 | 100.0% | 100.0% | 0.003 | | |

**Pooled over all documents** (random and near-cut draws together; not a population estimate).

| Condition | documents | same verdict in all 5 runs | pairwise agreement | mean per-document SD of P(AI) | TPR range over runs | FPR range over runs |
|---|---|---|---|---|---|---|
| (a) extractor only | 33 | 100.0% | 100.0% | 0.003 | 94.4–94.4 | 0.0–0.0 |

**Verdict flips by distance from the cut** (condition a; mean over the five runs of logit P(human), minus logit of the cut; logit bins because probability bins are lopsided around a cut of 0.137).

| logit distance from the cut | documents | any flip |
|---|---|---|
| below -2 | 16 | 0.0% |
| [-2, -0.5) | 1 | 0.0% |
| [+0.5, +2) | 1 | 0.0% |
| above +2 | 15 | 0.0% |

**Format gate.** Same format in all 5 runs: 81.0% of documents; runs placing the document outside the eight formats: 40.0%; runs agreeing with the corpus's recorded (WebOrganizer) format: 38.1%. Most common swaps (recorded -> gate): Knowledge Article -> None (19); News Article -> None (14); User Reviews -> Nonfiction Writing (13); Nonfiction Writing -> None (12); Personal Blog -> None (10); User Reviews -> None (10).

Items per outline: mean coefficient of variation across the five runs 0.100.
