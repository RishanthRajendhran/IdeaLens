### Pangram 4 probe: does the paraphrase preserve meaning?

1000 held-out test documents (500 human-labelled, 500 AI-labelled), each with its raw outline and its paraphrased outline. text-embedding-3-large; cosine of L2-normalised embeddings; mean (median). Chance references use up to 20 other documents of the same label and format. Item i of the raw outline and item i of the paraphrased outline are the same item.

| measure | all | human-labelled | AI-labelled |
|---|---|---|---|
| raw outline vs its paraphrased outline (cosine) | 0.933 (0.938) | 0.934 (0.937) | 0.933 (0.939) |
|   chance: raw outline vs another document's paraphrased outline (same label, format) | 0.389 (0.392) | 0.360 (0.363) | 0.418 (0.421) |
| item i raw vs item i paraphrased (mean cosine) | 0.834 (0.837) | 0.845 (0.851) | 0.822 (0.826) |
|   chance: item i raw vs the other paraphrased items of the same outline | 0.436 (0.436) | 0.418 (0.420) | 0.453 (0.452) |
| share of raw items whose closest paraphrased item is their own | 99.2 (100.0) | 99.6 (100.0) | 98.8 (100.0) |
| share of items keeping their role label | 100.0 (100.0) | 100.0 (100.0) | 100.0 (100.0) |
| document vs raw outline (cosine) | 0.794 (0.804) | 0.790 (0.802) | 0.798 (0.806) |
| document vs paraphrased outline (cosine) | 0.758 (0.765) | 0.754 (0.761) | 0.762 (0.770) |
|   chance: document vs another document's raw outline | 0.262 (0.261) | 0.239 (0.242) | 0.285 (0.288) |
|   chance: document vs another document's paraphrased outline | 0.262 (0.261) | 0.239 (0.243) | 0.285 (0.289) |
| raw outline 3-grams found in the document (%) | 12.3 (11.0) | 10.3 (9.2) | 14.2 (13.1) |
| paraphrased outline 3-grams found in the document (%) | 3.5 (2.8) | 3.6 (3.0) | 3.3 (2.7) |
| raw outline 5-grams found in the document (%) | 3.6 (2.6) | 3.0 (2.1) | 4.3 (3.3) |
| paraphrased outline 5-grams found in the document (%) | 0.8 (0.3) | 0.9 (0.3) | 0.8 (0.3) |
| raw outline 8-grams found in the document (%) | 0.9 (0.2) | 0.8 (0.2) | 1.1 (0.4) |
| paraphrased outline 8-grams found in the document (%) | 0.3 (0.0) | 0.3 (0.0) | 0.3 (0.0) |

**By format** (mean cosine: raw vs paraphrased, chance; document vs raw, document vs paraphrased; 5-gram share of raw / paraphrased in the document)

| format | n | raw vs para | chance | doc vs raw | doc vs para | raw 5-grams in doc | para 5-grams in doc |
|---|---|---|---|---|---|---|---|
| Academic Writing | 126 | 0.926 | 0.378 | 0.810 | 0.771 | 3.0 | 0.6 |
| Creative Writing | 126 | 0.941 | 0.452 | 0.748 | 0.720 | 2.0 | 0.7 |
| Knowledge Article | 125 | 0.934 | 0.316 | 0.798 | 0.763 | 3.5 | 0.6 |
| News Article | 120 | 0.942 | 0.299 | 0.846 | 0.812 | 6.6 | 2.1 |
| Nonfiction Writing | 126 | 0.934 | 0.369 | 0.810 | 0.769 | 2.9 | 0.7 |
| Personal About Page | 125 | 0.937 | 0.453 | 0.751 | 0.734 | 5.2 | 1.1 |
| Personal Blog | 125 | 0.920 | 0.393 | 0.790 | 0.731 | 2.7 | 0.5 |
| User Reviews | 127 | 0.934 | 0.447 | 0.801 | 0.764 | 3.5 | 0.6 |
