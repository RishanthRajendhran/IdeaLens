### Sem-Detect: main table

Fire rate % at the 1% cut (global / per-format). TPR on model-idea rows, FPR on human-idea rows.

- rewrite: a model rewords a person's review. The benchmark labels it AI; by the idea-level rule it carries the person's ideas, so its fire rate is an FPR.
- The rewrite FPR is driven by qwen3-235b (see the generator table), whose rewrites run about 24% longer and add interpretive detail.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai | model ideas (TPR) | 6,767 | 71.4 / 85.7 | 95.9 / 99.9 | 100.0 / 100.0 | 63.6 / 76.6 | 85.4 / 97.9 | 99.9 / 100.0 | 65.2 / 95.2 | 0.2 / – | 75.7 |
| human | human ideas (FPR) | 3,061 | 0.2 / 0.7 | 0.0 / 0.0 | 0.0 / 0.1 | 1.7 / 3.8 | 0.0 / 2.6 | 0.1 / 1.7 | 0.0 / 0.9 | 0.1 / – | 0.0 |
| rewrite | human ideas, AI prose (FPR) | 12,318 | 8.2 / 15.2 | 11.8 / 25.0 | 64.7 / 90.8 | 10.9 / 17.6 | 13.0 / 35.0 | 54.2 / 87.5 | 66.0 / 93.5 | 1.7 / – | 77.7 |
| AUC, ai vs human | | | 0.993 | 1.000 | 1.000 | 0.961 | 0.998 | 1.000 | 0.999 | 0.795 | 0.979 |
| AUC, ai vs human + rewrite | | | 0.942 | 0.978 | 0.959 | 0.895 | 0.955 | 0.913 | 0.560 | 0.527 | 0.722 |

**Length.** Share under 500 words: ai 22.0%, human 65.6%, rewrite 64.2%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai · < 500 | model ideas (TPR) | 1,488 | 91.7 / 97.3 | 98.4 / 100.0 | 100.0 / 100.0 | 86.2 / 93.8 | 98.1 / 100.0 | 99.9 / 100.0 | 98.4 / 100.0 | 0.9 / – | 80.0 |
| ai · >= 500 | model ideas (TPR) | 5,279 | 65.7 / 82.4 | 95.2 / 99.8 | 100.0 / 100.0 | 57.3 / 71.7 | 81.8 / 97.3 | 99.9 / 100.0 | 55.9 / 93.8 | 0.1 / – | 74.6 |
| human · < 500 | human ideas (FPR) | 2,007 | 0.2 / 0.9 | 0.0 / 0.0 | 0.0 / 0.1 | 2.0 / 4.8 | 0.0 / 3.9 | 0.1 / 2.6 | 0.0 / 1.1 | 0.1 / – | 0.0 |
| human · >= 500 | human ideas (FPR) | 1,054 | 0.0 / 0.2 | 0.0 / 0.0 | 0.0 / 0.0 | 0.9 / 1.9 | 0.0 / 0.1 | 0.0 / 0.0 | 0.0 / 0.4 | 0.0 / – | 0.0 |
| rewrite · < 500 | human ideas, AI prose (FPR) | 7,903 | 7.7 / 14.0 | 8.6 / 21.1 | 69.0 / 94.8 | 10.5 / 17.5 | 11.2 / 35.7 | 54.2 / 90.7 | 70.8 / 96.2 | 2.6 / – | 81.7 |
| rewrite · >= 500 | human ideas, AI prose (FPR) | 4,415 | 9.2 / 17.4 | 17.6 / 32.1 | 56.8 / 83.6 | 11.6 / 17.9 | 16.2 / 33.8 | 54.2 / 81.9 | 57.4 / 88.8 | 0.2 / – | 70.6 |

### Sem-Detect: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global / per-format).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| ai | IdeaLens · outline | 34.2 / – | 61.5 / 74.5 | 83.1 / 92.2 | 93.0 / 96.9 |
| ai | IdeaLens · document | 74.0 / – | 89.7 / 99.4 | 99.7 / 100.0 | 100.0 / 100.0 |
| ai | ProseLens | 100.0 / – | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 |
| ai | IdeaLens-ModernBERT-L · outline | 23.8 / – | 50.5 / 59.6 | 79.7 / 89.4 | 94.9 / 97.9 |
| ai | IdeaLens-ModernBERT-L · document | 57.0 / – | 75.0 / 92.7 | 96.4 / 99.9 | 99.9 / 100.0 |
| ai | ProseLens-ModernBERT-L | 74.2 / – | 99.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 |
| ai | EditLens-Llama-3B (cal.) | 0.0 / – | 15.6 / 80.8 | 93.6 / 99.6 | 99.9 / 100.0 |
| ai | Binoculars (cal.) | 0.0 / – | 0.3 / 6.2 | 11.3 / 27.6 | 31.8 / 44.9 |
| human | IdeaLens · outline | 0.0 / – | 0.1 / 0.2 | 0.6 / 2.0 | 2.5 / 5.2 |
| human | IdeaLens · document | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.2 | 0.4 / 1.5 |
| human | ProseLens | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.3 | 0.7 / 1.8 |
| human | IdeaLens-ModernBERT-L · outline | 0.1 / – | 0.5 / 1.2 | 4.7 / 10.4 | 19.5 / 32.6 |
| human | IdeaLens-ModernBERT-L · document | 0.0 / – | 0.0 / 0.2 | 0.8 / 24.9 | 35.5 / 61.4 |
| human | ProseLens-ModernBERT-L | 0.0 / – | 0.1 / 0.2 | 0.6 / 7.1 | 9.0 / 20.9 |
| human | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 0.1 | 0.5 / 3.3 | 6.2 / 9.8 |
| human | Binoculars (cal.) | 0.0 / – | 0.2 / 1.5 | 2.9 / 6.1 | 7.8 / 11.1 |
| rewrite | IdeaLens · outline | 1.5 / – | 5.4 / 9.5 | 13.3 / 21.6 | 22.7 / 31.6 |
| rewrite | IdeaLens · document | 3.4 / – | 7.6 / 18.9 | 20.6 / 31.7 | 33.2 / 42.2 |
| rewrite | ProseLens | 29.7 / – | 48.1 / 82.0 | 85.6 / 96.3 | 97.6 / 99.1 |
| rewrite | IdeaLens-ModernBERT-L · outline | 1.8 / – | 6.8 / 9.3 | 20.0 / 31.5 | 43.4 / 58.2 |
| rewrite | IdeaLens-ModernBERT-L · document | 2.3 / – | 7.2 / 20.8 | 28.6 / 66.9 | 71.8 / 87.9 |
| rewrite | ProseLens-ModernBERT-L | 14.8 / – | 36.9 / 70.2 | 79.8 / 96.0 | 96.7 / 98.9 |
| rewrite | EditLens-Llama-3B (cal.) | 0.0 / – | 27.9 / 80.8 | 91.9 / 98.7 | 99.6 / 99.9 |
| rewrite | Binoculars (cal.) | 0.1 / – | 1.8 / 15.5 | 22.4 / 36.5 | 40.3 / 50.5 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek.v3-v1:0 | ai | 1,692 | 90.7 / 97.0 | 98.5 / 100.0 | 100.0 / 100.0 | 85.6 / 93.1 | 97.8 / 100.0 | 99.9 / 100.0 | 98.8 / 100.0 | 0.9 / – | 78.3 |
| gemini-2.5-flash | ai | 1,691 | 81.2 / 93.7 | 99.9 / 100.0 | 100.0 / 100.0 | 71.7 / 85.6 | 89.9 / 98.8 | 99.9 / 100.0 | 40.5 / 94.3 | 0.0 / – | 49.0 |
| gemini-2.5-pro | ai | 1,692 | 30.9 / 57.0 | 86.3 / 99.5 | 100.0 / 100.0 | 25.7 / 42.9 | 58.9 / 92.8 | 99.9 / 100.0 | 30.6 / 86.6 | 0.0 / – | 98.9 |
| qwen.qwen3-235b-a22b-2507-v1:0 | ai | 1,692 | 82.7 / 95.0 | 99.1 / 100.0 | 100.0 / 100.0 | 71.6 / 84.8 | 95.0 / 99.8 | 100.0 / 100.0 | 91.1 / 99.6 | 0.0 / – | 76.8 |
| deepseek.v3-v1:0 | rewrite | 3,079 | 1.4 / 4.5 | 0.3 / 4.9 | 57.0 / 91.7 | 3.8 / 8.3 | 2.7 / 20.6 | 40.7 / 87.2 | 59.4 / 93.1 | 0.4 / – | 73.9 |
| gemini-2.5-flash | rewrite | 3,075 | 0.6 / 2.4 | 0.0 / 1.5 | 43.9 / 81.0 | 1.9 / 4.9 | 0.6 / 9.7 | 24.1 / 69.9 | 44.6 / 87.2 | 0.4 / – | 62.5 |
| gemini-2.5-pro | rewrite | 3,082 | 2.2 / 6.4 | 1.4 / 11.8 | 58.4 / 90.5 | 4.6 / 9.7 | 4.3 / 27.2 | 56.7 / 93.0 | 68.6 / 94.6 | 4.5 / – | 76.5 |
| qwen.qwen3-235b-a22b-2507-v1:0 | rewrite | 3,082 | 28.7 / 47.6 | 45.4 / 82.0 | 99.3 / 100.0 | 33.3 / 47.7 | 44.4 / 82.4 | 95.3 / 99.9 | 91.3 / 99.2 | 1.6 / – | 97.9 |

**By conference.** Fire rate % at the 1% cut.

| Conference | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ICLR | ai | 3,243 | 70.2 / 84.8 | 95.6 / 99.9 | 100.0 / 100.0 | 63.3 / 76.8 | 85.1 / 97.9 | 100.0 / 100.0 | 66.8 / 96.0 | 0.3 / – | 77.4 |
| NeurIPS | ai | 3,524 | 72.4 / 86.5 | 96.3 / 99.9 | 100.0 / 100.0 | 63.9 / 76.4 | 85.7 / 97.8 | 99.9 / 100.0 | 63.8 / 94.4 | 0.2 / – | 74.3 |
| ICLR | human | 1,553 | 0.3 / 0.8 | 0.0 / 0.1 | 0.0 / 0.1 | 2.0 / 4.7 | 0.0 / 2.5 | 0.1 / 1.6 | 0.0 / 1.0 | 0.1 / – | 0.0 |
| NeurIPS | human | 1,508 | 0.0 / 0.5 | 0.0 / 0.0 | 0.0 / 0.1 | 1.3 / 2.9 | 0.1 / 2.7 | 0.1 / 1.8 | 0.0 / 0.7 | 0.1 / – | 0.0 |
| ICLR | rewrite | 6,213 | 9.0 / 17.2 | 12.8 / 26.8 | 68.5 / 92.4 | 12.0 / 19.4 | 14.2 / 36.5 | 57.7 / 89.2 | 71.7 / 94.9 | 1.7 / – | 79.3 |
| NeurIPS | rewrite | 6,105 | 7.4 / 13.3 | 10.7 / 23.3 | 60.8 / 89.1 | 9.8 / 15.8 | 11.7 / 33.4 | 50.7 / 85.8 | 60.2 / 92.2 | 1.7 / – | 76.1 |

**By year.** Fire rate % at the 1% cut.

| Year | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | ai | 3,567 | 69.5 / 84.6 | 95.2 / 99.8 | 100.0 / 100.0 | 63.5 / 77.1 | 85.4 / 97.8 | 100.0 / 100.0 | 64.5 / 94.9 | 0.4 / – | 75.7 |
| 2022 | ai | 3,200 | 73.4 / 86.8 | 96.7 / 99.9 | 100.0 / 100.0 | 63.7 / 76.0 | 85.3 / 97.9 | 99.9 / 100.0 | 66.1 / 95.5 | 0.1 / – | 75.8 |
| 2021 | human | 1,558 | 0.0 / 0.3 | 0.0 / 0.0 | 0.0 / 0.1 | 1.1 / 2.7 | 0.0 / 1.8 | 0.1 / 1.5 | 0.0 / 0.8 | 0.1 / – | 0.0 |
| 2022 | human | 1,503 | 0.3 / 1.1 | 0.0 / 0.1 | 0.0 / 0.1 | 2.3 / 5.0 | 0.1 / 3.5 | 0.1 / 1.9 | 0.0 / 1.0 | 0.1 / – | 0.0 |
| 2021 | rewrite | 6,306 | 6.1 / 11.8 | 10.1 / 22.2 | 62.0 / 89.6 | 8.7 / 14.7 | 11.1 / 31.4 | 50.7 / 85.9 | 60.2 / 92.1 | 1.6 / – | 76.7 |
| 2022 | rewrite | 6,012 | 10.4 / 18.9 | 13.6 / 28.0 | 67.5 / 92.0 | 13.2 / 20.8 | 15.0 / 38.8 | 57.9 / 89.3 | 72.1 / 95.0 | 1.8 / – | 78.8 |
