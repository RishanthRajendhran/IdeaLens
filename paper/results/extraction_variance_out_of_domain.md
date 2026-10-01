# Extractor and format-gate stochasticity (ood)

400 documents (DetectRL-X, MELD, Saha), 5 independent runs each, production settings (gemini-3.7-flash, 6 exemplars, thinking HIGH). IdeaLens reads each raw outline; fire at the global 1% cut (P(human) <= 0.137).

Documents with all 5 extractions scored: 400 of 400.

| Set | Draw | Condition | documents | same verdict in all 5 runs | pairwise agreement | mean per-document SD of P(AI) | TPR range over runs | FPR range over runs |
|---|---|---|---|---|---|---|---|---|
| DetectRL-X | near | (a) extractor | 60 | 65.0% | 84.0% | 0.100 | 75.0–86.4 | 18.8–25.0 |
| DetectRL-X | random | (a) extractor | 60 | 91.7% | 95.7% | 0.037 | 86.7–100.0 | 0.0–0.0 |
| MELD | near | (a) extractor | 80 | 32.5% | 65.8% | 0.118 | 52.7–68.9 | 0.0–66.7 |
| MELD | random | (a) extractor | 80 | 93.8% | 97.3% | 0.018 | 82.5–92.5 | 0.0–0.0 |
| Saha | near | (a) extractor | 60 | 66.7% | 83.7% | 0.064 | 84.7–91.5 | 0.0–0.0 |
| Saha | random | (a) extractor | 60 | 96.7% | 98.3% | 0.007 | 96.7–100.0 | 0.0–0.0 |
| all sets | random | (a) extractor | 200 | 94.0% | 97.1% | 0.021 | | |
| all sets | near | (a) extractor | 200 | 52.5% | 76.6% | 0.096 | | |

**Pooled over all documents** (random and near-cut draws together; not a population estimate).

| Condition | documents | same verdict in all 5 runs | pairwise agreement | mean per-document SD of P(AI) | TPR range over runs | FPR range over runs |
|---|---|---|---|---|---|---|
| (a) extractor only | 400 | 73.2% | 86.8% | 0.058 | 79.4–83.8 | 3.3–5.7 |

**Verdict flips by distance from the cut** (condition a; mean over the five runs of logit P(human), minus logit of the cut; logit bins because probability bins are lopsided around a cut of 0.137).

| logit distance from the cut | documents | any flip |
|---|---|---|
| below -2 | 133 | 3.0% |
| [-2, -0.5) | 94 | 57.4% |
| [-0.5, +0.5) | 29 | 100.0% |
| [+0.5, +2) | 23 | 78.3% |
| above +2 | 121 | 1.7% |

**Format gate.** Same format in all 5 runs: 93.2% of documents; runs placing the document outside the eight formats: 9.6%; runs agreeing with the corpus's recorded (WebOrganizer) format: 85.0%. Most common swaps (recorded -> gate): Knowledge Article -> None (120); Creative Writing -> Nonfiction Writing (53); Academic Writing -> User Reviews (35); Personal Blog -> None (29); Nonfiction Writing -> None (20); Creative Writing -> None (16).

Items per outline: mean coefficient of variation across the five runs 0.087.
