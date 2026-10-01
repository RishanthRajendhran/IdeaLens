# Content preserved by humanizers and adversarial attacks, and IdeaLens detection

Pairs: every attacked document with its clean AI original (same pair id and generator). Embeddings: text-embedding-3-large. An original item is **kept** when its best match among the attacked outline's items reaches tau = 0.766, the 95th percentile of best-match cosines against a different author's document on the same prompt or source (84,973 items). IdeaLens fires at the global 1% cut on the raw outline. Cells are means; 'kept, missed' and 'kept, caught' split the attacked documents that the clean original was caught on by whether IdeaLens still catches the attacked version.

| Set | Attack | pairs | doc cosine | items kept | items traceable | items attacked / clean | IdeaLens TPR clean | IdeaLens TPR attacked | kept, caught | kept, missed | Spearman(kept, P(AI)) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DetectionAI | StealthGPT humanizer | 7,705 | 0.873 | 0.430 | 0.563 | 0.80 | 90.3 | 57.8 | 0.440 (n 4369) | 0.373 (n 2587) | +0.10 |
| DetectRL-X | seq2seq paraphrasing | 550 | 0.914 | 0.620 | 0.609 | 1.12 | 82.9 | 60.7 | 0.807 (n 319) | 0.208 (n 137) | +0.64 |
| DetectRL-X | decoder paraphrasing | 550 | 0.946 | 0.657 | 0.664 | 1.00 | 82.9 | 58.4 | 0.840 (n 304) | 0.335 (n 152) | +0.63 |
| DetectRL-X | backtranslation | 550 | 0.945 | 0.773 | 0.769 | 1.02 | 82.9 | 81.5 | 0.784 (n 430) | 0.615 (n 26) | +0.11 |
| DetectRL-X | expanding | 550 | 0.982 | 0.782 | 0.741 | 1.11 | 82.9 | 88.5 | 0.786 (n 440) | 0.798 (n 16) | -0.02 |
| DetectRL-X | condensing | 550 | 0.990 | 0.793 | 0.801 | 1.00 | 82.9 | 83.6 | 0.801 (n 437) | 0.777 (n 19) | +0.15 |
| DetectRL-X | encoder paraphrasing | 550 | 0.982 | 0.825 | 0.822 | 1.02 | 82.9 | 83.1 | 0.837 (n 428) | 0.810 (n 28) | +0.10 |
| DetectRL-X | polishing | 549 | 0.992 | 0.830 | 0.818 | 1.03 | 82.9 | 84.7 | 0.841 (n 435) | 0.819 (n 20) | +0.13 |
| DetectRL-X | character substitution | 550 | 0.988 | 0.831 | 0.826 | 1.02 | 82.9 | 83.3 | 0.844 (n 428) | 0.840 (n 28) | +0.16 |
| DetectRL-X | character insertion | 550 | 0.992 | 0.835 | 0.833 | 1.02 | 82.9 | 84.5 | 0.846 (n 439) | 0.823 (n 17) | +0.10 |
| DetectRL-X | character deletion | 550 | 0.992 | 0.842 | 0.841 | 1.02 | 82.9 | 83.6 | 0.854 (n 436) | 0.793 (n 20) | +0.13 |
| DetectRL-X | zero width insertion | 550 | 0.993 | 0.844 | 0.836 | 1.03 | 82.9 | 83.5 | 0.854 (n 434) | 0.780 (n 22) | +0.09 |

Across all 13,754 pairs: Spearman(items kept, IdeaLens P(AI) of the attacked document) = +0.274; among pairs whose clean original IdeaLens caught, items kept 0.637 when the attacked version is still caught against 0.390 when it is missed.
