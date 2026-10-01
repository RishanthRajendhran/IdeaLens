### LAMP: main table

Fire rate % at the 1% cut (global / per-format). TPR on model-idea rows, FPR on human-idea rows.

- Both arms carry the model's ideas, so every cell is a detection rate; the result is the drop from preedit to postedit. There is no human arm, so no FPR or AUC.
- A professional writer's edit keeps a median of 76% of the draft's words. Every document is under 500 words.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| preedit | model ideas (TPR) | 1,057 | 98.3 / 99.1 | 100.0 / 99.9 | 100.0 / 100.0 | 93.0 / 95.4 | 94.6 / 97.7 | 100.0 / 99.6 | 99.8 / 99.1 | 72.7 / – | 100.0 |
| postedit | model ideas, person-edited (TPR) | 1,053 | 88.0 / 92.4 | 89.6 / 95.7 | 96.0 / 98.0 | 79.1 / 85.5 | 64.3 / 91.9 | 91.6 / 94.3 | 80.5 / 88.4 | 37.5 / – | 92.4 |

**Length.** Share under 500 words: preedit 100.0%, postedit 100.0%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| preedit · < 500 | model ideas (TPR) | 1,057 | 98.3 / 99.1 | 100.0 / 99.9 | 100.0 / 100.0 | 93.0 / 95.4 | 94.6 / 97.7 | 100.0 / 99.6 | 99.8 / 99.1 | 72.7 / – | 100.0 |
| postedit · < 500 | model ideas, person-edited (TPR) | 1,053 | 88.0 / 92.4 | 89.6 / 95.7 | 96.0 / 98.0 | 79.1 / 85.5 | 64.3 / 91.9 | 91.6 / 94.3 | 80.5 / 88.4 | 37.5 / – | 92.4 |

### LAMP: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global / per-format).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| preedit | IdeaLens · outline | 91.1 / – | 97.7 / 98.7 | 99.5 / 99.5 | 100.0 / 100.0 |
| preedit | IdeaLens · document | 99.7 / – | 100.0 / 99.9 | 100.0 / 100.0 | 100.0 / 100.0 |
| preedit | ProseLens | 100.0 / – | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 |
| preedit | IdeaLens-ModernBERT-L · outline | 66.4 / – | 87.2 / 90.2 | 97.2 / 97.4 | 99.9 / 99.5 |
| preedit | IdeaLens-ModernBERT-L · document | 80.2 / – | 89.4 / 96.5 | 99.1 / 99.1 | 100.0 / 99.9 |
| preedit | ProseLens-ModernBERT-L | 94.0 / – | 99.9 / 98.5 | 100.0 / 99.9 | 100.0 / 100.0 |
| preedit | EditLens-Llama-3B (cal.) | 0.0 / – | 96.9 / 83.5 | 100.0 / 99.9 | 100.0 / 100.0 |
| preedit | Binoculars (cal.) | 50.4 / – | 72.9 / 76.5 | 89.3 / 88.4 | 93.9 / 94.2 |
| postedit | IdeaLens · outline | 71.1 / – | 83.6 / 89.5 | 92.8 / 94.9 | 97.1 / 97.7 |
| postedit | IdeaLens · document | 74.0 / – | 84.0 / 94.2 | 94.4 / 97.5 | 98.6 / 99.3 |
| postedit | ProseLens | 91.8 / – | 94.7 / 97.5 | 97.2 / 98.4 | 98.5 / 99.0 |
| postedit | IdeaLens-ModernBERT-L · outline | 41.5 / – | 68.3 / 75.1 | 88.5 / 92.8 | 96.9 / 97.6 |
| postedit | IdeaLens-ModernBERT-L · document | 37.3 / – | 51.1 / 86.0 | 83.5 / 95.6 | 98.8 / 99.0 |
| postedit | ProseLens-ModernBERT-L | 60.3 / – | 85.0 / 91.0 | 96.4 / 97.8 | 99.2 / 99.8 |
| postedit | EditLens-Llama-3B (cal.) | 0.0 / – | 55.4 / 76.8 | 92.4 / 93.7 | 96.0 / 96.8 |
| postedit | Binoculars (cal.) | 17.3 / – | 37.6 / 46.7 | 64.4 / 65.4 | 75.9 / 75.4 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude3.5-sonnet | preedit | 368 | 98.6 / 99.2 | 100.0 / 100.0 | 100.0 / 100.0 | 92.4 / 94.8 | 94.0 / 96.7 | 100.0 / 99.5 | 100.0 / 98.9 | 88.0 / – | 100.0 |
| gpt4o | preedit | 393 | 98.7 / 99.7 | 100.0 / 99.7 | 100.0 / 100.0 | 93.6 / 96.2 | 92.6 / 97.2 | 100.0 / 99.5 | 99.5 / 98.7 | 37.7 / – | 100.0 |
| llama370B | preedit | 296 | 97.3 / 98.3 | 100.0 / 100.0 | 100.0 / 100.0 | 92.9 / 94.9 | 98.0 / 99.7 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / – | 100.0 |
| claude3.5-sonnet | postedit | 368 | 86.4 / 91.8 | 87.8 / 96.2 | 95.7 / 97.3 | 73.6 / 83.4 | 60.6 / 91.6 | 90.8 / 93.2 | 84.0 / 89.9 | 38.0 / – | 89.9 |
| gpt4o | postedit | 392 | 89.5 / 93.1 | 89.3 / 95.2 | 95.7 / 98.2 | 79.8 / 86.2 | 62.5 / 91.1 | 91.3 / 94.1 | 75.8 / 86.7 | 10.7 / – | 93.6 |
| llama370B | postedit | 293 | 88.1 / 92.2 | 92.2 / 95.9 | 96.9 / 98.6 | 85.0 / 87.0 | 71.3 / 93.5 | 93.2 / 95.9 | 82.6 / 88.7 | 72.7 / – | 93.9 |

**By genre.** Fire rate % at the 1% cut.

| Genre | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Creative NonFiction | preedit | 19 | 94.7 / 94.7 | 100.0 / 100.0 | 100.0 / 100.0 | 78.9 / 94.7 | 89.5 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 57.9 / – | 100.0 |
| Food Writing | preedit | 83 | 97.6 / 97.6 | 100.0 / 98.8 | 100.0 / 100.0 | 88.0 / 85.5 | 96.4 / 89.2 | 100.0 / 98.8 | 98.8 / 97.6 | 61.4 / – | 100.0 |
| Internet Advice Column | preedit | 30 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 76.7 / 93.3 | 80.0 / 96.7 | 100.0 / 100.0 | 100.0 / 100.0 | 40.0 / – | 100.0 |
| Literary Fiction | preedit | 815 | 98.4 / 99.6 | 100.0 / 100.0 | 100.0 / 100.0 | 94.7 / 98.0 | 94.7 / 99.6 | 100.0 / 100.0 | 99.9 / 99.8 | 75.5 / – | 100.0 |
| Travel Writing | preedit | 110 | 98.2 / 97.3 | 100.0 / 100.0 | 100.0 / 100.0 | 90.9 / 83.6 | 97.3 / 90.0 | 100.0 / 97.3 | 100.0 / 95.5 | 71.8 / – | 100.0 |
| Creative NonFiction | postedit | 19 | 73.7 / 84.2 | 73.7 / 94.7 | 78.9 / 94.7 | 52.6 / 68.4 | 36.8 / 73.7 | 73.7 / 94.7 | 84.2 / 78.9 | 15.8 / – | 84.2 |
| Food Writing | postedit | 81 | 93.8 / 93.8 | 98.8 / 92.6 | 100.0 / 98.8 | 79.0 / 72.8 | 84.0 / 69.1 | 93.8 / 81.5 | 93.8 / 69.1 | 45.7 / – | 98.8 |
| Internet Advice Column | postedit | 30 | 76.7 / 83.3 | 90.0 / 96.7 | 93.3 / 96.7 | 63.3 / 63.3 | 33.3 / 83.3 | 83.3 / 90.0 | 76.7 / 86.7 | 6.7 / – | 90.0 |
| Literary Fiction | postedit | 813 | 87.2 / 92.6 | 87.8 / 96.8 | 95.6 / 97.8 | 79.0 / 89.3 | 61.3 / 97.3 | 91.6 / 98.0 | 77.1 / 93.4 | 36.7 / – | 91.0 |
| Travel Writing | postedit | 110 | 95.5 / 93.6 | 98.2 / 90.0 | 100.0 / 100.0 | 89.1 / 75.5 | 85.5 / 74.5 | 95.5 / 77.3 | 96.4 / 68.2 | 50.0 / – | 100.0 |

**By LAMP split.** Fire rate % at the 1% cut.

| Lamp split | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| test | preedit | 911 | 98.2 / 99.1 | 100.0 / 99.9 | 100.0 / 100.0 | 92.3 / 95.0 | 94.2 / 97.5 | 100.0 / 99.6 | 99.8 / 99.0 | 73.0 / – | 100.0 |
| validation | preedit | 146 | 98.6 / 99.3 | 100.0 / 100.0 | 100.0 / 100.0 | 97.3 / 97.9 | 97.3 / 99.3 | 100.0 / 100.0 | 100.0 / 100.0 | 70.5 / – | 100.0 |
| test | postedit | 907 | 87.2 / 91.8 | 89.4 / 95.3 | 95.9 / 97.9 | 77.7 / 84.2 | 63.5 / 90.8 | 91.5 / 93.8 | 80.9 / 87.9 | 38.0 / – | 92.1 |
| validation | postedit | 146 | 93.2 / 95.9 | 90.4 / 98.6 | 96.6 / 98.6 | 87.7 / 93.2 | 69.2 / 98.6 | 92.5 / 97.3 | 78.1 / 91.8 | 34.2 / – | 94.5 |
