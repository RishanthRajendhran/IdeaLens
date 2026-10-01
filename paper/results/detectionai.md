### UChicago DetectionAI: main table

Fire rate % at the 1% cut (global / per-format). TPR on model-idea rows, FPR on human-idea rows.

- IdeaLens-ModernBERT-L on the document is scored on the re-gated set (17,340 documents, 2026-09-14).

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai | model ideas (TPR) | 7,707 | 90.3 / 93.7 | 93.7 / 98.2 | 99.7 / 99.9 | 79.9 / 82.3 | 83.1 / 92.6 | 98.4 / 99.5 | 94.7 / 96.9 | 54.9 / – | 99.8 |
| stealth (humanized) | model ideas (TPR) | 7,706 | 57.9 / 69.3 | 32.4 / 72.9 | 64.1 / 87.3 | 36.6 / 47.6 | 5.7 / 40.3 | 37.7 / 69.7 | 4.9 / 29.4 | 1.8 / – | 94.2 |
| human | human ideas (FPR) | 1,927 | 0.0 / 0.6 | 0.0 / 2.3 | 0.1 / 3.8 | 0.6 / 1.1 | 0.1 / 3.2 | 0.5 / 4.2 | 0.0 / 0.1 | 1.2 / – | 0.0 |
| All model ideas | TPR | 15,413 | 74.1 / 81.5 | 63.0 / 85.6 | 81.9 / 93.6 | 58.3 / 65.0 | 44.4 / 66.4 | 68.1 / 84.6 | 49.8 / 63.2 | 28.4 / – | 97.0 |
| AUC, ai vs human | | | 0.998 | 1.000 | 1.000 | 0.989 | 0.997 | 1.000 | 1.000 | 0.902 | 0.999 |
| AUC, stealth vs human | | | 0.982 | 0.983 | 0.991 | 0.940 | 0.879 | 0.964 | 0.987 | 0.828 | 0.974 |
| AUC, all model ideas vs human | | | 0.990 | 0.991 | 0.996 | 0.965 | 0.938 | 0.982 | 0.994 | 0.865 | 0.986 |

**Length.** Share under 500 words: ai 34.2%, stealth (humanized) 37.9%, human 34.1%, All model ideas 36.0%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai · < 500 | model ideas (TPR) | 2,634 | 76.5 / 83.8 | 81.5 / 94.9 | 99.2 / 99.8 | 58.7 / 63.5 | 53.2 / 83.9 | 95.4 / 98.7 | 92.0 / 95.9 | 27.3 / – | 99.5 |
| ai · >= 500 | model ideas (TPR) | 5,073 | 97.5 / 98.8 | 100.0 / 100.0 | 100.0 / 100.0 | 91.0 / 92.1 | 98.6 / 97.1 | 100.0 / 99.9 | 96.0 / 97.4 | 69.2 / – | 100.0 |
| stealth (humanized) · < 500 | model ideas (TPR) | 2,917 | 47.4 / 56.7 | 27.0 / 58.9 | 64.5 / 81.8 | 31.9 / 38.4 | 6.3 / 34.7 | 38.9 / 60.0 | 11.0 / 37.7 | 3.9 / – | 84.9 |
| stealth (humanized) · >= 500 | model ideas (TPR) | 4,789 | 64.2 / 77.0 | 35.7 / 81.5 | 63.8 / 90.7 | 39.5 / 53.2 | 5.3 / 43.7 | 36.9 / 75.5 | 1.2 / 24.4 | 0.6 / – | 99.9 |
| human · < 500 | human ideas (FPR) | 658 | 0.0 / 1.5 | 0.0 / 6.7 | 0.2 / 11.1 | 1.5 / 2.7 | 0.0 / 8.8 | 1.5 / 12.3 | 0.0 / 0.2 | 3.5 / – | 0.0 |
| human · >= 500 | human ideas (FPR) | 1,269 | 0.0 / 0.1 | 0.0 / 0.0 | 0.0 / 0.0 | 0.1 / 0.2 | 0.1 / 0.3 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / – | 0.0 |
| All model ideas · < 500 | TPR | 5,551 | 61.2 / 69.6 | 52.9 / 76.0 | 81.0 / 90.4 | 44.6 / 50.3 | 28.6 / 58.0 | 65.7 / 78.4 | 49.5 / 65.3 | 15.0 / – | 91.8 |
| All model ideas · >= 500 | TPR | 9,862 | 81.3 / 88.2 | 68.8 / 91.0 | 82.4 / 95.5 | 66.0 / 73.2 | 53.3 / 71.2 | 69.4 / 88.1 | 50.0 / 61.9 | 35.9 / – | 99.9 |

### UChicago DetectionAI: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global / per-format).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| ai | IdeaLens · outline | 73.9 / – | 86.5 / 88.6 | 95.4 / 96.9 | 99.0 / 99.3 |
| ai | IdeaLens · document | 81.2 / – | 88.0 / 96.3 | 98.9 / 99.3 | 100.0 / 100.0 |
| ai | ProseLens | 94.3 / – | 98.4 / 99.8 | 100.0 / 100.0 | 100.0 / 100.0 |
| ai | IdeaLens-ModernBERT-L · outline | 56.6 / – | 73.1 / 74.7 | 87.5 / 90.2 | 96.4 / 97.4 |
| ai | IdeaLens-ModernBERT-L · document | 66.3 / – | 75.1 / 86.2 | 91.5 / 96.8 | 99.6 / 99.5 |
| ai | ProseLens-ModernBERT-L | 87.1 / – | 96.3 / 98.2 | 99.9 / 99.9 | 100.0 / 100.0 |
| ai | EditLens-Llama-3B (cal.) | 0.0 / – | 70.9 / 86.8 | 98.8 / 99.3 | 99.7 / 99.8 |
| ai | Binoculars (cal.) | 22.4 / – | 55.7 / 65.5 | 80.2 / 80.5 | 85.2 / 85.4 |
| stealth (humanized) | IdeaLens · outline | 26.9 / – | 48.4 / 59.0 | 73.4 / 78.5 | 89.4 / 90.7 |
| stealth (humanized) | IdeaLens · document | 7.5 / – | 17.9 / 63.5 | 65.6 / 81.2 | 94.4 / 91.4 |
| stealth (humanized) | ProseLens | 24.2 / – | 44.7 / 78.8 | 87.7 / 93.6 | 99.3 / 98.8 |
| stealth (humanized) | IdeaLens-ModernBERT-L · outline | 12.2 / – | 27.1 / 34.5 | 52.8 / 61.5 | 78.0 / 80.2 |
| stealth (humanized) | IdeaLens-ModernBERT-L · document | 1.8 / – | 3.4 / 27.3 | 16.3 / 56.1 | 63.0 / 73.5 |
| stealth (humanized) | ProseLens-ModernBERT-L | 7.0 / – | 22.7 / 56.0 | 64.9 / 81.1 | 93.1 / 93.0 |
| stealth (humanized) | EditLens-Llama-3B (cal.) | 0.0 / – | 1.0 / 14.9 | 20.9 / 47.9 | 69.4 / 73.2 |
| stealth (humanized) | Binoculars (cal.) | 0.1 / – | 1.9 / 7.7 | 25.2 / 28.6 | 47.7 / 49.9 |
| human | IdeaLens · outline | 0.0 / – | 0.0 / 0.1 | 0.5 / 1.8 | 5.8 / 7.5 |
| human | IdeaLens · document | 0.0 / – | 0.0 / 1.1 | 0.1 / 6.9 | 10.3 / 13.1 |
| human | ProseLens | 0.0 / – | 0.0 / 2.1 | 1.9 / 8.9 | 13.6 / 16.3 |
| human | IdeaLens-ModernBERT-L · outline | 0.0 / – | 0.1 / 0.5 | 1.7 / 3.9 | 8.6 / 11.0 |
| human | IdeaLens-ModernBERT-L · document | 0.0 / – | 0.0 / 0.9 | 0.2 / 9.9 | 13.8 / 19.0 |
| human | ProseLens-ModernBERT-L | 0.0 / – | 0.1 / 2.0 | 2.7 / 7.9 | 13.8 / 16.2 |
| human | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 0.1 | 0.1 / 0.3 | 0.7 / 0.9 |
| human | Binoculars (cal.) | 0.2 / – | 1.2 / 3.3 | 4.8 / 5.7 | 7.9 / 8.1 |
| All model ideas | IdeaLens · outline | 50.4 / – | 67.4 / 73.8 | 84.4 / 87.7 | 94.2 / 95.0 |
| All model ideas | IdeaLens · document | 44.4 / – | 53.0 / 79.9 | 82.2 / 90.3 | 97.2 / 95.7 |
| All model ideas | ProseLens | 59.2 / – | 71.5 / 89.3 | 93.9 / 96.8 | 99.6 / 99.4 |
| All model ideas | IdeaLens-ModernBERT-L · outline | 34.4 / – | 50.1 / 54.6 | 70.1 / 75.9 | 87.2 / 88.8 |
| All model ideas | IdeaLens-ModernBERT-L · document | 34.1 / – | 39.3 / 56.7 | 53.9 / 76.5 | 81.3 / 86.5 |
| All model ideas | ProseLens-ModernBERT-L | 47.1 / – | 59.5 / 77.1 | 82.4 / 90.5 | 96.6 / 96.5 |
| All model ideas | EditLens-Llama-3B (cal.) | 0.0 / – | 36.0 / 50.9 | 59.8 / 73.6 | 84.5 / 86.5 |
| All model ideas | Binoculars (cal.) | 11.3 / – | 28.8 / 36.6 | 52.7 / 54.6 | 66.5 / 67.7 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-opus-4-20250514 | ai | 1,927 | 83.7 / 89.5 | 92.7 / 97.7 | 99.7 / 99.9 | 65.9 / 71.7 | 77.4 / 90.9 | 98.0 / 99.7 | 89.1 / 96.2 | 19.1 / – | 100.0 |
| claude-sonnet-4-20250514 | ai | 1,927 | 91.2 / 94.7 | 93.8 / 98.2 | 99.8 / 99.9 | 78.6 / 81.8 | 82.4 / 91.4 | 99.1 / 99.8 | 95.8 / 97.6 | 44.3 / – | 99.9 |
| gemini-2.0-flash | ai | 1,926 | 90.3 / 93.2 | 93.1 / 98.4 | 99.6 / 99.9 | 83.9 / 84.8 | 84.0 / 93.5 | 97.9 / 99.2 | 95.0 / 96.1 | 81.3 / – | 99.5 |
| gpt-4.1-2025-04-14 | ai | 1,927 | 95.8 / 97.3 | 95.0 / 98.6 | 99.9 / 100.0 | 91.3 / 90.8 | 88.4 / 94.6 | 98.8 / 99.3 | 98.9 / 97.8 | 74.8 / – | 99.9 |
| claude-opus-4-20250514 | stealth (humanized) | 1,927 | 47.8 / 61.6 | 26.5 / 70.3 | 52.2 / 83.8 | 21.2 / 31.2 | 2.4 / 27.5 | 28.2 / 65.5 | 4.9 / 24.5 | 0.9 / – | 93.5 |
| claude-sonnet-4-20250514 | stealth (humanized) | 1,925 | 57.4 / 70.1 | 27.3 / 71.8 | 61.7 / 87.1 | 31.1 / 41.5 | 3.3 / 34.0 | 34.9 / 69.0 | 3.8 / 27.8 | 0.7 / – | 94.9 |
| gemini-2.0-flash | stealth (humanized) | 1,927 | 65.4 / 74.3 | 42.0 / 77.4 | 72.1 / 89.8 | 46.9 / 58.8 | 8.3 / 51.0 | 49.5 / 74.1 | 5.1 / 31.2 | 3.2 / – | 93.5 |
| gpt-4.1-2025-04-14 | stealth (humanized) | 1,927 | 60.8 / 71.3 | 33.8 / 72.2 | 70.4 / 88.6 | 47.3 / 59.0 | 8.8 / 48.7 | 38.1 / 70.1 | 5.9 / 34.0 | 2.5 / – | 94.9 |
| human | human | 1,927 | 0.0 / 0.6 | 0.0 / 2.3 | 0.1 / 3.8 | 0.6 / 1.1 | 0.1 / 3.2 | 0.5 / 4.2 | 0.0 / 0.1 | 1.2 / – | 0.0 |

**By genre.** Fire rate % at the 1% cut.

| Genre | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| amazon review | ai | 700 | 66.0 / 74.3 | 68.1 / 90.7 | 99.3 / 99.7 | 48.4 / 54.3 | 40.1 / 75.3 | 93.9 / 98.3 | 90.1 / 93.9 | 15.4 / – | 99.6 |
| blog | ai | 796 | 69.1 / 84.9 | 84.7 / 99.6 | 99.1 / 100.0 | 40.7 / 52.8 | 37.9 / 92.6 | 95.7 / 99.7 | 91.3 / 97.5 | 19.2 / – | 99.2 |
| news | ai | 1,068 | 95.2 / 93.1 | 96.0 / 94.8 | 99.9 / 99.8 | 88.1 / 80.8 | 90.0 / 86.2 | 99.3 / 98.3 | 99.0 / 93.4 | 52.2 / – | 100.0 |
| novel | ai | 3,999 | 97.1 / 98.9 | 100.0 / 100.0 | 100.0 / 100.0 | 90.5 / 94.6 | 98.7 / 99.9 | 100.0 / 100.0 | 95.1 / 98.6 | 65.2 / – | 100.0 |
| restaurant review | ai | 380 | 74.5 / 82.9 | 73.7 / 97.1 | 98.2 / 100.0 | 56.6 / 64.7 | 42.4 / 80.5 | 90.3 / 99.2 | 83.2 / 95.5 | 31.8 / – | 98.9 |
| resume | ai | 764 | 100.0 / 99.5 | 100.0 / 99.9 | 100.0 / 100.0 | 94.5 / 85.1 | 97.8 / 84.8 | 100.0 / 99.6 | 99.9 / 95.9 | 89.3 / – | 100.0 |
| amazon review | stealth (humanized) | 700 | 30.9 / 41.1 | 13.4 / 48.7 | 53.3 / 81.3 | 18.4 / 25.3 | 4.1 / 26.9 | 29.4 / 56.6 | 11.4 / 42.6 | 6.0 / – | 75.3 |
| blog | stealth (humanized) | 795 | 41.6 / 63.8 | 32.7 / 86.0 | 61.5 / 94.2 | 18.0 / 32.2 | 3.5 / 53.0 | 48.7 / 82.1 | 15.1 / 55.1 | 1.9 / – | 78.4 |
| news | stealth (humanized) | 1,067 | 59.1 / 51.8 | 27.1 / 22.4 | 72.1 / 57.0 | 48.4 / 41.5 | 7.3 / 9.6 | 33.8 / 24.6 | 4.4 / 5.9 | 1.1 / – | 98.3 |
| novel | stealth (humanized) | 4,000 | 62.7 / 79.2 | 36.5 / 91.1 | 61.2 / 95.7 | 40.2 / 56.7 | 6.7 / 54.0 | 40.4 / 87.3 | 1.5 / 28.7 | 0.8 / – | 99.8 |
| restaurant review | stealth (humanized) | 380 | 44.2 / 58.9 | 21.6 / 69.2 | 58.4 / 88.7 | 25.8 / 32.9 | 3.4 / 33.2 | 37.6 / 72.4 | 11.6 / 49.7 | 8.2 / – | 79.5 |
| resume | stealth (humanized) | 764 | 79.1 / 79.1 | 40.8 / 58.9 | 83.5 / 83.4 | 43.1 / 52.2 | 2.9 / 13.6 | 25.0 / 37.8 | 4.1 / 16.8 | 1.3 / – | 100.0 |
| amazon review | human | 175 | 0.0 / 1.7 | 0.0 / 5.7 | 0.6 / 13.7 | 1.7 / 1.7 | 0.0 / 4.6 | 1.7 / 13.1 | 0.0 / 0.6 | 5.7 / – | 0.0 |
| blog | human | 199 | 0.0 / 3.5 | 0.0 / 17.1 | 0.0 / 21.6 | 2.5 / 6.0 | 0.0 / 22.1 | 3.0 / 26.1 | 0.0 / 0.0 | 5.0 / – | 0.0 |
| news | human | 267 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.4 | 0.4 / 0.4 | 0.0 / 0.4 | 0.0 / 0.4 | 0.0 / 0.0 | 0.4 / – | 0.0 |
| novel | human | 1,000 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.1 / 0.3 | 0.0 / 0.2 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / – | 0.0 |
| restaurant review | human | 95 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 5.3 | 1.1 / 2.1 | 0.0 / 5.3 | 1.1 / 5.3 | 0.0 / 0.0 | 2.1 / – | 0.0 |
| resume | human | 191 | 0.0 / 0.5 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.5 / 1.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / – | 0.0 |
