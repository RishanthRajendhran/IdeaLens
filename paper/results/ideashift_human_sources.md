### IdeaShift, human sources: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- 237 human sources from the 1M test split, each rewritten by a model at six levels that hand over more and more of the source: level 0 names only the type, topic and length; level 5 hands over the source's whole outline. The generator is held constant within a source (sol 119, terra 58, luna 60).
- Labels: the source is clear human (FPR); levels 0 and 1 are model ideas, model prose (TPR); levels 2 and 3 are mixed, AI-leaning, and level 4 mixed, human-leaning (fire rates); level 5 is human ideas, model prose (FPR).
- Level 5 is the 2026-09-14 regeneration, sent with its system prompt (realise every item, add nothing); the first generation had been sent without it and added items (median 1.29x the source's).
- Sources: Pangram 4 is shown for the IdeaShift figure, but it is circular there (the sources' silver labels are Pangram 3.3.2 verdicts), so its source rate is agreement with its own labels, not accuracy. IdeaLens on the document covers 237 of 237 sources.

| Arm | Label | n | IdeaLens · outline (paraphrased) | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline (paraphrased) | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| source (the person's document) | clear human (FPR) | 237 | 3.4 | 3.4 | 2.1 | 0.8 | 2.1 | 2.5 | 2.5 | 0.8 | 0.4 |
| level 0 (type line) | model ideas (TPR) | 237 | 94.9 | 98.7 | 99.2 | 73.8 | 93.2 | 99.6 | 68.4 | 0.0 | 100.0 |
| level 1 (topic line) | model ideas (TPR) | 237 | 91.1 | 98.3 | 99.6 | 69.2 | 92.4 | 99.6 | 59.5 | 0.4 | 100.0 |
| level 2 (themes) | mixed, AI-leaning (fire rate) | 237 | 86.1 | 97.0 | 98.7 | 65.8 | 88.6 | 98.7 | 57.0 | 0.0 | 100.0 |
| level 3 (themes and structure) | mixed, AI-leaning (fire rate) | 237 | 78.9 | 97.5 | 99.6 | 63.7 | 90.3 | 98.3 | 54.0 | 0.0 | 99.6 |
| level 4 (themes and full outline) | mixed, human-leaning (fire rate) | 237 | 23.6 | 75.1 | 94.9 | 16.0 | 48.5 | 95.4 | 29.5 | 0.0 | 98.3 |
| level 5 (the source's outline) | human ideas, AI prose (FPR) | 237 | 6.8 | 54.4 | 86.5 | 6.8 | 36.3 | 78.5 | 16.0 | 0.0 | 92.4 |
| AUC, levels 0-1 vs source | | | 0.991 | 0.998 | 0.999 | 0.964 | 0.991 | 0.997 | 0.980 | 0.425 | 0.998 |

**Length.** Share under 500 words: source (the person's document) 0.0%, level 0 (type line) 0.4%, level 1 (topic line) 0.4%, level 2 (themes) 2.1%, level 3 (themes and structure) 1.3%, level 4 (themes and full outline) 2.5%, level 5 (the source's outline) 5.5%.

| Arm · length | Label | n | IdeaLens · outline (paraphrased) | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline (paraphrased) | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| source (the person's document) · >= 500 | clear human (FPR) | 237 | 3.4 | 3.4 | 2.1 | 0.8 | 2.1 | 2.5 | 2.5 | 0.8 | 0.4 |
| level 0 (type line) · < 500 | model ideas (TPR) | 1 | 100.0 | 100.0 | 100.0 | 0.0 | 0.0 | 100.0 | 100.0 | 0.0 | 100.0 |
| level 0 (type line) · >= 500 | model ideas (TPR) | 236 | 94.9 | 98.7 | 99.2 | 74.2 | 93.6 | 99.6 | 68.2 | 0.0 | 100.0 |
| level 1 (topic line) · < 500 | model ideas (TPR) | 1 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 100.0 |
| level 1 (topic line) · >= 500 | model ideas (TPR) | 236 | 91.1 | 98.3 | 99.6 | 69.1 | 92.4 | 99.6 | 59.3 | 0.4 | 100.0 |
| level 2 (themes) · < 500 | mixed, AI-leaning (fire rate) | 5 | 80.0 | 80.0 | 100.0 | 60.0 | 60.0 | 80.0 | 60.0 | 0.0 | 100.0 |
| level 2 (themes) · >= 500 | mixed, AI-leaning (fire rate) | 232 | 86.2 | 97.4 | 98.7 | 65.9 | 89.2 | 99.1 | 56.9 | 0.0 | 100.0 |
| level 3 (themes and structure) · < 500 | mixed, AI-leaning (fire rate) | 3 | 33.3 | 66.7 | 100.0 | 0.0 | 0.0 | 33.3 | 0.0 | 0.0 | 66.7 |
| level 3 (themes and structure) · >= 500 | mixed, AI-leaning (fire rate) | 234 | 79.5 | 97.9 | 99.6 | 64.5 | 91.5 | 99.1 | 54.7 | 0.0 | 100.0 |
| level 4 (themes and full outline) · < 500 | mixed, human-leaning (fire rate) | 6 | 33.3 | 50.0 | 83.3 | 0.0 | 0.0 | 16.7 | 33.3 | 0.0 | 83.3 |
| level 4 (themes and full outline) · >= 500 | mixed, human-leaning (fire rate) | 231 | 23.4 | 75.8 | 95.2 | 16.5 | 49.8 | 97.4 | 29.4 | 0.0 | 98.7 |
| level 5 (the source's outline) · < 500 | human ideas, AI prose (FPR) | 13 | 7.7 | 15.4 | 46.2 | 0.0 | 7.7 | 23.1 | 15.4 | 0.0 | 58.3 |
| level 5 (the source's outline) · >= 500 | human ideas, AI prose (FPR) | 224 | 6.7 | 56.7 | 88.8 | 7.1 | 37.9 | 81.7 | 16.1 | 0.0 | 94.2 |

### IdeaShift, human sources: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| source (the person's document) | IdeaLens · outline (paraphrased) | 0.4 | 2.1 | 5.9 | 6.8 |
| source (the person's document) | IdeaLens · document | 1.3 | 1.7 | 4.6 | 7.6 |
| source (the person's document) | ProseLens | 0.8 | 1.7 | 3.8 | 4.6 |
| source (the person's document) | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.0 | 0.4 | 3.0 | 8.9 |
| source (the person's document) | IdeaLens-ModernBERT-L · document | 0.8 | 1.3 | 5.5 | 7.6 |
| source (the person's document) | ProseLens-ModernBERT-L | 0.0 | 1.3 | 4.2 | 5.5 |
| source (the person's document) | EditLens-Llama-3B (cal.) | 0.0 | 1.3 | 3.8 | 8.0 |
| source (the person's document) | Binoculars (cal.) | 0.0 | 0.8 | 2.1 | 5.9 |
| level 0 (type line) | IdeaLens · outline (paraphrased) | 88.6 | 93.7 | 96.6 | 97.5 |
| level 0 (type line) | IdeaLens · document | 97.5 | 98.3 | 99.6 | 99.6 |
| level 0 (type line) | ProseLens | 99.2 | 99.2 | 99.2 | 99.6 |
| level 0 (type line) | IdeaLens-ModernBERT-L · outline (paraphrased) | 49.8 | 65.4 | 81.4 | 89.5 |
| level 0 (type line) | IdeaLens-ModernBERT-L · document | 86.5 | 91.1 | 94.9 | 98.3 |
| level 0 (type line) | ProseLens-ModernBERT-L | 98.7 | 99.6 | 99.6 | 99.6 |
| level 0 (type line) | EditLens-Llama-3B (cal.) | 0.0 | 30.0 | 94.1 | 100.0 |
| level 0 (type line) | Binoculars (cal.) | 0.0 | 0.0 | 0.8 | 9.3 |
| level 1 (topic line) | IdeaLens · outline (paraphrased) | 81.4 | 89.9 | 93.2 | 96.6 |
| level 1 (topic line) | IdeaLens · document | 97.5 | 97.9 | 99.2 | 99.6 |
| level 1 (topic line) | ProseLens | 99.2 | 99.6 | 99.6 | 99.6 |
| level 1 (topic line) | IdeaLens-ModernBERT-L · outline (paraphrased) | 49.8 | 62.9 | 81.0 | 90.7 |
| level 1 (topic line) | IdeaLens-ModernBERT-L · document | 82.7 | 86.9 | 96.6 | 98.7 |
| level 1 (topic line) | ProseLens-ModernBERT-L | 99.2 | 99.6 | 99.6 | 99.6 |
| level 1 (topic line) | EditLens-Llama-3B (cal.) | 0.0 | 24.5 | 91.6 | 99.6 |
| level 1 (topic line) | Binoculars (cal.) | 0.0 | 0.4 | 3.0 | 5.9 |
| level 2 (themes) | IdeaLens · outline (paraphrased) | 74.7 | 81.9 | 92.0 | 94.1 |
| level 2 (themes) | IdeaLens · document | 94.5 | 95.8 | 98.3 | 99.6 |
| level 2 (themes) | ProseLens | 97.5 | 98.3 | 99.2 | 99.6 |
| level 2 (themes) | IdeaLens-ModernBERT-L · outline (paraphrased) | 40.1 | 58.2 | 75.5 | 87.3 |
| level 2 (themes) | IdeaLens-ModernBERT-L · document | 76.8 | 83.5 | 92.0 | 96.6 |
| level 2 (themes) | ProseLens-ModernBERT-L | 97.0 | 98.3 | 99.2 | 99.6 |
| level 2 (themes) | EditLens-Llama-3B (cal.) | 0.0 | 18.6 | 89.5 | 99.6 |
| level 2 (themes) | Binoculars (cal.) | 0.0 | 0.0 | 2.1 | 8.0 |
| level 3 (themes and structure) | IdeaLens · outline (paraphrased) | 67.9 | 76.8 | 87.3 | 94.9 |
| level 3 (themes and structure) | IdeaLens · document | 95.4 | 97.5 | 98.7 | 99.6 |
| level 3 (themes and structure) | ProseLens | 98.3 | 98.7 | 99.6 | 99.6 |
| level 3 (themes and structure) | IdeaLens-ModernBERT-L · outline (paraphrased) | 37.6 | 54.4 | 73.8 | 84.4 |
| level 3 (themes and structure) | IdeaLens-ModernBERT-L · document | 81.4 | 87.3 | 94.9 | 97.9 |
| level 3 (themes and structure) | ProseLens-ModernBERT-L | 97.5 | 97.9 | 98.7 | 99.6 |
| level 3 (themes and structure) | EditLens-Llama-3B (cal.) | 0.0 | 17.7 | 90.3 | 99.2 |
| level 3 (themes and structure) | Binoculars (cal.) | 0.0 | 0.0 | 0.8 | 2.5 |
| level 4 (themes and full outline) | IdeaLens · outline (paraphrased) | 10.1 | 18.6 | 33.3 | 48.9 |
| level 4 (themes and full outline) | IdeaLens · document | 59.1 | 70.5 | 86.1 | 94.5 |
| level 4 (themes and full outline) | ProseLens | 89.9 | 93.7 | 96.6 | 98.3 |
| level 4 (themes and full outline) | IdeaLens-ModernBERT-L · outline (paraphrased) | 3.0 | 13.5 | 23.6 | 41.8 |
| level 4 (themes and full outline) | IdeaLens-ModernBERT-L · document | 32.1 | 41.8 | 62.9 | 85.7 |
| level 4 (themes and full outline) | ProseLens-ModernBERT-L | 82.3 | 91.1 | 97.5 | 99.2 |
| level 4 (themes and full outline) | EditLens-Llama-3B (cal.) | 0.0 | 4.2 | 69.2 | 96.2 |
| level 4 (themes and full outline) | Binoculars (cal.) | 0.0 | 0.0 | 0.8 | 2.1 |
| level 5 (the source's outline) | IdeaLens · outline (paraphrased) | 2.1 | 5.9 | 12.2 | 19.0 |
| level 5 (the source's outline) | IdeaLens · document | 37.6 | 48.5 | 70.5 | 82.3 |
| level 5 (the source's outline) | ProseLens | 77.2 | 82.7 | 90.3 | 97.0 |
| level 5 (the source's outline) | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.8 | 3.8 | 11.8 | 23.2 |
| level 5 (the source's outline) | IdeaLens-ModernBERT-L · document | 20.7 | 29.1 | 51.1 | 73.0 |
| level 5 (the source's outline) | ProseLens-ModernBERT-L | 57.8 | 70.9 | 92.4 | 98.3 |
| level 5 (the source's outline) | EditLens-Llama-3B (cal.) | 0.0 | 1.3 | 62.0 | 94.9 |
| level 5 (the source's outline) | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 3.4 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline (paraphrased) | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline (paraphrased) | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5.6-luna | level 0 (type line) | 60 | 93.3 | 98.3 | 98.3 | 81.7 | 95.0 | 98.3 | 78.3 | 0.0 | 100.0 |
| gpt-5.6-sol | level 0 (type line) | 119 | 96.6 | 98.3 | 99.2 | 67.2 | 92.4 | 100.0 | 63.0 | 0.0 | 100.0 |
| gpt-5.6-terra | level 0 (type line) | 58 | 93.1 | 100.0 | 100.0 | 79.3 | 93.1 | 100.0 | 69.0 | 0.0 | 100.0 |
| gpt-5.6-luna | level 1 (topic line) | 60 | 91.7 | 98.3 | 98.3 | 78.3 | 90.0 | 98.3 | 73.3 | 1.7 | 100.0 |
| gpt-5.6-sol | level 1 (topic line) | 119 | 91.6 | 98.3 | 100.0 | 65.5 | 93.3 | 100.0 | 54.6 | 0.0 | 100.0 |
| gpt-5.6-terra | level 1 (topic line) | 58 | 89.7 | 98.3 | 100.0 | 67.2 | 93.1 | 100.0 | 55.2 | 0.0 | 100.0 |
| gpt-5.6-luna | level 2 (themes) | 60 | 91.7 | 95.0 | 96.7 | 78.3 | 91.7 | 96.7 | 61.7 | 0.0 | 100.0 |
| gpt-5.6-sol | level 2 (themes) | 119 | 85.7 | 97.5 | 99.2 | 63.9 | 87.4 | 100.0 | 52.9 | 0.0 | 100.0 |
| gpt-5.6-terra | level 2 (themes) | 58 | 81.0 | 98.3 | 100.0 | 56.9 | 87.9 | 98.3 | 60.3 | 0.0 | 100.0 |
| gpt-5.6-luna | level 3 (themes and structure) | 60 | 88.3 | 98.3 | 98.3 | 76.7 | 93.3 | 96.7 | 65.0 | 0.0 | 100.0 |
| gpt-5.6-sol | level 3 (themes and structure) | 119 | 71.4 | 96.6 | 100.0 | 57.1 | 88.2 | 99.2 | 47.1 | 0.0 | 99.2 |
| gpt-5.6-terra | level 3 (themes and structure) | 58 | 84.5 | 98.3 | 100.0 | 63.8 | 91.4 | 98.3 | 56.9 | 0.0 | 100.0 |
| gpt-5.6-luna | level 4 (themes and full outline) | 60 | 35.0 | 83.3 | 91.7 | 23.3 | 58.3 | 91.7 | 41.7 | 0.0 | 96.7 |
| gpt-5.6-sol | level 4 (themes and full outline) | 119 | 21.0 | 68.9 | 95.8 | 14.3 | 45.4 | 96.6 | 25.2 | 0.0 | 99.2 |
| gpt-5.6-terra | level 4 (themes and full outline) | 58 | 17.2 | 79.3 | 96.6 | 12.1 | 44.8 | 96.6 | 25.9 | 0.0 | 98.3 |
| gpt-5.6-luna | level 5 (the source's outline) | 60 | 8.3 | 70.0 | 86.7 | 6.7 | 41.7 | 78.3 | 18.3 | 0.0 | 95.0 |
| gpt-5.6-sol | level 5 (the source's outline) | 119 | 5.9 | 48.7 | 84.9 | 8.4 | 36.1 | 77.3 | 13.4 | 0.0 | 92.4 |
| gpt-5.6-terra | level 5 (the source's outline) | 58 | 6.9 | 50.0 | 89.7 | 3.4 | 31.0 | 81.0 | 19.0 | 0.0 | 89.7 |

**By format.** Fire rate % at the 1% cut.

| Format | Arm | n | IdeaLens · outline (paraphrased) | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline (paraphrased) | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Academic Writing | source (the person's document) | 27 | 3.7 | 3.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Creative Writing | source (the person's document) | 28 | 3.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Knowledge Article | source (the person's document) | 32 | 3.1 | 3.1 | 0.0 | 0.0 | 0.0 | 3.1 | 3.1 | 3.1 | 0.0 |
| News Article | source (the person's document) | 25 | 0.0 | 4.0 | 4.0 | 0.0 | 0.0 | 4.0 | 0.0 | 0.0 | 0.0 |
| Nonfiction Writing | source (the person's document) | 31 | 9.7 | 9.7 | 9.7 | 6.5 | 9.7 | 9.7 | 12.9 | 3.2 | 3.2 |
| Personal About Page | source (the person's document) | 33 | 0.0 | 3.0 | 0.0 | 0.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Personal Blog | source (the person's document) | 26 | 7.7 | 3.8 | 3.8 | 0.0 | 3.8 | 3.8 | 3.8 | 0.0 | 0.0 |
| User Reviews | source (the person's document) | 35 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Academic Writing | level 0 (type line) | 27 | 88.9 | 96.3 | 100.0 | 63.0 | 81.5 | 100.0 | 66.7 | 0.0 | 100.0 |
| Creative Writing | level 0 (type line) | 28 | 85.7 | 96.4 | 96.4 | 50.0 | 85.7 | 96.4 | 42.9 | 0.0 | 100.0 |
| Knowledge Article | level 0 (type line) | 32 | 93.8 | 100.0 | 100.0 | 75.0 | 96.9 | 100.0 | 90.6 | 0.0 | 100.0 |
| News Article | level 0 (type line) | 25 | 92.0 | 96.0 | 96.0 | 68.0 | 80.0 | 100.0 | 56.0 | 0.0 | 100.0 |
| Nonfiction Writing | level 0 (type line) | 31 | 96.8 | 100.0 | 100.0 | 74.2 | 100.0 | 100.0 | 45.2 | 0.0 | 100.0 |
| Personal About Page | level 0 (type line) | 33 | 100.0 | 100.0 | 100.0 | 84.8 | 100.0 | 100.0 | 90.9 | 0.0 | 100.0 |
| Personal Blog | level 0 (type line) | 26 | 100.0 | 100.0 | 100.0 | 88.5 | 100.0 | 100.0 | 73.1 | 0.0 | 100.0 |
| User Reviews | level 0 (type line) | 35 | 100.0 | 100.0 | 100.0 | 82.9 | 97.1 | 100.0 | 74.3 | 0.0 | 100.0 |
| Academic Writing | level 1 (topic line) | 27 | 85.2 | 92.6 | 100.0 | 66.7 | 85.2 | 100.0 | 59.3 | 0.0 | 100.0 |
| Creative Writing | level 1 (topic line) | 28 | 78.6 | 96.4 | 96.4 | 46.4 | 85.7 | 96.4 | 42.9 | 3.6 | 100.0 |
| Knowledge Article | level 1 (topic line) | 32 | 90.6 | 100.0 | 100.0 | 62.5 | 93.8 | 100.0 | 78.1 | 0.0 | 100.0 |
| News Article | level 1 (topic line) | 25 | 88.0 | 96.0 | 100.0 | 72.0 | 72.0 | 100.0 | 40.0 | 0.0 | 100.0 |
| Nonfiction Writing | level 1 (topic line) | 31 | 96.8 | 100.0 | 100.0 | 80.6 | 100.0 | 100.0 | 54.8 | 0.0 | 100.0 |
| Personal About Page | level 1 (topic line) | 33 | 97.0 | 100.0 | 100.0 | 81.8 | 100.0 | 100.0 | 87.9 | 0.0 | 100.0 |
| Personal Blog | level 1 (topic line) | 26 | 96.2 | 100.0 | 100.0 | 76.9 | 100.0 | 100.0 | 50.0 | 0.0 | 100.0 |
| User Reviews | level 1 (topic line) | 35 | 94.3 | 100.0 | 100.0 | 65.7 | 97.1 | 100.0 | 54.3 | 0.0 | 100.0 |
| Academic Writing | level 2 (themes) | 27 | 81.5 | 92.6 | 96.3 | 63.0 | 85.2 | 100.0 | 40.7 | 0.0 | 100.0 |
| Creative Writing | level 2 (themes) | 28 | 78.6 | 89.3 | 92.9 | 35.7 | 60.7 | 89.3 | 35.7 | 0.0 | 100.0 |
| Knowledge Article | level 2 (themes) | 32 | 75.0 | 96.9 | 100.0 | 56.2 | 87.5 | 100.0 | 56.2 | 0.0 | 100.0 |
| News Article | level 2 (themes) | 25 | 84.0 | 96.0 | 100.0 | 72.0 | 84.0 | 100.0 | 48.0 | 0.0 | 100.0 |
| Nonfiction Writing | level 2 (themes) | 31 | 93.5 | 100.0 | 100.0 | 74.2 | 100.0 | 100.0 | 54.8 | 0.0 | 100.0 |
| Personal About Page | level 2 (themes) | 33 | 97.0 | 100.0 | 100.0 | 81.8 | 97.0 | 100.0 | 84.8 | 0.0 | 100.0 |
| Personal Blog | level 2 (themes) | 26 | 84.6 | 100.0 | 100.0 | 65.4 | 96.2 | 100.0 | 46.2 | 0.0 | 100.0 |
| User Reviews | level 2 (themes) | 35 | 91.4 | 100.0 | 100.0 | 74.3 | 94.3 | 100.0 | 77.1 | 0.0 | 100.0 |
| Academic Writing | level 3 (themes and structure) | 27 | 63.0 | 88.9 | 100.0 | 48.1 | 85.2 | 100.0 | 51.9 | 0.0 | 100.0 |
| Creative Writing | level 3 (themes and structure) | 28 | 67.9 | 96.4 | 96.4 | 21.4 | 71.4 | 89.3 | 25.0 | 0.0 | 100.0 |
| Knowledge Article | level 3 (themes and structure) | 32 | 81.2 | 100.0 | 100.0 | 62.5 | 93.8 | 100.0 | 53.1 | 0.0 | 100.0 |
| News Article | level 3 (themes and structure) | 25 | 76.0 | 96.0 | 100.0 | 68.0 | 84.0 | 100.0 | 44.0 | 0.0 | 100.0 |
| Nonfiction Writing | level 3 (themes and structure) | 31 | 80.6 | 100.0 | 100.0 | 80.6 | 100.0 | 100.0 | 51.6 | 0.0 | 100.0 |
| Personal About Page | level 3 (themes and structure) | 33 | 90.9 | 100.0 | 100.0 | 87.9 | 97.0 | 100.0 | 84.8 | 0.0 | 100.0 |
| Personal Blog | level 3 (themes and structure) | 26 | 76.9 | 96.2 | 100.0 | 65.4 | 92.3 | 96.2 | 50.0 | 0.0 | 96.2 |
| User Reviews | level 3 (themes and structure) | 35 | 88.6 | 100.0 | 100.0 | 68.6 | 94.3 | 100.0 | 62.9 | 0.0 | 100.0 |
| Academic Writing | level 4 (themes and full outline) | 27 | 18.5 | 70.4 | 92.6 | 14.8 | 55.6 | 96.3 | 40.7 | 0.0 | 100.0 |
| Creative Writing | level 4 (themes and full outline) | 28 | 21.4 | 67.9 | 92.9 | 3.6 | 39.3 | 85.7 | 14.3 | 0.0 | 96.4 |
| Knowledge Article | level 4 (themes and full outline) | 32 | 34.4 | 81.2 | 100.0 | 15.6 | 50.0 | 100.0 | 34.4 | 0.0 | 100.0 |
| News Article | level 4 (themes and full outline) | 25 | 20.0 | 56.0 | 84.0 | 16.0 | 28.0 | 88.0 | 20.0 | 0.0 | 96.0 |
| Nonfiction Writing | level 4 (themes and full outline) | 31 | 38.7 | 90.3 | 100.0 | 29.0 | 74.2 | 100.0 | 35.5 | 0.0 | 100.0 |
| Personal About Page | level 4 (themes and full outline) | 33 | 27.3 | 84.8 | 93.9 | 21.2 | 57.6 | 93.9 | 39.4 | 0.0 | 100.0 |
| Personal Blog | level 4 (themes and full outline) | 26 | 19.2 | 88.5 | 100.0 | 19.2 | 38.5 | 100.0 | 26.9 | 0.0 | 100.0 |
| User Reviews | level 4 (themes and full outline) | 35 | 8.6 | 60.0 | 94.3 | 8.6 | 40.0 | 97.1 | 22.9 | 0.0 | 94.3 |
| Academic Writing | level 5 (the source's outline) | 27 | 3.7 | 48.1 | 85.2 | 0.0 | 40.7 | 81.5 | 11.1 | 0.0 | 96.3 |
| Creative Writing | level 5 (the source's outline) | 28 | 7.1 | 64.3 | 89.3 | 3.6 | 39.3 | 85.7 | 10.7 | 0.0 | 92.6 |
| Knowledge Article | level 5 (the source's outline) | 32 | 9.4 | 56.2 | 84.4 | 9.4 | 31.2 | 75.0 | 28.1 | 0.0 | 96.9 |
| News Article | level 5 (the source's outline) | 25 | 4.0 | 24.0 | 76.0 | 0.0 | 8.0 | 56.0 | 4.0 | 0.0 | 84.0 |
| Nonfiction Writing | level 5 (the source's outline) | 31 | 16.1 | 74.2 | 100.0 | 16.1 | 61.3 | 93.5 | 25.8 | 0.0 | 96.8 |
| Personal About Page | level 5 (the source's outline) | 33 | 9.1 | 63.6 | 81.8 | 12.1 | 36.4 | 72.7 | 18.2 | 0.0 | 93.9 |
| Personal Blog | level 5 (the source's outline) | 26 | 3.8 | 61.5 | 100.0 | 3.8 | 34.6 | 88.5 | 15.4 | 0.0 | 100.0 |
| User Reviews | level 5 (the source's outline) | 35 | 0.0 | 40.0 | 77.1 | 5.7 | 34.3 | 74.3 | 11.4 | 0.0 | 80.0 |
