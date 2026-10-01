# TwiceTold

50 stories written by people from the outline of a model's story (gpt-5.6-sol), and the 50 model stories they were written
from. Both sets have model ideas, so every flag is a correct detection. Flagged as AI (%), 1% global cut; Pangram 4 at its
own threshold. At the Creative Writing per-format cut IdeaLens flags 80.0% of the rewrites.

| Detector | Human rewrites | Model originals |
|---|---|---|
| IdeaLens (outline) | 68.0 (34/50) | 96.0 (48/50) |
| IdeaLens (document) | 6.0 (3/50) | 100.0 (50/50) |
| ProseLens | 0.0 (0/50) | 100.0 (50/50) |
| EditLens-3B | 0.0 (0/50) | 90.0 (45/50) |
| Pangram 4 | 8.0 (4/50) | 100.0 (50/50) |

Spearman correlation of P(AI) with story length and with unigram Jaccard overlap between rewrite and original.

| Author | IdeaLens, length | IdeaLens, Jaccard | ProseLens, length | ProseLens, Jaccard |
|---|---|---|---|---|
| Human | 0.07 | -0.52 | 0.60 | -0.65 |
| GPT 5.6 Sol | -0.11 | -0.28 | -0.18 | -0.02 |
