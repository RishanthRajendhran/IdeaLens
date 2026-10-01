### extractor swap: main table

% of predictions that stay the same between the reference extractor's raw outline (gemini-3.7-flash) and the alternate extractor's raw outline, at the global 1% cut.

- 625 documents of the 1M test split (321 AI, 304 human): the reference is the corpus's own gemini-3.7-flash extraction, raw; three alternate extractors (gpt-5.6 sol, terra, luna) re-extracted the same documents (1,874 outlines; one source has only two). One row per alternate outline, paired with its reference by source id. Our outline-trained models on the raw outline, the global calibrated cut on both sides.

| Rows | Label | n | IdeaLens: % unchanged | IdeaLens-ModernBERT-L: % unchanged |
|---|---|---|---|---|
| all | AI + human | 1,874 | 98.8 | 96.0 |
| AI | AI | 963 | 98.3 | 93.0 |
| human | human | 911 | 99.3 | 99.1 |

**Length.** Share under 500 words: 0.0%.

### extractor swap: appendix

**Change directions at the global 1% cut.** Fire rate on the reference extractor's raw outline (gemini-3.7-flash) and the alternate extractor's raw outline, and the share of documents whose prediction changes each way.

| Rows | Model | n | fire, reference | fire, variant | fired -> not | not -> fired | AUC, reference | AUC, variant |
|---|---|---|---|---|---|---|---|---|
| all | IdeaLens | 1,874 | 51.5 | 50.9 | 0.9 | 0.3 | 0.995 | 0.996 |
| all | IdeaLens-ModernBERT-L | 1,874 | 47.5 | 46.5 | 2.5 | 1.5 | 0.988 | 0.992 |
| AI | IdeaLens | 963 | 97.2 | 96.6 | 1.1 | 0.5 |  |  |
| AI | IdeaLens-ModernBERT-L | 963 | 90.3 | 88.8 | 4.3 | 2.7 |  |  |
| human | IdeaLens | 911 | 3.3 | 2.6 | 0.7 | 0.0 |  |  |
| human | IdeaLens-ModernBERT-L | 911 | 2.3 | 1.9 | 0.7 | 0.2 |  |  |

**Other cuts.** % unchanged at 0.1%, 0.5%, 2%, 5% (global).

| Rows | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| all | IdeaLens | 96.2 | 98.0 | 98.6 | 98.6 |
| all | IdeaLens-ModernBERT-L | 93.6 | 94.5 | 97.0 | 97.1 |
| AI | IdeaLens | 93.1 | 96.4 | 98.8 | 99.1 |
| AI | IdeaLens-ModernBERT-L | 87.5 | 90.3 | 96.3 | 97.6 |
| human | IdeaLens | 99.3 | 99.7 | 98.5 | 98.1 |
| human | IdeaLens-ModernBERT-L | 100.0 | 98.9 | 97.8 | 96.6 |

**By extractor.** % unchanged at the 1% cut.

| Extractor | Rows | n | IdeaLens: % unchanged | IdeaLens-ModernBERT-L: % unchanged |
|---|---|---|---|---|
| gpt-5.6-luna | AI | 321 | 98.8 | 93.5 |
| gpt-5.6-sol | AI | 321 | 98.4 | 94.1 |
| gpt-5.6-terra | AI | 321 | 97.8 | 91.6 |
| gpt-5.6-luna | human | 304 | 99.3 | 99.7 |
| gpt-5.6-sol | human | 303 | 99.3 | 98.7 |
| gpt-5.6-terra | human | 304 | 99.3 | 99.0 |

**By format.** % unchanged at the 1% cut.

| Format | Rows | n | IdeaLens: % unchanged | IdeaLens-ModernBERT-L: % unchanged |
|---|---|---|---|---|
| Academic Writing | AI | 114 | 100.0 | 99.1 |
| Creative Writing | AI | 126 | 97.6 | 97.6 |
| Knowledge Article | AI | 114 | 97.4 | 87.7 |
| News Article | AI | 108 | 99.1 | 99.1 |
| Nonfiction Writing | AI | 141 | 97.9 | 81.6 |
| Personal About Page | AI | 102 | 98.0 | 92.2 |
| Personal Blog | AI | 132 | 99.2 | 95.5 |
| User Reviews | AI | 126 | 97.6 | 93.7 |
| Academic Writing | human | 123 | 100.0 | 100.0 |
| Creative Writing | human | 108 | 100.0 | 100.0 |
| Knowledge Article | human | 120 | 96.7 | 97.5 |
| News Article | human | 126 | 98.4 | 97.6 |
| Nonfiction Writing | human | 93 | 100.0 | 98.9 |
| Personal About Page | human | 131 | 100.0 | 99.2 |
| Personal Blog | human | 102 | 100.0 | 100.0 |
| User Reviews | human | 108 | 100.0 | 100.0 |
