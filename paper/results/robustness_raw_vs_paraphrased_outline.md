### paraphrase invariance: main table

% of predictions that stay the same between the raw outline and the paraphrased outline, at the global 1% cut.

- 10,000 documents of the 1M test split (4,993 AI, 5,007 human), each scored by the same model on the raw outline (straight from the extractor) and on the paraphrased outline (the corpus's own). Our outline-trained models only; global calibrated cut for each input.
- IdeaLens-ModernBERT-L: both columns from the deployed checkpoint.
- Every document is 500 words or more.

| Rows | Label | n | IdeaLens: % unchanged | IdeaLens-ModernBERT-L: % unchanged |
|---|---|---|---|---|
| all | AI + human | 10,000 | 98.6 | 96.7 |
| AI | AI | 4,993 | 97.9 | 94.0 |
| human | human | 5,007 | 99.2 | 99.4 |

**Length.** Share under 500 words: 0.0%.

### paraphrase invariance: appendix

**Change directions at the global 1% cut.** Fire rate on the raw outline and the paraphrased outline, and the share of documents whose prediction changes each way.

| Rows | Model | n | fire, reference | fire, variant | fired -> not | not -> fired | AUC, reference | AUC, variant |
|---|---|---|---|---|---|---|---|---|
| all | IdeaLens | 10,000 | 49.9 | 49.0 | 1.2 | 0.3 | 0.995 | 0.995 |
| all | IdeaLens-ModernBERT-L | 10,000 | 46.1 | 44.1 | 2.7 | 0.7 |  |  |
| AI | IdeaLens | 4,993 | 97.1 | 95.6 | 1.8 | 0.3 |  |  |
| AI | IdeaLens-ModernBERT-L | 4,993 | 89.9 | 86.3 | 4.8 | 1.2 |  |  |
| human | IdeaLens | 5,007 | 2.8 | 2.5 | 0.5 | 0.3 |  |  |
| human | IdeaLens-ModernBERT-L | 5,007 | 2.5 | 2.1 | 0.5 | 0.1 |  |  |

**Other cuts.** % unchanged at 0.1%, 0.5%, 2%, 5% (global).

| Rows | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| all | IdeaLens | 96.4 | 98.2 | 99.1 | 98.8 |
| all | IdeaLens-ModernBERT-L | 95.7 | 95.9 | 97.6 | 97.9 |
| AI | IdeaLens | 93.2 | 97.1 | 99.0 | 99.5 |
| AI | IdeaLens-ModernBERT-L | 91.6 | 92.4 | 96.4 | 98.8 |
| human | IdeaLens | 99.6 | 99.4 | 99.3 | 98.2 |
| human | IdeaLens-ModernBERT-L | 99.9 | 99.5 | 98.8 | 96.9 |

**By format.** % unchanged at the 1% cut.

| Format | Rows | n | IdeaLens: % unchanged | IdeaLens-ModernBERT-L: % unchanged |
|---|---|---|---|---|
| Academic Writing | AI | 634 | 99.1 | 96.4 |
| Creative Writing | AI | 625 | 97.9 | 93.4 |
| Knowledge Article | AI | 654 | 96.2 | 91.0 |
| News Article | AI | 589 | 98.1 | 94.9 |
| Nonfiction Writing | AI | 601 | 96.8 | 93.2 |
| Personal About Page | AI | 621 | 97.6 | 92.4 |
| Personal Blog | AI | 643 | 98.4 | 94.4 |
| User Reviews | AI | 626 | 99.0 | 96.0 |
| Academic Writing | human | 618 | 99.5 | 99.7 |
| Creative Writing | human | 627 | 99.7 | 99.2 |
| Knowledge Article | human | 598 | 98.0 | 99.2 |
| News Article | human | 663 | 99.5 | 99.4 |
| Nonfiction Writing | human | 647 | 98.6 | 98.9 |
| Personal About Page | human | 627 | 99.2 | 100.0 |
| Personal Blog | human | 605 | 99.5 | 99.2 |
| User Reviews | human | 622 | 99.5 | 99.7 |
