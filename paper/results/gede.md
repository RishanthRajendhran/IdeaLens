### GEDE: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Ordered by the student's contribution: the student's essay; a model improving or rewriting it; a model writing from a summary of it (with or without the assignment); a model given only the assignment; evasion attacks on generated text.
- summary and task+summary follow GEDE's own boundary (LLM-generated): a summary carries only the gist. Every document is under 500 words.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| human | human ideas (FPR) | 915 | 0.1 | 0.0 | 0.0 | 1.5 | 0.0 | 0.9 | 0.0 | 0.1 | 0.0 |
| model rewrites of the student's essay (improve-human, rewrite-human) | human ideas, AI prose (FPR) | 3,648 | 1.6 | 1.1 | 61.5 | 4.2 | 2.0 | 46.0 | 28.6 | 14.6 | 74.5 |
| task (assignment only; task, task+resource) | model ideas (TPR) | 1,870 | 99.4 | 99.9 | 100.0 | 93.3 | 98.9 | 100.0 | 100.0 | 96.7 | 100.0 |
| from the student's summary (summary, task+summary) | model ideas (TPR) | 3,550 | 94.8 | 99.5 | 100.0 | 86.3 | 94.3 | 100.0 | 100.0 | 91.8 | 99.9 |
| attacks (dipper, rewrite_attack) | model ideas (TPR) | 3,604 | 88.7 | 76.6 | 98.6 | 81.1 | 67.9 | 83.3 | 60.7 | 87.3 | 97.6 |
| AUC, model ideas vs human | | | 0.999 | 1.000 | 1.000 | 0.988 | 0.999 | 0.998 | 0.997 | 0.999 | 0.996 |
| AUC, model ideas vs human + rewrites | | | 0.995 | 0.996 | 0.966 | 0.978 | 0.984 | 0.915 | 0.891 | 0.958 | 0.983 |

**Length.** Share under 500 words: human 100.0%, model rewrites of the student's essay (improve-human, rewrite-human) 100.0%, task (assignment only; task, task+resource) 100.0%, from the student's summary (summary, task+summary) 100.0%, attacks (dipper, rewrite_attack) 100.0%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| human · < 500 | human ideas (FPR) | 915 | 0.1 | 0.0 | 0.0 | 1.5 | 0.0 | 0.9 | 0.0 | 0.1 | 0.0 |
| model rewrites of the student's essay (improve-human, rewrite-human) · < 500 | human ideas, AI prose (FPR) | 3,648 | 1.6 | 1.1 | 61.5 | 4.2 | 2.0 | 46.0 | 28.6 | 14.6 | 74.5 |
| task (assignment only; task, task+resource) · < 500 | model ideas (TPR) | 1,870 | 99.4 | 99.9 | 100.0 | 93.3 | 98.9 | 100.0 | 100.0 | 96.7 | 100.0 |
| from the student's summary (summary, task+summary) · < 500 | model ideas (TPR) | 3,550 | 94.8 | 99.5 | 100.0 | 86.3 | 94.3 | 100.0 | 100.0 | 91.8 | 99.9 |
| attacks (dipper, rewrite_attack) · < 500 | model ideas (TPR) | 3,604 | 88.7 | 76.6 | 98.6 | 81.1 | 67.9 | 83.3 | 60.7 | 87.3 | 97.6 |

### GEDE: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| human | IdeaLens · outline | 0.0 | 0.0 | 0.7 | 6.1 |
| human | IdeaLens · document | 0.0 | 0.0 | 0.0 | 7.4 |
| human | ProseLens | 0.0 | 0.0 | 0.4 | 29.7 |
| human | IdeaLens-ModernBERT-L · outline | 0.0 | 0.5 | 5.6 | 19.9 |
| human | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 0.2 | 8.6 |
| human | ProseLens-ModernBERT-L | 0.0 | 0.0 | 4.0 | 29.1 |
| human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.0 | 0.4 |
| human | Binoculars (cal.) | 0.0 | 0.1 | 3.0 | 9.2 |
| model rewrites of the student's essay (improve-human, rewrite-human) | IdeaLens · outline | 0.0 | 0.7 | 5.2 | 16.9 |
| model rewrites of the student's essay (improve-human, rewrite-human) | IdeaLens · document | 0.0 | 0.2 | 6.1 | 34.9 |
| model rewrites of the student's essay (improve-human, rewrite-human) | ProseLens | 13.8 | 41.8 | 84.5 | 99.2 |
| model rewrites of the student's essay (improve-human, rewrite-human) | IdeaLens-ModernBERT-L · outline | 0.3 | 1.7 | 11.4 | 28.9 |
| model rewrites of the student's essay (improve-human, rewrite-human) | IdeaLens-ModernBERT-L · document | 0.0 | 0.5 | 9.7 | 46.9 |
| model rewrites of the student's essay (improve-human, rewrite-human) | ProseLens-ModernBERT-L | 5.5 | 28.9 | 69.9 | 95.6 |
| model rewrites of the student's essay (improve-human, rewrite-human) | EditLens-Llama-3B (cal.) | 0.0 | 8.1 | 64.3 | 91.9 |
| model rewrites of the student's essay (improve-human, rewrite-human) | Binoculars (cal.) | 2.8 | 15.1 | 48.8 | 65.3 |
| task (assignment only; task, task+resource) | IdeaLens · outline | 42.6 | 96.1 | 99.9 | 100.0 |
| task (assignment only; task, task+resource) | IdeaLens · document | 77.1 | 99.1 | 100.0 | 100.0 |
| task (assignment only; task, task+resource) | ProseLens | 100.0 | 100.0 | 100.0 | 100.0 |
| task (assignment only; task, task+resource) | IdeaLens-ModernBERT-L · outline | 27.6 | 79.1 | 98.3 | 99.8 |
| task (assignment only; task, task+resource) | IdeaLens-ModernBERT-L · document | 31.8 | 87.4 | 99.9 | 100.0 |
| task (assignment only; task, task+resource) | ProseLens-ModernBERT-L | 84.0 | 99.7 | 100.0 | 100.0 |
| task (assignment only; task, task+resource) | EditLens-Llama-3B (cal.) | 0.0 | 99.9 | 100.0 | 100.0 |
| task (assignment only; task, task+resource) | Binoculars (cal.) | 77.9 | 96.8 | 99.7 | 100.0 |
| from the student's summary (summary, task+summary) | IdeaLens · outline | 35.9 | 83.6 | 99.1 | 99.9 |
| from the student's summary (summary, task+summary) | IdeaLens · document | 44.7 | 93.3 | 100.0 | 100.0 |
| from the student's summary (summary, task+summary) | ProseLens | 100.0 | 100.0 | 100.0 | 100.0 |
| from the student's summary (summary, task+summary) | IdeaLens-ModernBERT-L · outline | 22.9 | 66.9 | 95.6 | 99.4 |
| from the student's summary (summary, task+summary) | IdeaLens-ModernBERT-L · document | 23.6 | 75.4 | 99.4 | 100.0 |
| from the student's summary (summary, task+summary) | ProseLens-ModernBERT-L | 70.4 | 99.2 | 100.0 | 100.0 |
| from the student's summary (summary, task+summary) | EditLens-Llama-3B (cal.) | 0.0 | 99.5 | 100.0 | 100.0 |
| from the student's summary (summary, task+summary) | Binoculars (cal.) | 61.8 | 92.3 | 99.4 | 99.8 |
| attacks (dipper, rewrite_attack) | IdeaLens · outline | 31.7 | 77.2 | 96.6 | 99.5 |
| attacks (dipper, rewrite_attack) | IdeaLens · document | 34.8 | 59.0 | 95.8 | 99.9 |
| attacks (dipper, rewrite_attack) | ProseLens | 71.8 | 94.3 | 99.9 | 100.0 |
| attacks (dipper, rewrite_attack) | IdeaLens-ModernBERT-L · outline | 20.3 | 61.8 | 94.0 | 98.8 |
| attacks (dipper, rewrite_attack) | IdeaLens-ModernBERT-L · document | 14.7 | 50.7 | 85.9 | 99.4 |
| attacks (dipper, rewrite_attack) | ProseLens-ModernBERT-L | 42.6 | 68.7 | 96.4 | 100.0 |
| attacks (dipper, rewrite_attack) | EditLens-Llama-3B (cal.) | 0.0 | 52.9 | 71.7 | 83.9 |
| attacks (dipper, rewrite_attack) | Binoculars (cal.) | 43.1 | 88.0 | 99.2 | 99.7 |

**By arm.** Fire rate % at the 1% cut.

| Arm | Description | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| human | human | 915 | 0.1 | 0.0 | 0.0 | 1.5 | 0.0 | 0.9 | 0.0 | 0.1 | 0.0 |
| improve-human | model rewrites of the student's essay (improve-human, rewrite-human) | 1,818 | 0.5 | 0.1 | 45.8 | 2.4 | 0.4 | 31.2 | 7.8 | 5.4 | 54.6 |
| rewrite-human | model rewrites of the student's essay (improve-human, rewrite-human) | 1,830 | 2.6 | 2.0 | 77.1 | 6.0 | 3.7 | 60.6 | 49.3 | 23.8 | 94.3 |
| task | task (assignment only; task, task+resource) | 1,830 | 99.5 | 99.9 | 100.0 | 93.2 | 98.9 | 100.0 | 100.0 | 97.4 | 100.0 |
| task+resource | task (assignment only; task, task+resource) | 40 | 95.0 | 100.0 | 100.0 | 95.0 | 100.0 | 100.0 | 100.0 | 67.5 | 100.0 |
| summary | from the student's summary (summary, task+summary) | 1,775 | 96.2 | 99.9 | 100.0 | 88.6 | 96.8 | 100.0 | 100.0 | 92.7 | 100.0 |
| task+summary | from the student's summary (summary, task+summary) | 1,775 | 93.5 | 99.2 | 100.0 | 83.9 | 91.9 | 100.0 | 100.0 | 90.8 | 99.8 |
| dipper | attacks (dipper, rewrite_attack) | 1,773 | 77.6 | 52.6 | 97.1 | 68.1 | 36.3 | 66.0 | 20.0 | 79.3 | 95.1 |
| rewrite_attack | attacks (dipper, rewrite_attack) | 1,831 | 99.6 | 99.9 | 100.0 | 93.7 | 98.5 | 100.0 | 100.0 | 95.1 | 100.0 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-4o-mini-2024-07-18 | model rewrites of the student's essay (improve-human, rewrite-human) | 1,831 | 0.7 | 0.1 | 61.6 | 3.1 | 0.5 | 44.5 | 27.3 | 4.4 | 80.4 |
| meta-llama/Llama-3.3-70B-Instruct | model rewrites of the student's essay (improve-human, rewrite-human) | 1,817 | 2.4 | 2.1 | 61.4 | 5.3 | 3.5 | 47.4 | 29.9 | 24.9 | 68.5 |
| gpt-4o-mini-2024-07-18 | task (assignment only; task, task+resource) | 934 | 99.9 | 100.0 | 100.0 | 94.8 | 98.9 | 100.0 | 100.0 | 93.7 | 100.0 |
| meta-llama/Llama-3.3-70B-Instruct | task (assignment only; task, task+resource) | 936 | 98.8 | 99.9 | 100.0 | 91.8 | 98.9 | 100.0 | 100.0 | 99.8 | 100.0 |
| gpt-4o-mini-2024-07-18 | from the student's summary (summary, task+summary) | 1,776 | 97.6 | 100.0 | 100.0 | 89.7 | 96.3 | 100.0 | 100.0 | 84.1 | 100.0 |
| meta-llama/Llama-3.3-70B-Instruct | from the student's summary (summary, task+summary) | 1,774 | 92.1 | 99.1 | 100.0 | 82.9 | 92.3 | 100.0 | 100.0 | 99.5 | 99.8 |
| dipper | attacks (dipper, rewrite_attack) | 1,773 | 77.6 | 52.6 | 97.1 | 68.1 | 36.3 | 66.0 | 20.0 | 79.3 | 95.1 |
| gpt-4o-mini-2024-07-18 | attacks (dipper, rewrite_attack) | 916 | 99.3 | 99.9 | 100.0 | 93.1 | 98.4 | 100.0 | 100.0 | 96.1 | 100.0 |
| meta-llama/Llama-3.3-70B-Instruct | attacks (dipper, rewrite_attack) | 915 | 99.8 | 100.0 | 100.0 | 94.2 | 98.6 | 100.0 | 100.0 | 94.2 | 100.0 |

**By corpus.** Fire rate % at the 1% cut.

| Corpus | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BAWE | human | 439 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| argument-annotated-essays | human | 402 | 0.2 | 0.0 | 0.0 | 3.2 | 0.0 | 1.7 | 0.0 | 0.2 | 0.0 |
| persuade | human | 74 | 0.0 | 0.0 | 0.0 | 1.4 | 0.0 | 1.4 | 0.0 | 0.0 | 0.0 |
| BAWE | model rewrites of the student's essay (improve-human, rewrite-human) | 1,754 | 1.0 | 0.3 | 30.0 | 1.0 | 0.3 | 13.6 | 9.7 | 6.4 | 61.7 |
| argument-annotated-essays | model rewrites of the student's essay (improve-human, rewrite-human) | 1,597 | 1.9 | 1.1 | 91.6 | 6.9 | 3.1 | 79.2 | 48.4 | 20.5 | 87.7 |
| persuade | model rewrites of the student's essay (improve-human, rewrite-human) | 297 | 3.0 | 5.4 | 85.5 | 8.8 | 6.7 | 58.6 | 34.0 | 31.6 | 79.1 |
| BAWE | task (assignment only; task, task+resource) | 878 | 99.5 | 100.0 | 100.0 | 94.3 | 98.1 | 100.0 | 100.0 | 95.9 | 100.0 |
| argument-annotated-essays | task (assignment only; task, task+resource) | 802 | 99.4 | 99.9 | 100.0 | 92.3 | 99.6 | 100.0 | 100.0 | 99.5 | 100.0 |
| persuade | task (assignment only; task, task+resource) | 190 | 98.4 | 100.0 | 100.0 | 92.6 | 100.0 | 100.0 | 100.0 | 88.9 | 100.0 |
| BAWE | from the student's summary (summary, task+summary) | 1,735 | 98.2 | 99.5 | 100.0 | 88.5 | 93.9 | 100.0 | 100.0 | 86.3 | 100.0 |
| argument-annotated-essays | from the student's summary (summary, task+summary) | 1,515 | 91.8 | 99.5 | 100.0 | 85.3 | 95.6 | 100.0 | 100.0 | 97.8 | 99.7 |
| persuade | from the student's summary (summary, task+summary) | 300 | 91.0 | 99.7 | 100.0 | 78.3 | 90.0 | 100.0 | 100.0 | 93.0 | 100.0 |
| BAWE | attacks (dipper, rewrite_attack) | 1,713 | 94.5 | 81.7 | 98.4 | 86.2 | 72.5 | 84.9 | 63.5 | 85.6 | 99.7 |
| argument-annotated-essays | attacks (dipper, rewrite_attack) | 1,606 | 82.4 | 70.2 | 98.5 | 76.8 | 62.5 | 79.8 | 57.0 | 89.2 | 95.3 |
| persuade | attacks (dipper, rewrite_attack) | 285 | 89.8 | 82.1 | 99.6 | 74.4 | 70.2 | 93.3 | 63.9 | 87.0 | 97.5 |
