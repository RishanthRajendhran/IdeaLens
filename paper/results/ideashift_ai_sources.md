### IdeaShift, AI sources: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- 263 AI sources from the 1M test split, rewritten at the same six levels as IdeaShift's human sources (sol 131, terra 67, luna 65; the generator is held constant within a source).
- Every row is clear AI (TPR): on an AI source every level's ideas are a model's, the source's or the generator's own. There is no human row; the human sources (ideashift_human_sources.md) are the comparison.
- Level 5 is the 2026-09-14 regeneration, sent with its system prompt (realise every item, add nothing); the first generation had been sent without it and added items (median 1.29x the source's).
- Sources: Pangram 4 is shown for the IdeaShift figure, but it is circular there (the sources' silver labels are Pangram 3.3.2 verdicts), so its source rate is agreement with its own labels, not accuracy. IdeaLens on the document covers 263 of 263 sources.

| Arm | Label | n | IdeaLens · outline (paraphrased) | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline (paraphrased) | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| source (a model's document) | clear AI (TPR) | 263 | 98.1 | 98.5 | 100.0 | 92.4 | 94.3 | 99.2 | 77.2 | 53.6 | 73.4 |
| level 0 (type line) | clear AI (TPR) | 263 | 98.1 | 99.6 | 100.0 | 84.4 | 96.2 | 100.0 | 74.9 | 0.0 | 100.0 |
| level 1 (topic line) | clear AI (TPR) | 263 | 98.5 | 100.0 | 100.0 | 89.0 | 96.6 | 100.0 | 72.6 | 0.0 | 100.0 |
| level 2 (themes) | clear AI (TPR) | 263 | 99.2 | 100.0 | 100.0 | 88.2 | 96.2 | 100.0 | 75.7 | 0.0 | 100.0 |
| level 3 (themes and structure) | clear AI (TPR) | 263 | 96.6 | 100.0 | 100.0 | 89.4 | 97.7 | 100.0 | 75.7 | 0.0 | 100.0 |
| level 4 (themes and full outline) | clear AI (TPR) | 263 | 98.9 | 100.0 | 100.0 | 93.9 | 97.7 | 100.0 | 78.3 | 0.0 | 100.0 |
| level 5 (the source's outline) | clear AI (TPR) | 263 | 98.5 | 100.0 | 100.0 | 93.5 | 97.3 | 100.0 | 79.8 | 0.0 | 99.2 |

**Length.** Share under 500 words: source (a model's document) 0.0%, level 0 (type line) 0.8%, level 1 (topic line) 0.4%, level 2 (themes) 0.0%, level 3 (themes and structure) 0.0%, level 4 (themes and full outline) 1.1%, level 5 (the source's outline) 4.6%.

| Arm · length | Label | n | IdeaLens · outline (paraphrased) | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline (paraphrased) | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| source (a model's document) · >= 500 | clear AI (TPR) | 263 | 98.1 | 98.5 | 100.0 | 92.4 | 94.3 | 99.2 | 77.2 | 53.6 | 73.4 |
| level 0 (type line) · < 500 | clear AI (TPR) | 2 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 100.0 |
| level 0 (type line) · >= 500 | clear AI (TPR) | 261 | 98.1 | 99.6 | 100.0 | 84.3 | 96.2 | 100.0 | 74.7 | 0.0 | 100.0 |
| level 1 (topic line) · < 500 | clear AI (TPR) | 1 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 100.0 |
| level 1 (topic line) · >= 500 | clear AI (TPR) | 262 | 98.5 | 100.0 | 100.0 | 88.9 | 96.6 | 100.0 | 72.5 | 0.0 | 100.0 |
| level 2 (themes) · >= 500 | clear AI (TPR) | 263 | 99.2 | 100.0 | 100.0 | 88.2 | 96.2 | 100.0 | 75.7 | 0.0 | 100.0 |
| level 3 (themes and structure) · >= 500 | clear AI (TPR) | 263 | 96.6 | 100.0 | 100.0 | 89.4 | 97.7 | 100.0 | 75.7 | 0.0 | 100.0 |
| level 4 (themes and full outline) · < 500 | clear AI (TPR) | 3 | 100.0 | 100.0 | 100.0 | 66.7 | 33.3 | 100.0 | 100.0 | 0.0 | 100.0 |
| level 4 (themes and full outline) · >= 500 | clear AI (TPR) | 260 | 98.8 | 100.0 | 100.0 | 94.2 | 98.5 | 100.0 | 78.1 | 0.0 | 100.0 |
| level 5 (the source's outline) · < 500 | clear AI (TPR) | 12 | 100.0 | 100.0 | 100.0 | 83.3 | 91.7 | 100.0 | 83.3 | 0.0 | 100.0 |
| level 5 (the source's outline) · >= 500 | clear AI (TPR) | 251 | 98.4 | 100.0 | 100.0 | 94.0 | 97.6 | 100.0 | 79.7 | 0.0 | 99.2 |

### IdeaShift, AI sources: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| source (a model's document) | IdeaLens · outline (paraphrased) | 84.8 | 95.4 | 98.5 | 98.5 |
| source (a model's document) | IdeaLens · document | 79.1 | 96.6 | 100.0 | 100.0 |
| source (a model's document) | ProseLens | 98.9 | 100.0 | 100.0 | 100.0 |
| source (a model's document) | IdeaLens-ModernBERT-L · outline (paraphrased) | 58.6 | 80.2 | 96.2 | 98.1 |
| source (a model's document) | IdeaLens-ModernBERT-L · document | 42.6 | 77.6 | 98.9 | 100.0 |
| source (a model's document) | ProseLens-ModernBERT-L | 80.2 | 95.8 | 99.6 | 100.0 |
| source (a model's document) | EditLens-Llama-3B (cal.) | 0.0 | 42.2 | 93.9 | 98.9 |
| source (a model's document) | Binoculars (cal.) | 17.1 | 53.6 | 80.6 | 88.6 |
| level 0 (type line) | IdeaLens · outline (paraphrased) | 95.1 | 98.1 | 99.2 | 99.6 |
| level 0 (type line) | IdeaLens · document | 99.6 | 99.6 | 100.0 | 100.0 |
| level 0 (type line) | ProseLens | 100.0 | 100.0 | 100.0 | 100.0 |
| level 0 (type line) | IdeaLens-ModernBERT-L · outline (paraphrased) | 64.6 | 79.5 | 89.4 | 94.7 |
| level 0 (type line) | IdeaLens-ModernBERT-L · document | 89.4 | 93.9 | 97.7 | 99.2 |
| level 0 (type line) | ProseLens-ModernBERT-L | 99.2 | 100.0 | 100.0 | 100.0 |
| level 0 (type line) | EditLens-Llama-3B (cal.) | 0.0 | 33.5 | 97.3 | 100.0 |
| level 0 (type line) | Binoculars (cal.) | 0.0 | 0.0 | 3.4 | 11.4 |
| level 1 (topic line) | IdeaLens · outline (paraphrased) | 96.2 | 97.7 | 98.9 | 100.0 |
| level 1 (topic line) | IdeaLens · document | 100.0 | 100.0 | 100.0 | 100.0 |
| level 1 (topic line) | ProseLens | 100.0 | 100.0 | 100.0 | 100.0 |
| level 1 (topic line) | IdeaLens-ModernBERT-L · outline (paraphrased) | 63.5 | 85.2 | 92.4 | 95.4 |
| level 1 (topic line) | IdeaLens-ModernBERT-L · document | 90.5 | 95.8 | 98.5 | 99.2 |
| level 1 (topic line) | ProseLens-ModernBERT-L | 99.6 | 100.0 | 100.0 | 100.0 |
| level 1 (topic line) | EditLens-Llama-3B (cal.) | 0.0 | 29.7 | 96.6 | 100.0 |
| level 1 (topic line) | Binoculars (cal.) | 0.0 | 0.0 | 1.5 | 10.6 |
| level 2 (themes) | IdeaLens · outline (paraphrased) | 95.1 | 98.5 | 100.0 | 100.0 |
| level 2 (themes) | IdeaLens · document | 99.6 | 99.6 | 100.0 | 100.0 |
| level 2 (themes) | ProseLens | 100.0 | 100.0 | 100.0 | 100.0 |
| level 2 (themes) | IdeaLens-ModernBERT-L · outline (paraphrased) | 69.6 | 83.7 | 91.6 | 95.4 |
| level 2 (themes) | IdeaLens-ModernBERT-L · document | 86.3 | 92.8 | 98.9 | 100.0 |
| level 2 (themes) | ProseLens-ModernBERT-L | 99.6 | 100.0 | 100.0 | 100.0 |
| level 2 (themes) | EditLens-Llama-3B (cal.) | 0.0 | 34.6 | 98.9 | 100.0 |
| level 2 (themes) | Binoculars (cal.) | 0.0 | 0.0 | 1.5 | 8.0 |
| level 3 (themes and structure) | IdeaLens · outline (paraphrased) | 94.3 | 96.6 | 98.1 | 98.9 |
| level 3 (themes and structure) | IdeaLens · document | 100.0 | 100.0 | 100.0 | 100.0 |
| level 3 (themes and structure) | ProseLens | 100.0 | 100.0 | 100.0 | 100.0 |
| level 3 (themes and structure) | IdeaLens-ModernBERT-L · outline (paraphrased) | 71.1 | 85.9 | 92.8 | 93.9 |
| level 3 (themes and structure) | IdeaLens-ModernBERT-L · document | 91.3 | 95.4 | 99.2 | 100.0 |
| level 3 (themes and structure) | ProseLens-ModernBERT-L | 100.0 | 100.0 | 100.0 | 100.0 |
| level 3 (themes and structure) | EditLens-Llama-3B (cal.) | 0.0 | 31.6 | 97.7 | 100.0 |
| level 3 (themes and structure) | Binoculars (cal.) | 0.0 | 0.0 | 0.4 | 3.8 |
| level 4 (themes and full outline) | IdeaLens · outline (paraphrased) | 93.9 | 97.7 | 99.2 | 99.2 |
| level 4 (themes and full outline) | IdeaLens · document | 98.5 | 100.0 | 100.0 | 100.0 |
| level 4 (themes and full outline) | ProseLens | 100.0 | 100.0 | 100.0 | 100.0 |
| level 4 (themes and full outline) | IdeaLens-ModernBERT-L · outline (paraphrased) | 68.8 | 87.8 | 97.0 | 98.1 |
| level 4 (themes and full outline) | IdeaLens-ModernBERT-L · document | 77.2 | 91.6 | 99.6 | 100.0 |
| level 4 (themes and full outline) | ProseLens-ModernBERT-L | 98.5 | 100.0 | 100.0 | 100.0 |
| level 4 (themes and full outline) | EditLens-Llama-3B (cal.) | 0.0 | 30.0 | 98.9 | 100.0 |
| level 4 (themes and full outline) | Binoculars (cal.) | 0.0 | 0.0 | 2.7 | 8.7 |
| level 5 (the source's outline) | IdeaLens · outline (paraphrased) | 85.9 | 96.6 | 99.2 | 99.6 |
| level 5 (the source's outline) | IdeaLens · document | 94.7 | 99.2 | 100.0 | 100.0 |
| level 5 (the source's outline) | ProseLens | 99.2 | 100.0 | 100.0 | 100.0 |
| level 5 (the source's outline) | IdeaLens-ModernBERT-L · outline (paraphrased) | 60.8 | 85.6 | 97.3 | 98.9 |
| level 5 (the source's outline) | IdeaLens-ModernBERT-L · document | 63.5 | 86.3 | 99.6 | 100.0 |
| level 5 (the source's outline) | ProseLens-ModernBERT-L | 93.2 | 98.9 | 100.0 | 100.0 |
| level 5 (the source's outline) | EditLens-Llama-3B (cal.) | 0.0 | 30.4 | 99.6 | 100.0 |
| level 5 (the source's outline) | Binoculars (cal.) | 0.0 | 0.0 | 8.0 | 22.1 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline (paraphrased) | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline (paraphrased) | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5.6-luna | source (a model's document) | 65 | 98.5 | 98.5 | 100.0 | 90.8 | 93.8 | 98.5 | 76.9 | 61.5 | 72.3 |
| gpt-5.6-sol | source (a model's document) | 131 | 98.5 | 97.7 | 100.0 | 93.1 | 95.4 | 99.2 | 80.2 | 50.4 | 71.8 |
| gpt-5.6-terra | source (a model's document) | 67 | 97.0 | 100.0 | 100.0 | 92.5 | 92.5 | 100.0 | 71.6 | 52.2 | 77.6 |
| gpt-5.6-luna | level 0 (type line) | 65 | 98.5 | 100.0 | 100.0 | 87.7 | 96.9 | 100.0 | 81.5 | 0.0 | 100.0 |
| gpt-5.6-sol | level 0 (type line) | 131 | 97.7 | 99.2 | 100.0 | 86.3 | 95.4 | 100.0 | 68.7 | 0.0 | 100.0 |
| gpt-5.6-terra | level 0 (type line) | 67 | 98.5 | 100.0 | 100.0 | 77.6 | 97.0 | 100.0 | 80.6 | 0.0 | 100.0 |
| gpt-5.6-luna | level 1 (topic line) | 65 | 100.0 | 100.0 | 100.0 | 89.2 | 98.5 | 100.0 | 84.6 | 0.0 | 100.0 |
| gpt-5.6-sol | level 1 (topic line) | 131 | 99.2 | 100.0 | 100.0 | 91.6 | 95.4 | 100.0 | 69.5 | 0.0 | 100.0 |
| gpt-5.6-terra | level 1 (topic line) | 67 | 95.5 | 100.0 | 100.0 | 83.6 | 97.0 | 100.0 | 67.2 | 0.0 | 100.0 |
| gpt-5.6-luna | level 2 (themes) | 65 | 98.5 | 100.0 | 100.0 | 90.8 | 95.4 | 100.0 | 84.6 | 0.0 | 100.0 |
| gpt-5.6-sol | level 2 (themes) | 131 | 99.2 | 100.0 | 100.0 | 88.5 | 96.2 | 100.0 | 70.2 | 0.0 | 100.0 |
| gpt-5.6-terra | level 2 (themes) | 67 | 100.0 | 100.0 | 100.0 | 85.1 | 97.0 | 100.0 | 77.6 | 0.0 | 100.0 |
| gpt-5.6-luna | level 3 (themes and structure) | 65 | 98.5 | 100.0 | 100.0 | 93.8 | 98.5 | 100.0 | 84.6 | 0.0 | 100.0 |
| gpt-5.6-sol | level 3 (themes and structure) | 131 | 94.7 | 100.0 | 100.0 | 90.8 | 97.7 | 100.0 | 68.7 | 0.0 | 100.0 |
| gpt-5.6-terra | level 3 (themes and structure) | 67 | 98.5 | 100.0 | 100.0 | 82.1 | 97.0 | 100.0 | 80.6 | 0.0 | 100.0 |
| gpt-5.6-luna | level 4 (themes and full outline) | 65 | 100.0 | 100.0 | 100.0 | 93.8 | 96.9 | 100.0 | 84.6 | 0.0 | 100.0 |
| gpt-5.6-sol | level 4 (themes and full outline) | 131 | 99.2 | 100.0 | 100.0 | 93.9 | 97.7 | 100.0 | 76.3 | 0.0 | 100.0 |
| gpt-5.6-terra | level 4 (themes and full outline) | 67 | 97.0 | 100.0 | 100.0 | 94.0 | 98.5 | 100.0 | 76.1 | 0.0 | 100.0 |
| gpt-5.6-luna | level 5 (the source's outline) | 65 | 100.0 | 100.0 | 100.0 | 98.5 | 96.9 | 100.0 | 81.5 | 0.0 | 100.0 |
| gpt-5.6-sol | level 5 (the source's outline) | 131 | 98.5 | 100.0 | 100.0 | 93.9 | 99.2 | 100.0 | 79.4 | 0.0 | 100.0 |
| gpt-5.6-terra | level 5 (the source's outline) | 67 | 97.0 | 100.0 | 100.0 | 88.1 | 94.0 | 100.0 | 79.1 | 0.0 | 97.0 |

**By format.** Fire rate % at the 1% cut.

| Format | Arm | n | IdeaLens · outline (paraphrased) | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline (paraphrased) | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Academic Writing | source (a model's document) | 36 | 100.0 | 100.0 | 100.0 | 100.0 | 94.4 | 97.2 | 80.6 | 88.9 | 66.7 |
| Creative Writing | source (a model's document) | 35 | 100.0 | 100.0 | 100.0 | 97.1 | 100.0 | 100.0 | 71.4 | 85.7 | 88.6 |
| Knowledge Article | source (a model's document) | 31 | 96.8 | 96.8 | 100.0 | 77.4 | 100.0 | 100.0 | 67.7 | 38.7 | 71.0 |
| News Article | source (a model's document) | 38 | 97.4 | 94.7 | 100.0 | 97.4 | 92.1 | 100.0 | 81.6 | 52.6 | 78.9 |
| Nonfiction Writing | source (a model's document) | 31 | 93.5 | 100.0 | 100.0 | 83.9 | 96.8 | 96.8 | 80.6 | 32.3 | 83.9 |
| Personal About Page | source (a model's document) | 29 | 96.6 | 96.6 | 100.0 | 82.8 | 75.9 | 100.0 | 82.8 | 44.8 | 55.2 |
| Personal Blog | source (a model's document) | 36 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 77.8 | 44.4 | 72.2 |
| User Reviews | source (a model's document) | 27 | 100.0 | 100.0 | 100.0 | 96.3 | 92.6 | 100.0 | 74.1 | 29.6 | 66.7 |
| Academic Writing | level 0 (type line) | 36 | 100.0 | 100.0 | 100.0 | 80.6 | 97.2 | 100.0 | 88.9 | 0.0 | 100.0 |
| Creative Writing | level 0 (type line) | 35 | 91.4 | 100.0 | 100.0 | 51.4 | 82.9 | 100.0 | 40.0 | 0.0 | 100.0 |
| Knowledge Article | level 0 (type line) | 31 | 100.0 | 100.0 | 100.0 | 93.5 | 100.0 | 100.0 | 93.5 | 0.0 | 100.0 |
| News Article | level 0 (type line) | 38 | 94.7 | 97.4 | 100.0 | 84.2 | 92.1 | 100.0 | 71.1 | 0.0 | 100.0 |
| Nonfiction Writing | level 0 (type line) | 31 | 100.0 | 100.0 | 100.0 | 90.3 | 100.0 | 100.0 | 67.7 | 0.0 | 100.0 |
| Personal About Page | level 0 (type line) | 29 | 100.0 | 100.0 | 100.0 | 89.7 | 100.0 | 100.0 | 93.1 | 0.0 | 100.0 |
| Personal Blog | level 0 (type line) | 36 | 100.0 | 100.0 | 100.0 | 97.2 | 100.0 | 100.0 | 88.9 | 0.0 | 100.0 |
| User Reviews | level 0 (type line) | 27 | 100.0 | 100.0 | 100.0 | 92.6 | 100.0 | 100.0 | 55.6 | 0.0 | 100.0 |
| Academic Writing | level 1 (topic line) | 36 | 100.0 | 100.0 | 100.0 | 88.9 | 97.2 | 100.0 | 83.3 | 0.0 | 100.0 |
| Creative Writing | level 1 (topic line) | 35 | 91.4 | 100.0 | 100.0 | 54.3 | 88.6 | 100.0 | 51.4 | 0.0 | 100.0 |
| Knowledge Article | level 1 (topic line) | 31 | 100.0 | 100.0 | 100.0 | 90.3 | 100.0 | 100.0 | 93.5 | 0.0 | 100.0 |
| News Article | level 1 (topic line) | 38 | 100.0 | 100.0 | 100.0 | 97.4 | 92.1 | 100.0 | 76.3 | 0.0 | 100.0 |
| Nonfiction Writing | level 1 (topic line) | 31 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 61.3 | 0.0 | 100.0 |
| Personal About Page | level 1 (topic line) | 29 | 100.0 | 100.0 | 100.0 | 89.7 | 96.6 | 100.0 | 82.8 | 0.0 | 100.0 |
| Personal Blog | level 1 (topic line) | 36 | 100.0 | 100.0 | 100.0 | 97.2 | 100.0 | 100.0 | 69.4 | 0.0 | 100.0 |
| User Reviews | level 1 (topic line) | 27 | 96.3 | 100.0 | 100.0 | 96.3 | 100.0 | 100.0 | 63.0 | 0.0 | 100.0 |
| Academic Writing | level 2 (themes) | 36 | 100.0 | 100.0 | 100.0 | 86.1 | 97.2 | 100.0 | 75.0 | 0.0 | 100.0 |
| Creative Writing | level 2 (themes) | 35 | 94.3 | 100.0 | 100.0 | 60.0 | 91.4 | 100.0 | 51.4 | 0.0 | 100.0 |
| Knowledge Article | level 2 (themes) | 31 | 100.0 | 100.0 | 100.0 | 83.9 | 93.5 | 100.0 | 87.1 | 0.0 | 100.0 |
| News Article | level 2 (themes) | 38 | 100.0 | 100.0 | 100.0 | 100.0 | 94.7 | 100.0 | 81.6 | 0.0 | 100.0 |
| Nonfiction Writing | level 2 (themes) | 31 | 100.0 | 100.0 | 100.0 | 87.1 | 100.0 | 100.0 | 51.6 | 0.0 | 100.0 |
| Personal About Page | level 2 (themes) | 29 | 100.0 | 100.0 | 100.0 | 93.1 | 96.6 | 100.0 | 93.1 | 0.0 | 100.0 |
| Personal Blog | level 2 (themes) | 36 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 83.3 | 0.0 | 100.0 |
| User Reviews | level 2 (themes) | 27 | 100.0 | 100.0 | 100.0 | 96.3 | 96.3 | 100.0 | 85.2 | 0.0 | 100.0 |
| Academic Writing | level 3 (themes and structure) | 36 | 97.2 | 100.0 | 100.0 | 80.6 | 94.4 | 100.0 | 80.6 | 0.0 | 100.0 |
| Creative Writing | level 3 (themes and structure) | 35 | 82.9 | 100.0 | 100.0 | 60.0 | 91.4 | 100.0 | 60.0 | 0.0 | 100.0 |
| Knowledge Article | level 3 (themes and structure) | 31 | 96.8 | 100.0 | 100.0 | 90.3 | 96.8 | 100.0 | 74.2 | 0.0 | 100.0 |
| News Article | level 3 (themes and structure) | 38 | 97.4 | 100.0 | 100.0 | 97.4 | 100.0 | 100.0 | 84.2 | 0.0 | 100.0 |
| Nonfiction Writing | level 3 (themes and structure) | 31 | 100.0 | 100.0 | 100.0 | 93.5 | 100.0 | 100.0 | 77.4 | 0.0 | 100.0 |
| Personal About Page | level 3 (themes and structure) | 29 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 86.2 | 0.0 | 100.0 |
| Personal Blog | level 3 (themes and structure) | 36 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 75.0 | 0.0 | 100.0 |
| User Reviews | level 3 (themes and structure) | 27 | 100.0 | 100.0 | 100.0 | 96.3 | 100.0 | 100.0 | 66.7 | 0.0 | 100.0 |
| Academic Writing | level 4 (themes and full outline) | 36 | 100.0 | 100.0 | 100.0 | 97.2 | 97.2 | 100.0 | 83.3 | 0.0 | 100.0 |
| Creative Writing | level 4 (themes and full outline) | 35 | 97.1 | 100.0 | 100.0 | 80.0 | 97.1 | 100.0 | 57.1 | 0.0 | 100.0 |
| Knowledge Article | level 4 (themes and full outline) | 31 | 96.8 | 100.0 | 100.0 | 96.8 | 100.0 | 100.0 | 87.1 | 0.0 | 100.0 |
| News Article | level 4 (themes and full outline) | 38 | 100.0 | 100.0 | 100.0 | 100.0 | 94.7 | 100.0 | 78.9 | 0.0 | 100.0 |
| Nonfiction Writing | level 4 (themes and full outline) | 31 | 96.8 | 100.0 | 100.0 | 83.9 | 100.0 | 100.0 | 74.2 | 0.0 | 100.0 |
| Personal About Page | level 4 (themes and full outline) | 29 | 100.0 | 100.0 | 100.0 | 96.6 | 96.6 | 100.0 | 86.2 | 0.0 | 100.0 |
| Personal Blog | level 4 (themes and full outline) | 36 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 86.1 | 0.0 | 100.0 |
| User Reviews | level 4 (themes and full outline) | 27 | 100.0 | 100.0 | 100.0 | 96.3 | 96.3 | 100.0 | 74.1 | 0.0 | 100.0 |
| Academic Writing | level 5 (the source's outline) | 36 | 100.0 | 100.0 | 100.0 | 100.0 | 91.7 | 100.0 | 88.9 | 0.0 | 100.0 |
| Creative Writing | level 5 (the source's outline) | 35 | 97.1 | 100.0 | 100.0 | 88.6 | 100.0 | 100.0 | 57.1 | 0.0 | 97.1 |
| Knowledge Article | level 5 (the source's outline) | 31 | 100.0 | 100.0 | 100.0 | 96.8 | 100.0 | 100.0 | 80.6 | 0.0 | 100.0 |
| News Article | level 5 (the source's outline) | 38 | 97.4 | 100.0 | 100.0 | 89.5 | 94.7 | 100.0 | 76.3 | 0.0 | 97.4 |
| Nonfiction Writing | level 5 (the source's outline) | 31 | 93.5 | 100.0 | 100.0 | 80.6 | 100.0 | 100.0 | 71.0 | 0.0 | 100.0 |
| Personal About Page | level 5 (the source's outline) | 29 | 100.0 | 100.0 | 100.0 | 93.1 | 93.1 | 100.0 | 86.2 | 0.0 | 100.0 |
| Personal Blog | level 5 (the source's outline) | 36 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 97.2 | 0.0 | 100.0 |
| User Reviews | level 5 (the source's outline) | 27 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 81.5 | 0.0 | 100.0 |
