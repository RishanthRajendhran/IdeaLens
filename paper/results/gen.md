### AI Writers/Editors (GEN): main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- A person's document revised by a model keeps the person's ideas, so model-edited rows are false positives. adding_detail edits add new model content: mixed, human-leaning, shown as its own row (a fire rate, neither TPR nor FPR).
- Re-gated set, by document id. The 67 documents the re-gate added are scored on the raw outline.
- Reasoning trace (found and fixed 2026-09-14): 4,395 gpt-oss-120B / 20B documents open with a leaked 'analysis...' reasoning trace in the released text. Our models (IdeaLens, IdeaLens-ModernBERT-L, IdeaLens-Qwen3.5-9B, IdeaLens-LogisticClassifier; outline and document) read the stripped text of the 4,339 with a clean 'assistantfinal' boundary (re-gated and re-extracted); the 56 without one are excluded from every column; EditLens-Llama-3B, Binoculars and Pangram 4 read the text as released.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean human | human ideas (FPR) | 3,055 | 0.5 | 0.0 | 0.0 | 0.9 | 0.0 | 0.2 | 0.0 | 0.1 | 0.0 |
| clean AI (model-written) | model ideas (TPR) | 4,046 | 95.8 | 98.4 | 99.7 | 83.4 | 72.8 | 98.9 | 70.9 | 19.6 | 99.8 |
| model-edited (7 categories, adding_detail excluded) | human ideas, AI prose (FPR) | 14,086 | 14.0 | 26.3 | 59.9 | 10.7 | 17.3 | 45.4 | 33.7 | 23.6 | 56.8 |
| adding_detail (model-edited) | mixed, human-leaning (fire rate) | 1,915 | 36.4 | 75.2 | 93.6 | 27.3 | 50.5 | 83.7 | 46.4 | 56.3 | 67.5 |
| AUC, clean AI vs clean human | | | 0.992 | 0.997 | 1.000 | 0.983 | 0.983 | 1.000 | 1.000 | 0.693 | 1.000 |
| AUC, clean AI vs clean human + model-edited | | | 0.978 | 0.979 | 0.965 | 0.944 | 0.889 | 0.931 | 0.791 | 0.411 | 0.961 |

**Length.** Share under 500 words: clean human 66.4%, clean AI (model-written) 7.8%, model-edited (7 categories, adding_detail excluded) 74.0%, adding_detail (model-edited) 21.6%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean human · < 500 | human ideas (FPR) | 2,027 | 0.3 | 0.0 | 0.0 | 0.5 | 0.0 | 0.2 | 0.0 | 0.1 | 0.0 |
| clean human · >= 500 | human ideas (FPR) | 1,028 | 0.9 | 0.0 | 0.0 | 1.5 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 |
| clean AI (model-written) · < 500 | model ideas (TPR) | 314 | 81.2 | 83.1 | 96.2 | 59.2 | 12.4 | 88.5 | 49.7 | 0.0 | 98.1 |
| clean AI (model-written) · >= 500 | model ideas (TPR) | 3,732 | 97.0 | 99.7 | 99.9 | 85.4 | 77.9 | 99.8 | 72.7 | 21.3 | 100.0 |
| model-edited (7 categories, adding_detail excluded) · < 500 | human ideas, AI prose (FPR) | 10,420 | 13.5 | 23.7 | 59.6 | 9.9 | 14.9 | 43.2 | 35.1 | 21.5 | 62.1 |
| model-edited (7 categories, adding_detail excluded) · >= 500 | human ideas, AI prose (FPR) | 3,666 | 15.6 | 33.9 | 60.8 | 12.9 | 24.1 | 51.8 | 29.7 | 29.3 | 41.8 |
| adding_detail (model-edited) · < 500 | mixed, human-leaning (fire rate) | 414 | 44.5 | 72.0 | 95.2 | 31.6 | 47.3 | 83.8 | 66.9 | 61.6 | 69.1 |
| adding_detail (model-edited) · >= 500 | mixed, human-leaning (fire rate) | 1,501 | 34.1 | 76.1 | 93.2 | 26.0 | 51.4 | 83.6 | 40.8 | 54.8 | 67.0 |

### AI Writers/Editors (GEN): appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| clean human | IdeaLens · outline | 0.1 | 0.4 | 1.0 | 3.1 |
| clean human | IdeaLens · document | 0.0 | 0.0 | 0.0 | 0.6 |
| clean human | ProseLens | 0.0 | 0.0 | 0.0 | 0.3 |
| clean human | IdeaLens-ModernBERT-L · outline | 0.1 | 0.4 | 2.3 | 8.1 |
| clean human | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 0.3 | 10.9 |
| clean human | ProseLens-ModernBERT-L | 0.0 | 0.0 | 0.8 | 8.7 |
| clean human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.0 | 0.4 |
| clean human | Binoculars (cal.) | 0.0 | 0.1 | 2.3 | 7.0 |
| clean AI (model-written) | IdeaLens · outline | 89.7 | 94.7 | 97.4 | 98.2 |
| clean AI (model-written) | IdeaLens · document | 95.8 | 98.0 | 98.7 | 99.0 |
| clean AI (model-written) | ProseLens | 98.9 | 99.3 | 99.9 | 100.0 |
| clean AI (model-written) | IdeaLens-ModernBERT-L · outline | 58.8 | 76.1 | 90.6 | 95.7 |
| clean AI (model-written) | IdeaLens-ModernBERT-L · document | 61.9 | 68.4 | 82.0 | 95.2 |
| clean AI (model-written) | ProseLens-ModernBERT-L | 87.7 | 96.7 | 99.7 | 99.9 |
| clean AI (model-written) | EditLens-Llama-3B (cal.) | 0.0 | 28.8 | 93.4 | 99.3 |
| clean AI (model-written) | Binoculars (cal.) | 8.6 | 20.0 | 29.9 | 36.7 |
| model-edited (7 categories, adding_detail excluded) | IdeaLens · outline | 3.9 | 10.6 | 20.7 | 29.8 |
| model-edited (7 categories, adding_detail excluded) | IdeaLens · document | 11.6 | 19.7 | 37.6 | 50.6 |
| model-edited (7 categories, adding_detail excluded) | ProseLens | 44.4 | 53.6 | 68.8 | 81.7 |
| model-edited (7 categories, adding_detail excluded) | IdeaLens-ModernBERT-L · outline | 2.3 | 6.7 | 18.8 | 34.0 |
| model-edited (7 categories, adding_detail excluded) | IdeaLens-ModernBERT-L · document | 6.5 | 11.5 | 30.3 | 60.2 |
| model-edited (7 categories, adding_detail excluded) | ProseLens-ModernBERT-L | 16.9 | 32.4 | 64.5 | 86.7 |
| model-edited (7 categories, adding_detail excluded) | EditLens-Llama-3B (cal.) | 0.0 | 13.9 | 55.7 | 82.9 |
| model-edited (7 categories, adding_detail excluded) | Binoculars (cal.) | 7.6 | 24.1 | 48.7 | 62.3 |
| adding_detail (model-edited) | IdeaLens · outline | 15.4 | 30.5 | 45.6 | 57.0 |
| adding_detail (model-edited) | IdeaLens · document | 46.7 | 65.6 | 85.4 | 92.7 |
| adding_detail (model-edited) | ProseLens | 86.0 | 91.3 | 95.8 | 97.4 |
| adding_detail (model-edited) | IdeaLens-ModernBERT-L · outline | 5.8 | 19.2 | 40.1 | 58.1 |
| adding_detail (model-edited) | IdeaLens-ModernBERT-L · document | 20.3 | 35.7 | 70.5 | 87.4 |
| adding_detail (model-edited) | ProseLens-ModernBERT-L | 37.9 | 70.3 | 92.4 | 97.0 |
| adding_detail (model-edited) | EditLens-Llama-3B (cal.) | 0.0 | 24.2 | 69.6 | 91.0 |
| adding_detail (model-edited) | Binoculars (cal.) | 19.5 | 57.0 | 83.6 | 88.9 |

**By edit category.** Fire rate % at the 1% cut.

| Edit category | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clarity_and_precision | model-edited (7 categories, adding_detail excluded) | 2,155 | 24.4 | 38.6 | 79.1 | 18.4 | 27.3 | 63.6 | 54.0 | 32.3 | 73.7 |
| concision | model-edited (7 categories, adding_detail excluded) | 1,946 | 9.5 | 17.7 | 56.1 | 6.2 | 8.5 | 39.6 | 18.8 | 18.5 | 55.4 |
| fluency_and_flow | model-edited (7 categories, adding_detail excluded) | 2,059 | 11.7 | 23.1 | 61.2 | 9.2 | 15.9 | 46.1 | 33.8 | 24.7 | 61.0 |
| grammar_and_mechanics | model-edited (7 categories, adding_detail excluded) | 1,678 | 0.7 | 0.3 | 6.6 | 1.0 | 0.3 | 4.5 | 1.0 | 2.4 | 4.1 |
| paraphrasing | model-edited (7 categories, adding_detail excluded) | 2,011 | 4.4 | 7.0 | 46.9 | 3.7 | 4.7 | 30.8 | 21.9 | 18.9 | 63.1 |
| structure_and_organization | model-edited (7 categories, adding_detail excluded) | 2,243 | 25.4 | 36.2 | 76.7 | 18.3 | 23.5 | 60.8 | 56.4 | 31.9 | 65.1 |
| tone_and_style | model-edited (7 categories, adding_detail excluded) | 1,994 | 17.9 | 55.4 | 80.6 | 14.9 | 36.4 | 62.9 | 40.0 | 31.0 | 64.2 |
| adding_detail | adding_detail (model-edited) | 1,915 | 36.4 | 75.2 | 93.6 | 27.3 | 50.5 | 83.7 | 46.4 | 56.3 | 67.5 |

**By target ratio.** Fire rate % at the 1% cut.

| Target ratio | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 30 | model-edited (7 categories, adding_detail excluded) | 4,166 | 6.8 | 13.9 | 40.9 | 5.0 | 8.4 | 29.4 | 16.4 | 12.5 | 36.8 |
| 50 | model-edited (7 categories, adding_detail excluded) | 2,410 | 9.3 | 20.8 | 55.4 | 7.2 | 13.2 | 39.4 | 22.9 | 14.4 | 53.8 |
| 70 | model-edited (7 categories, adding_detail excluded) | 7,510 | 19.5 | 35.0 | 71.9 | 14.9 | 23.6 | 56.3 | 46.7 | 32.6 | 68.9 |
| 30 | adding_detail (model-edited) | 351 | 21.3 | 53.0 | 77.8 | 16.0 | 35.0 | 60.1 | 28.8 | 37.0 | 45.0 |
| 50 | adding_detail (model-edited) | 400 | 30.2 | 69.8 | 96.0 | 20.2 | 39.2 | 84.8 | 38.2 | 44.8 | 69.8 |
| 70 | adding_detail (model-edited) | 1,164 | 42.9 | 83.8 | 97.6 | 33.0 | 59.0 | 90.4 | 54.6 | 66.1 | 73.5 |

**By editor or generator.** Fire rate % at the 1% cut.

| Editor or generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma3-12B | clean AI (model-written) | 745 | 99.5 | 100.0 | 100.0 | 89.7 | 98.4 | 100.0 | 80.4 | 0.0 | 100.0 |
| gemma3-27B | clean AI (model-written) | 742 | 100.0 | 100.0 | 100.0 | 87.2 | 98.5 | 100.0 | 68.5 | 0.0 | 100.0 |
| gpt-oss-120B | clean AI (model-written) | 532 | 95.1 | 99.8 | 100.0 | 61.3 | 83.3 | 98.9 | 74.8 | 73.9 | 100.0 |
| gpt-oss-20B | clean AI (model-written) | 372 | 83.1 | 85.5 | 96.8 | 61.3 | 17.2 | 90.1 | 49.5 | 0.0 | 98.4 |
| llama3.1-8B | clean AI (model-written) | 347 | 93.1 | 99.7 | 99.7 | 87.0 | 41.5 | 100.0 | 51.6 | 0.0 | 100.0 |
| llama3.3-70B | clean AI (model-written) | 338 | 95.6 | 99.1 | 99.7 | 90.2 | 72.5 | 99.4 | 74.0 | 20.4 | 99.7 |
| qwen2.5-72B | clean AI (model-written) | 562 | 98.6 | 99.8 | 100.0 | 96.3 | 85.9 | 100.0 | 91.3 | 58.7 | 100.0 |
| qwen2.5-7B | clean AI (model-written) | 408 | 92.6 | 99.3 | 100.0 | 87.3 | 25.0 | 100.0 | 58.3 | 0.5 | 100.0 |
| gpt-oss-120B | model-edited (7 categories, adding_detail excluded) | 3,826 | 8.9 | 16.5 | 54.8 | 6.8 | 11.1 | 40.0 | 13.5 | 1.6 | 56.5 |
| llama3.3-70B | model-edited (7 categories, adding_detail excluded) | 5,175 | 16.4 | 31.1 | 65.5 | 12.4 | 20.1 | 49.7 | 41.7 | 32.7 | 57.2 |
| qwen2.5-72B | model-edited (7 categories, adding_detail excluded) | 5,085 | 15.4 | 28.9 | 58.1 | 11.8 | 19.1 | 45.1 | 40.6 | 30.8 | 56.6 |
| gpt-oss-120B | adding_detail (model-edited) | 513 | 26.5 | 60.0 | 91.8 | 15.8 | 34.1 | 81.9 | 20.7 | 19.7 | 86.0 |
| llama3.3-70B | adding_detail (model-edited) | 673 | 37.0 | 79.8 | 93.8 | 28.7 | 55.9 | 81.1 | 49.2 | 64.3 | 53.5 |
| qwen2.5-72B | adding_detail (model-edited) | 729 | 42.4 | 81.8 | 94.8 | 33.6 | 57.1 | 87.2 | 62.0 | 74.6 | 67.4 |

**By domain.** Fire rate % at the 1% cut.

| Domain | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| arxiv | clean human | 1,000 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.3 | 0.0 | 0.0 | 0.0 |
| reddit | clean human | 55 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| story_generation | clean human | 998 | 1.4 | 0.0 | 0.0 | 2.5 | 0.0 | 0.3 | 0.0 | 0.1 | 0.0 |
| wikihow | clean human | 10 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| wikipedia | clean human | 992 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 |
| arxiv | clean AI (model-written) | 81 | 19.8 | 37.0 | 85.2 | 24.7 | 17.3 | 64.2 | 23.5 | 0.0 | 92.6 |
| reddit | clean AI (model-written) | 335 | 94.9 | 99.1 | 99.4 | 81.5 | 64.2 | 99.4 | 77.0 | 30.4 | 100.0 |
| story_generation | clean AI (model-written) | 3,212 | 98.5 | 99.8 | 100.0 | 88.4 | 75.9 | 99.8 | 70.9 | 16.5 | 100.0 |
| wikipedia | clean AI (model-written) | 418 | 90.2 | 99.3 | 100.0 | 57.2 | 66.7 | 98.6 | 75.6 | 39.0 | 100.0 |
| arxiv | model-edited (7 categories, adding_detail excluded) | 3,988 | 4.2 | 12.8 | 40.8 | 2.5 | 5.7 | 25.4 | 22.4 | 3.1 | 62.9 |
| reddit | model-edited (7 categories, adding_detail excluded) | 2,413 | 15.1 | 24.7 | 83.5 | 8.8 | 12.6 | 58.8 | 56.9 | 39.8 | 81.0 |
| story_generation | model-edited (7 categories, adding_detail excluded) | 3,946 | 19.9 | 36.9 | 73.1 | 19.7 | 26.8 | 66.3 | 28.7 | 34.4 | 52.2 |
| wikihow | model-edited (7 categories, adding_detail excluded) | 300 | 13.7 | 27.7 | 75.7 | 8.9 | 21.0 | 55.3 | 53.3 | 41.7 | 75.0 |
| wikipedia | model-edited (7 categories, adding_detail excluded) | 3,439 | 18.0 | 30.9 | 49.1 | 11.3 | 22.9 | 34.4 | 34.4 | 21.9 | 36.6 |
| arxiv | adding_detail (model-edited) | 555 | 30.3 | 57.3 | 95.7 | 23.6 | 38.0 | 82.7 | 52.3 | 43.8 | 72.6 |
| reddit | adding_detail (model-edited) | 331 | 41.7 | 78.5 | 92.7 | 23.2 | 39.3 | 81.9 | 61.6 | 65.6 | 70.4 |
| story_generation | adding_detail (model-edited) | 571 | 34.7 | 82.1 | 92.3 | 32.1 | 56.9 | 87.0 | 25.4 | 59.5 | 62.7 |
| wikihow | adding_detail (model-edited) | 58 | 45.5 | 84.5 | 91.4 | 32.7 | 56.9 | 82.8 | 58.6 | 56.9 | 74.1 |
| wikipedia | adding_detail (model-edited) | 400 | 41.7 | 86.2 | 93.8 | 28.0 | 67.0 | 81.8 | 54.0 | 61.3 | 63.7 |

**By human draw.** Fire rate % at the 1% cut.

| Human draw | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| original draw | clean human | 1,081 | 0.8 | 0.0 | 0.0 | 1.4 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 |
| rebuild | clean human | 1,974 | 0.3 | 0.0 | 0.0 | 0.6 | 0.0 | 0.3 | 0.0 | 0.1 | 0.0 |

**Other model x input columns.** Fire rate % at the 1% cut.

| Arm | n | ProseLens · raw outline |
|---|---|---|
| clean human | 3,055 | 57.3 |
| clean AI (model-written) | 4,046 | 99.6 |
| model-edited (7 categories, adding_detail excluded) | 14,086 | 75.0 |
| adding_detail (model-edited) | 1,915 | 89.2 |
