### CoCoNUTS: main table

Fire rate % at the 1% cut (global / per-format). TPR on model-idea rows, FPR on human-idea rows.

- CoCoNUTS itself labels model-polished (hwmp) and model-translated (hwmt) human reviews human, as our rule does. hwmg, a model generating from the person's review, is its own mix class: reported in the P(AI) table, not as a rate.
- Every document is English (hwmt is translated into English), so the ModernBERT document columns are valid on every row.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hw | human ideas (FPR) | 1,194 | 0.0 / 0.1 | 0.0 / 0.0 | 0.0 / 0.0 | 0.3 / 1.3 | 0.0 / 0.7 | 0.0 / 0.7 | 0.0 / 0.3 | 0.0 / – | 0.0 |
| hwmp (model-polished) | human ideas, AI prose (FPR) | 1,497 | 12.2 / 19.1 | 12.0 / 26.7 | 61.0 / 79.1 | 15.4 / 22.1 | 13.9 / 36.5 | 52.8 / 80.4 | 62.9 / 87.2 | 7.1 / – | 61.2 |
| hwmt (model-translated into English) | human ideas, AI prose (FPR) | 1,493 | 0.1 / 0.5 | 0.0 / 0.1 | 0.5 / 7.2 | 0.8 / 2.3 | 0.1 / 2.9 | 2.1 / 16.9 | 1.3 / 27.2 | 1.3 / – | 0.1 |
| AI (mg, mgmp) | model ideas (TPR) | 1,400 | 92.1 / 97.1 | 98.9 / 100.0 | 100.0 / 100.0 | 92.5 / 96.6 | 94.7 / 99.5 | 100.0 / 100.0 | 99.0 / 99.9 | 47.7 / – | 96.3 |
| AUC, AI vs hw | | | 1.000 | 1.000 | 1.000 | 0.997 | 1.000 | 1.000 | 1.000 | 0.963 | 0.991 |
| AUC, AI vs hw + hwmp + hwmt | | | 0.988 | 0.995 | 0.989 | 0.981 | 0.986 | 0.974 | 0.960 | 0.873 | 0.966 |

**Length.** Share under 500 words: hw 61.6%, hwmp (model-polished) 77.0%, hwmt (model-translated into English) 76.3%, AI (mg, mgmp) 52.0%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hw · < 500 | human ideas (FPR) | 735 | 0.0 / 0.1 | 0.0 / 0.0 | 0.0 / 0.0 | 0.1 / 1.4 | 0.0 / 1.1 | 0.0 / 1.1 | 0.0 / 0.0 | 0.0 / – | 0.0 |
| hw · >= 500 | human ideas (FPR) | 459 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.4 / 1.3 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.7 | 0.0 / – | 0.0 |
| hwmp (model-polished) · < 500 | human ideas, AI prose (FPR) | 1,153 | 13.6 / 21.1 | 13.6 / 29.1 | 68.5 / 85.8 | 17.6 / 24.5 | 16.0 / 40.8 | 58.4 / 84.6 | 69.7 / 90.9 | 8.8 / – | 68.8 |
| hwmp (model-polished) · >= 500 | human ideas, AI prose (FPR) | 344 | 7.3 / 12.5 | 6.7 / 18.6 | 35.8 / 56.7 | 8.1 / 14.0 | 7.0 / 22.4 | 34.3 / 66.3 | 40.1 / 75.0 | 1.7 / – | 35.8 |
| hwmt (model-translated into English) · < 500 | human ideas, AI prose (FPR) | 1,139 | 0.1 / 0.6 | 0.0 / 0.1 | 0.6 / 9.5 | 1.1 / 3.0 | 0.1 / 3.9 | 2.8 / 21.5 | 1.8 / 33.1 | 1.7 / – | 0.2 |
| hwmt (model-translated into English) · >= 500 | human ideas, AI prose (FPR) | 354 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 2.0 | 0.0 / 8.2 | 0.3 / – | 0.0 |
| AI (mg, mgmp) · < 500 | model ideas (TPR) | 728 | 93.4 / 98.2 | 98.9 / 100.0 | 100.0 / 100.0 | 92.7 / 96.7 | 94.5 / 99.7 | 100.0 / 100.0 | 99.9 / 100.0 | 51.2 / – | 96.3 |
| AI (mg, mgmp) · >= 500 | model ideas (TPR) | 672 | 90.6 / 96.0 | 98.8 / 100.0 | 100.0 / 100.0 | 92.3 / 96.6 | 94.9 / 99.3 | 100.0 / 100.0 | 98.1 / 99.9 | 43.9 / – | 96.3 |

**Shared P(AI) table, CoCoNUTS rows.** P(AI) % (1 - P(human); Pangram: its derived P(AI)); the statistic is named per row where a level shows more than the mean.

| Level | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mg + mgmp · mean | model ideas | 1,400 | 95.6 | 99.3 | 99.9 | 97.7 | 98.4 | 99.8 | – | – | 92.7 |
| mg + mgmp · median | model ideas | 1,400 | 99.2 | 99.8 | 100.0 | 99.7 | 99.5 | 99.9 | – | – | 100.0 |
| hwmg · mean | mixed, human-leaning | 1,200 | 47.5 | 62.6 | 86.6 | 66.5 | 67.5 | 90.2 | – | – | 68.1 |
| hwmg · median | mixed, human-leaning | 1,200 | 46.7 | 83.6 | 98.4 | 82.9 | 88.1 | 98.9 | – | – | 71.3 |
| hwmg · min | mixed, human-leaning | 1,200 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 |
| hwmg · max | mixed, human-leaning | 1,200 | 99.7 | 99.9 | 100.0 | 99.9 | 99.8 | 100.0 | – | – | 100.0 |
| hwmp · mean | human ideas, AI prose | 1,497 | 21.4 | 22.1 | 55.8 | 41.1 | 35.9 | 62.5 | – | – | 52.4 |
| hwmp · median | human ideas, AI prose | 1,497 | 0.9 | 0.3 | 69.7 | 27.3 | 14.5 | 86.0 | – | – | 50.0 |
| hw · mean | human ideas | 1,194 | 0.7 | 0.0 | 0.0 | 13.0 | 2.7 | 0.2 | – | – | 0.0 |
| hw · median | human ideas | 1,194 | 0.1 | 0.0 | 0.0 | 4.6 | 0.6 | 0.0 | – | – | 0.0 |

### CoCoNUTS: appendix

**Rows reported in the appendix only.** Fire rate % at the 1% cut.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hwmg (CoCoNUTS mix) | mixed, human-leaning (fire rate) | 1,200 | 29.8 / 44.8 | 40.4 / 73.2 | 90.3 / 97.2 | 33.8 / 48.3 | 36.6 / 72.2 | 86.7 / 98.4 | 90.9 / 98.1 | 31.8 / – | 76.0 |

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global / per-format).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| hw | IdeaLens · outline | 0.0 / – | 0.0 / 0.1 | 0.1 / 0.4 | 0.5 / 1.8 |
| hw | IdeaLens · document | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.1 | 0.1 / 0.3 |
| hw | ProseLens | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.2 |
| hw | IdeaLens-ModernBERT-L · outline | 0.0 / – | 0.1 / 0.2 | 2.2 / 5.4 | 11.3 / 20.8 |
| hw | IdeaLens-ModernBERT-L · document | 0.0 / – | 0.0 / 0.0 | 0.1 / 14.6 | 23.1 / 53.9 |
| hw | ProseLens-ModernBERT-L | 0.0 / – | 0.0 / 0.1 | 0.4 / 2.9 | 4.1 / 13.6 |
| hw | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 0.0 | 0.3 / 1.5 | 4.1 / 7.4 |
| hw | Binoculars (cal.) | 0.0 / – | 0.0 / 0.8 | 2.0 / 5.2 | 6.2 / 9.8 |
| hwmp (model-polished) | IdeaLens · outline | 2.9 / – | 9.4 / 13.4 | 17.0 / 24.8 | 25.8 / 33.6 |
| hwmp (model-polished) | IdeaLens · document | 3.5 / – | 7.6 / 18.8 | 20.8 / 34.1 | 36.2 / 43.1 |
| hwmp (model-polished) | ProseLens | 34.1 / – | 50.2 / 71.7 | 75.1 / 85.9 | 88.3 / 90.7 |
| hwmp (model-polished) | IdeaLens-ModernBERT-L · outline | 2.7 / – | 10.4 / 13.9 | 24.7 / 34.5 | 45.8 / 57.9 |
| hwmp (model-polished) | IdeaLens-ModernBERT-L · document | 2.2 / – | 7.6 / 23.1 | 30.8 / 65.5 | 71.7 / 88.2 |
| hwmp (model-polished) | ProseLens-ModernBERT-L | 18.6 / – | 39.2 / 65.1 | 73.7 / 90.5 | 91.6 / 94.1 |
| hwmp (model-polished) | EditLens-Llama-3B (cal.) | 0.0 / – | 30.8 / 76.5 | 85.7 / 92.3 | 93.2 / 93.5 |
| hwmp (model-polished) | Binoculars (cal.) | 0.3 / – | 7.8 / 32.5 | 41.3 / 57.7 | 61.6 / 69.2 |
| hwmt (model-translated into English) | IdeaLens · outline | 0.0 / – | 0.0 / 0.1 | 0.2 / 1.1 | 1.2 / 3.2 |
| hwmt (model-translated into English) | IdeaLens · document | 0.0 / – | 0.0 / 0.1 | 0.1 / 0.1 | 0.1 / 1.7 |
| hwmt (model-translated into English) | ProseLens | 0.1 / – | 0.2 / 2.3 | 4.4 / 25.3 | 37.2 / 57.5 |
| hwmt (model-translated into English) | IdeaLens-ModernBERT-L · outline | 0.1 / – | 0.5 / 0.6 | 2.8 / 8.0 | 17.0 / 29.5 |
| hwmt (model-translated into English) | IdeaLens-ModernBERT-L · document | 0.0 / – | 0.0 / 0.4 | 1.2 / 31.3 | 44.2 / 71.0 |
| hwmt (model-translated into English) | ProseLens-ModernBERT-L | 0.0 / – | 0.5 / 4.4 | 9.8 / 43.9 | 53.7 / 78.4 |
| hwmt (model-translated into English) | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 7.6 | 18.6 / 66.6 | 82.5 / 92.6 |
| hwmt (model-translated into English) | Binoculars (cal.) | 0.1 / – | 1.4 / 11.6 | 18.2 / 31.1 | 36.2 / 45.5 |
| AI (mg, mgmp) | IdeaLens · outline | 70.1 / – | 88.3 / 93.6 | 96.6 / 98.9 | 99.1 / 99.6 |
| AI (mg, mgmp) | IdeaLens · document | 89.2 / – | 96.7 / 99.6 | 99.9 / 100.0 | 100.0 / 100.0 |
| AI (mg, mgmp) | ProseLens | 99.9 / – | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 |
| AI (mg, mgmp) | IdeaLens-ModernBERT-L · outline | 63.1 / – | 86.4 / 90.9 | 97.4 / 98.9 | 99.4 / 99.9 |
| AI (mg, mgmp) | IdeaLens-ModernBERT-L · document | 53.2 / – | 87.8 / 98.1 | 99.3 / 100.0 | 100.0 / 100.0 |
| AI (mg, mgmp) | ProseLens-ModernBERT-L | 92.6 / – | 99.9 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 |
| AI (mg, mgmp) | EditLens-Llama-3B (cal.) | 0.0 / – | 95.5 / 99.6 | 99.9 / 100.0 | 100.0 / 100.0 |
| AI (mg, mgmp) | Binoculars (cal.) | 22.5 / – | 48.9 / 74.0 | 79.4 / 86.6 | 88.6 / 92.4 |
| hwmg (CoCoNUTS mix) | IdeaLens · outline | 6.9 / – | 21.4 / 33.1 | 41.7 / 56.9 | 57.9 / 68.9 |
| hwmg (CoCoNUTS mix) | IdeaLens · document | 9.3 / – | 24.3 / 60.3 | 64.1 / 80.1 | 81.8 / 87.6 |
| hwmg (CoCoNUTS mix) | ProseLens | 72.8 / – | 85.9 / 95.1 | 96.0 / 98.8 | 99.2 / 99.8 |
| hwmg (CoCoNUTS mix) | IdeaLens-ModernBERT-L · outline | 7.2 / – | 23.2 / 30.1 | 50.9 / 64.7 | 75.2 / 84.4 |
| hwmg (CoCoNUTS mix) | IdeaLens-ModernBERT-L · document | 2.8 / – | 18.4 / 54.1 | 64.7 / 91.0 | 92.7 / 97.5 |
| hwmg (CoCoNUTS mix) | ProseLens-ModernBERT-L | 36.7 / – | 71.5 / 93.7 | 96.5 / 99.7 | 99.8 / 100.0 |
| hwmg (CoCoNUTS mix) | EditLens-Llama-3B (cal.) | 0.0 / – | 66.4 / 95.2 | 97.8 / 99.8 | 100.0 / 100.0 |
| hwmg (CoCoNUTS mix) | Binoculars (cal.) | 5.9 / – | 32.8 / 64.8 | 71.3 / 82.8 | 84.6 / 88.6 |

**By arm.** Fire rate % at the 1% cut.

| Arm | Description | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hw | hw | 1,194 | 0.0 / 0.1 | 0.0 / 0.0 | 0.0 / 0.0 | 0.3 / 1.3 | 0.0 / 0.7 | 0.0 / 0.7 | 0.0 / 0.3 | 0.0 / – | 0.0 |
| hwmp | hwmp (model-polished) | 1,497 | 12.2 / 19.1 | 12.0 / 26.7 | 61.0 / 79.1 | 15.4 / 22.1 | 13.9 / 36.5 | 52.8 / 80.4 | 62.9 / 87.2 | 7.1 / – | 61.2 |
| hwmt | hwmt (model-translated into English) | 1,493 | 0.1 / 0.5 | 0.0 / 0.1 | 0.5 / 7.2 | 0.8 / 2.3 | 0.1 / 2.9 | 2.1 / 16.9 | 1.3 / 27.2 | 1.3 / – | 0.1 |
| mg | AI (mg, mgmp) | 700 | 90.6 / 95.9 | 98.3 / 100.0 | 100.0 / 100.0 | 91.0 / 95.7 | 92.4 / 99.4 | 100.0 / 100.0 | 98.1 / 99.9 | 44.3 / – | 93.1 |
| mgmp | AI (mg, mgmp) | 700 | 93.6 / 98.4 | 99.4 / 100.0 | 100.0 / 100.0 | 94.0 / 97.6 | 97.0 / 99.6 | 100.0 / 100.0 | 99.9 / 100.0 | 51.1 / – | 99.4 |
| hwmg | hwmg (CoCoNUTS mix) | 1,200 | 29.8 / 44.8 | 40.4 / 73.2 | 90.3 / 97.2 | 33.8 / 48.3 | 36.6 / 72.2 | 86.7 / 98.4 | 90.9 / 98.1 | 31.8 / – | 76.0 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| human_gemini | hwmp (model-polished) | 499 | 0.4 / 1.4 | 0.6 / 4.8 | 41.3 / 71.1 | 3.0 / 6.4 | 1.6 / 14.4 | 34.9 / 74.3 | 48.9 / 88.6 | 0.8 / – | 46.1 |
| human_llama | hwmp (model-polished) | 500 | 3.4 / 8.2 | 1.8 / 14.0 | 62.4 / 85.0 | 6.8 / 11.8 | 4.6 / 28.0 | 47.6 / 85.6 | 64.4 / 92.2 | 17.0 / – | 61.2 |
| human_qwen3 | hwmp (model-polished) | 498 | 32.7 / 47.8 | 33.7 / 61.4 | 79.3 / 81.1 | 36.5 / 48.2 | 35.5 / 67.3 | 76.1 / 81.1 | 75.5 / 80.9 | 3.6 / – | 76.3 |
| human_llama | hwmt (model-translated into English) | 747 | 0.0 / 0.3 | 0.0 / 0.0 | 0.7 / 7.4 | 1.2 / 3.1 | 0.1 / 3.1 | 2.7 / 17.4 | 1.6 / 25.2 | 2.0 / – | 0.0 |
| human_qwen25 | hwmt (model-translated into English) | 746 | 0.1 / 0.7 | 0.0 / 0.1 | 0.3 / 7.1 | 0.4 / 1.5 | 0.0 / 2.8 | 1.6 / 16.4 | 1.1 / 29.2 | 0.7 / – | 0.3 |
| claude | AI (mg, mgmp) | 100 | 93.0 / 99.0 | 100.0 / 100.0 | 100.0 / 100.0 | 98.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 61.0 / – | 96.0 |
| deepseek | AI (mg, mgmp) | 100 | 91.0 / 98.0 | 100.0 / 100.0 | 100.0 / 100.0 | 80.0 / 89.0 | 85.0 / 99.0 | 100.0 / 100.0 | 99.0 / 100.0 | 0.0 / – | 100.0 |
| deepseek_gemini | AI (mg, mgmp) | 88 | 95.5 / 97.7 | 100.0 / 100.0 | 100.0 / 100.0 | 95.5 / 97.7 | 93.2 / 97.7 | 100.0 / 100.0 | 100.0 / 100.0 | 0.0 / – | 100.0 |
| deepseek_llama | AI (mg, mgmp) | 88 | 97.7 / 98.9 | 98.9 / 100.0 | 100.0 / 100.0 | 92.0 / 95.5 | 98.9 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 33.0 / – | 100.0 |
| gemini | AI (mg, mgmp) | 100 | 59.0 / 78.0 | 90.0 / 100.0 | 100.0 / 100.0 | 70.0 / 83.0 | 73.0 / 97.0 | 100.0 / 100.0 | 88.0 / 99.0 | 0.0 / – | 98.0 |
| gemini_llama | AI (mg, mgmp) | 88 | 75.0 / 95.5 | 98.9 / 100.0 | 100.0 / 100.0 | 83.0 / 95.5 | 95.5 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 35.2 / – | 95.5 |
| gpt4o | AI (mg, mgmp) | 100 | 98.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 98.0 / 100.0 | 99.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 26.0 / – | 59.0 |
| llama | AI (mg, mgmp) | 100 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / – | 100.0 |
| llama_gemini | AI (mg, mgmp) | 88 | 98.9 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 97.7 / 100.0 | 97.7 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 83.0 / – | 100.0 |
| llama_qwen25 | AI (mg, mgmp) | 87 | 97.7 / 98.9 | 100.0 / 100.0 | 100.0 / 100.0 | 98.9 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / – | 100.0 |
| qwen25 | AI (mg, mgmp) | 100 | 98.0 / 98.0 | 100.0 / 100.0 | 100.0 / 100.0 | 99.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / – | 99.0 |
| qwen25_gemini | AI (mg, mgmp) | 87 | 98.9 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 98.9 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 98.9 / 100.0 | 69.0 / – | 100.0 |
| qwen3 | AI (mg, mgmp) | 100 | 95.0 / 98.0 | 98.0 / 100.0 | 100.0 / 100.0 | 92.0 / 98.0 | 90.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 23.0 / – | 100.0 |
| qwen3_gemini | AI (mg, mgmp) | 87 | 88.5 / 97.7 | 100.0 / 100.0 | 100.0 / 100.0 | 89.7 / 95.4 | 94.3 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 32.2 / – | 100.0 |
| qwen3_llama | AI (mg, mgmp) | 87 | 96.6 / 98.9 | 97.7 / 100.0 | 100.0 / 100.0 | 96.6 / 96.6 | 96.6 / 98.9 | 100.0 / 100.0 | 100.0 / 100.0 | 57.5 / – | 100.0 |
| human_gemini | hwmg (CoCoNUTS mix) | 300 | 5.3 / 12.7 | 11.7 / 39.7 | 71.7 / 91.0 | 8.7 / 16.7 | 8.3 / 36.3 | 65.3 / 95.0 | 73.7 / 93.7 | 0.7 / – | 69.7 |
| human_llama | hwmg (CoCoNUTS mix) | 300 | 47.3 / 66.0 | 62.3 / 95.3 | 98.7 / 99.7 | 53.3 / 71.3 | 53.0 / 92.3 | 93.7 / 100.0 | 95.7 / 99.7 | 56.3 / – | 68.3 |
| human_qwen25 | hwmg (CoCoNUTS mix) | 300 | 35.7 / 52.3 | 47.0 / 79.3 | 91.3 / 98.0 | 41.3 / 55.3 | 48.0 / 80.7 | 91.3 / 98.7 | 96.3 / 99.0 | 50.3 / – | 69.3 |
| human_qwen3 | hwmg (CoCoNUTS mix) | 300 | 30.7 / 48.0 | 40.7 / 78.7 | 99.7 / 100.0 | 32.0 / 50.0 | 37.0 / 79.7 | 96.3 / 100.0 | 98.0 / 100.0 | 20.0 / – | 96.7 |
