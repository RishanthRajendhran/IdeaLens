### source paraphrase: main table

% of predictions that stay the same between the original's raw outline and the paraphrased document's raw outline, at the global 1% cut.

- 832 documents of the 1M test split (432 AI, 400 human), each paraphrased sentence by sentence by three models (sol, terra, luna): 2,494 paraphrased documents, each paired with its original. Our outline-trained models on the raw outline, the global calibrated cut on both sides.
- IdeaLens's human rows are identical across the three paraphrasers (1 fired -> not, 2 not -> fired of 400). Checked: the paraphrases differ in text, outline and score for every source; the shared 400 originals put the same borderline documents across the cut.
- The originals are all 500 words or more; 2.4% of the paraphrased documents are under 500.

| Rows | Label | n | IdeaLens: % unchanged | IdeaLens-ModernBERT-L: % unchanged |
|---|---|---|---|---|
| all | AI + human | 2,494 | 98.6 | 96.6 |
| AI | AI | 1,294 | 97.9 | 94.2 |
| human | human | 1,200 | 99.2 | 99.2 |

**Length.** Share under 500 words: 2.4%.

| Rows · length | Label | n | IdeaLens: % unchanged | IdeaLens-ModernBERT-L: % unchanged |
|---|---|---|---|---|
| all · < 500 | AI + human | 60 | 95.0 | 100.0 |
| all · >= 500 | AI + human | 2,434 | 98.6 | 96.5 |
| AI · < 500 | AI | 20 | 100.0 | 100.0 |
| AI · >= 500 | AI | 1,274 | 97.9 | 94.1 |
| human · < 500 | human | 40 | 92.5 | 100.0 |
| human · >= 500 | human | 1,160 | 99.5 | 99.2 |

### source paraphrase: appendix

**Change directions at the global 1% cut.** Fire rate on the original's raw outline and the paraphrased document's raw outline, and the share of documents whose prediction changes each way.

| Rows | Model | n | fire, reference | fire, variant | fired -> not | not -> fired | AUC, reference | AUC, variant |
|---|---|---|---|---|---|---|---|---|
| all | IdeaLens | 2,494 | 51.8 | 51.8 | 0.7 | 0.8 | 0.995 | 0.995 |
| all | IdeaLens-ModernBERT-L | 2,494 | 48.8 | 48.8 | 1.7 | 1.7 | 0.991 | 0.992 |
| AI | IdeaLens | 1,294 | 97.4 | 97.4 | 1.1 | 1.0 |  |  |
| AI | IdeaLens-ModernBERT-L | 1,294 | 91.4 | 91.7 | 2.8 | 3.0 |  |  |
| human | IdeaLens | 1,200 | 2.5 | 2.8 | 0.2 | 0.5 |  |  |
| human | IdeaLens-ModernBERT-L | 1,200 | 2.8 | 2.5 | 0.5 | 0.2 |  |  |

**Other cuts.** % unchanged at 0.1%, 0.5%, 2%, 5% (global).

| Rows | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| all | IdeaLens | 96.1 | 98.2 | 98.5 | 98.5 |
| all | IdeaLens-ModernBERT-L | 94.6 | 94.5 | 97.7 | 97.8 |
| AI | IdeaLens | 92.6 | 97.0 | 99.0 | 99.4 |
| AI | IdeaLens-ModernBERT-L | 89.8 | 90.2 | 97.4 | 99.3 |
| human | IdeaLens | 99.9 | 99.6 | 97.9 | 97.5 |
| human | IdeaLens-ModernBERT-L | 99.8 | 99.2 | 98.0 | 96.1 |

**By paraphraser.** % unchanged at the 1% cut.

| Paraphraser | Rows | n | IdeaLens: % unchanged | IdeaLens-ModernBERT-L: % unchanged |
|---|---|---|---|---|
| gpt-5.6-luna | AI | 431 | 97.0 | 93.0 |
| gpt-5.6-sol | AI | 432 | 97.9 | 94.4 |
| gpt-5.6-terra | AI | 431 | 98.8 | 95.1 |
| gpt-5.6-luna | human | 400 | 99.2 | 99.0 |
| gpt-5.6-sol | human | 400 | 99.2 | 99.0 |
| gpt-5.6-terra | human | 400 | 99.2 | 99.8 |

**By format.** % unchanged at the 1% cut.

| Format | Rows | n | IdeaLens: % unchanged | IdeaLens-ModernBERT-L: % unchanged |
|---|---|---|---|---|
| Academic Writing | AI | 189 | 99.5 | 97.9 |
| Creative Writing | AI | 140 | 97.1 | 95.7 |
| Knowledge Article | AI | 149 | 98.7 | 87.2 |
| News Article | AI | 147 | 95.2 | 94.6 |
| Nonfiction Writing | AI | 162 | 96.3 | 90.1 |
| Personal About Page | AI | 177 | 97.7 | 93.8 |
| Personal Blog | AI | 165 | 100.0 | 96.4 |
| User Reviews | AI | 165 | 98.2 | 97.0 |
| Academic Writing | human | 126 | 98.4 | 97.6 |
| Creative Writing | human | 171 | 98.2 | 98.2 |
| Knowledge Article | human | 162 | 100.0 | 100.0 |
| News Article | human | 165 | 98.2 | 99.4 |
| Nonfiction Writing | human | 150 | 100.0 | 99.3 |
| Personal About Page | human | 132 | 99.2 | 99.2 |
| Personal Blog | human | 147 | 100.0 | 100.0 |
| User Reviews | human | 147 | 100.0 | 100.0 |
