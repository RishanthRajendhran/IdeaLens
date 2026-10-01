# Document similarity between clean AI documents and their attacked versions, and IdeaLens detection

Cosine of text-embedding-3-large document embeddings. Same-topic reference: a different author's document on the same prompt or source (DetectionAI: another generator, mean 0.769, 95th pct 0.901; DetectRL-X: the human document of the same pair, mean 0.828, 95th pct 0.942). 'caught' and 'missed' split attacked documents whose clean original IdeaLens caught.

| Set | Attack | pairs | doc cosine (mean) | below the reference's 95th pct | IdeaLens TPR clean | attacked | cosine, still caught | cosine, missed | Spearman(cosine, P(AI)) |
|---|---|---|---|---|---|---|---|---|---|
| DetectionAI | StealthGPT humanizer | 7,705 | 0.873 | 68.2% | 90.3 | 57.8 | 0.879 (n 4369) | 0.862 (n 2587) | +0.10 |
| DetectRL-X | seq2seq paraphrasing | 550 | 0.914 | 34.2% | 82.9 | 60.7 | 0.979 (n 319) | 0.768 (n 137) | +0.57 |
| DetectRL-X | backtranslation | 550 | 0.945 | 24.0% | 82.9 | 81.5 | 0.955 (n 430) | 0.808 (n 26) | +0.10 |
| DetectRL-X | decoder paraphrasing | 550 | 0.946 | 32.4% | 82.9 | 58.4 | 0.993 (n 304) | 0.853 (n 152) | +0.60 |
| DetectRL-X | encoder paraphrasing | 550 | 0.982 | 10.5% | 82.9 | 83.1 | 0.984 (n 428) | 0.972 (n 28) | +0.06 |
| DetectRL-X | expanding | 550 | 0.982 | 10.4% | 82.9 | 88.5 | 0.982 (n 440) | 0.994 (n 16) | -0.17 |
| DetectRL-X | character substitution | 550 | 0.988 | 2.9% | 82.9 | 83.3 | 0.989 (n 428) | 0.983 (n 28) | +0.09 |
| DetectRL-X | condensing | 550 | 0.990 | 1.5% | 82.9 | 83.6 | 0.991 (n 437) | 0.982 (n 19) | +0.09 |
| DetectRL-X | character deletion | 550 | 0.992 | 1.1% | 82.9 | 83.6 | 0.992 (n 436) | 0.991 (n 20) | +0.08 |
| DetectRL-X | polishing | 549 | 0.992 | 1.1% | 82.9 | 84.7 | 0.992 (n 435) | 0.985 (n 20) | +0.06 |
| DetectRL-X | character insertion | 550 | 0.992 | 0.4% | 82.9 | 84.5 | 0.993 (n 439) | 0.988 (n 17) | +0.05 |
| DetectRL-X | zero width insertion | 550 | 0.993 | 0.0% | 82.9 | 83.5 | 0.994 (n 434) | 0.992 (n 22) | +0.07 |

All 13,754 pairs: Spearman(doc cosine, IdeaLens P(AI)) = +0.298; cosine 0.933 when still caught vs 0.864 when missed.
