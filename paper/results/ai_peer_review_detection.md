### IntelLabs AI-Peer-Review-Detection-Benchmark: main table

Fire rate % at the 1% cut (global / per-format). TPR on model-idea rows, FPR on human-idea rows.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai | model ideas (TPR) | 8,334 | 73.8 / 85.3 | 84.7 / 94.6 | 98.6 / 99.8 | 85.0 / 91.3 | 88.4 / 97.9 | 96.0 / 99.4 | 94.5 / 98.8 | 66.6 / – | 94.7 |
| human | human ideas (FPR) | 1,622 | 0.1 / 0.4 | 0.0 / 0.0 | 0.0 / 0.7 | 1.0 / 2.7 | 0.0 / 3.1 | 0.1 / 2.7 | 0.1 / 0.6 | 0.7 / – | 0.0 |
| AUC | | | 0.993 | 0.999 | 1.000 | 0.988 | 0.998 | 0.999 | 1.000 | 0.972 | 0.985 |

**Length.** Share under 500 words: ai 78.9%, human 74.7%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai · < 500 | model ideas (TPR) | 6,575 | 70.1 / 82.6 | 82.1 / 93.1 | 98.3 / 99.7 | 82.5 / 89.5 | 85.8 / 97.3 | 95.0 / 99.2 | 94.1 / 98.6 | 63.3 / – | 93.8 |
| ai · >= 500 | model ideas (TPR) | 1,759 | 87.8 / 95.7 | 94.7 / 99.9 | 100.0 / 100.0 | 94.2 / 98.1 | 98.0 / 99.9 | 99.9 / 100.0 | 96.1 / 99.9 | 78.8 / – | 97.8 |
| human · < 500 | human ideas (FPR) | 1,212 | 0.1 / 0.5 | 0.0 / 0.0 | 0.0 / 1.0 | 1.1 / 3.2 | 0.0 / 4.1 | 0.2 / 3.5 | 0.1 / 0.6 | 1.0 / – | 0.0 |
| human · >= 500 | human ideas (FPR) | 410 | 0.0 / 0.2 | 0.0 / 0.0 | 0.0 / 0.0 | 1.0 / 1.2 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.7 | 0.0 / – | 0.0 |

### IntelLabs AI-Peer-Review-Detection-Benchmark: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global / per-format).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| ai | IdeaLens · outline | 41.0 / – | 65.7 / 76.6 | 83.3 / 90.6 | 91.3 / 94.7 |
| ai | IdeaLens · document | 60.4 / – | 75.8 / 91.8 | 92.8 / 97.0 | 97.4 / 99.4 |
| ai | ProseLens | 93.9 / – | 97.2 / 99.4 | 99.6 / 100.0 | 100.0 / 100.0 |
| ai | IdeaLens-ModernBERT-L · outline | 48.7 / – | 77.3 / 82.8 | 92.4 / 96.5 | 98.6 / 99.6 |
| ai | IdeaLens-ModernBERT-L · document | 45.3 / – | 79.5 / 93.5 | 96.3 / 100.0 | 100.0 / 100.0 |
| ai | ProseLens-ModernBERT-L | 86.3 / – | 93.7 / 97.7 | 98.6 / 99.9 | 100.0 / 100.0 |
| ai | EditLens-Llama-3B (cal.) | 0.0 / – | 80.2 / 97.0 | 98.6 / 99.6 | 99.8 / 99.9 |
| ai | Binoculars (cal.) | 39.8 / – | 67.4 / 88.0 | 90.8 / 94.3 | 94.8 / 95.8 |
| human | IdeaLens · outline | 0.0 / – | 0.0 / 0.1 | 0.4 / 0.8 | 1.0 / 3.0 |
| human | IdeaLens · document | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.4 | 0.7 / 4.5 |
| human | ProseLens | 0.0 / – | 0.0 / 0.1 | 0.2 / 2.2 | 3.1 / 5.7 |
| human | IdeaLens-ModernBERT-L · outline | 0.1 / – | 0.4 / 0.8 | 3.7 / 8.8 | 18.9 / 30.6 |
| human | IdeaLens-ModernBERT-L · document | 0.0 / – | 0.0 / 0.2 | 1.5 / 27.3 | 39.6 / 66.3 |
| human | ProseLens-ModernBERT-L | 0.0 / – | 0.1 / 0.2 | 1.2 / 8.9 | 12.9 / 27.0 |
| human | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 0.2 | 0.3 / 2.3 | 4.7 / 9.1 |
| human | Binoculars (cal.) | 0.1 / – | 0.7 / 2.7 | 4.3 / 8.5 | 10.5 / 15.1 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude | ai | 1,669 | 76.8 / 88.6 | 84.7 / 94.9 | 99.3 / 99.9 | 89.9 / 93.8 | 93.4 / 98.3 | 96.9 / 99.9 | 96.5 / 99.0 | 49.3 / – | 98.4 |
| gemini | ai | 1,674 | 50.9 / 73.9 | 78.4 / 94.1 | 98.6 / 100.0 | 71.8 / 84.2 | 80.7 / 96.8 | 96.0 / 99.5 | 96.0 / 99.6 | 74.1 / – | 98.7 |
| gpt4o | ai | 1,671 | 88.6 / 94.5 | 90.5 / 97.2 | 99.2 / 100.0 | 92.2 / 95.3 | 93.5 / 98.9 | 97.0 / 99.6 | 96.2 / 99.5 | 19.1 / – | 88.6 |
| llama | ai | 1,664 | 66.9 / 78.5 | 77.1 / 91.8 | 96.6 / 98.9 | 80.2 / 88.0 | 80.2 / 96.9 | 93.4 / 98.4 | 89.3 / 96.9 | 94.8 / – | 91.6 |
| qwen | ai | 1,656 | 86.0 / 91.2 | 92.9 / 94.7 | 99.5 / 100.0 | 90.9 / 95.0 | 94.0 / 98.6 | 96.7 / 99.5 | 94.5 / 99.2 | 96.1 / – | 96.0 |
| human | human | 1,622 | 0.1 / 0.4 | 0.0 / 0.0 | 0.0 / 0.7 | 1.0 / 2.7 | 0.0 / 3.1 | 0.1 / 2.7 | 0.1 / 0.6 | 0.7 / – | 0.0 |

**By year.** Fire rate % at the 1% cut.

| Year | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | ai | 1,105 | 75.4 / 87.4 | 93.3 / 98.6 | 99.6 / 99.7 | 88.8 / 94.8 | 93.8 / 99.3 | 99.3 / 99.8 | 99.1 / 99.9 | 70.1 / – | 96.4 |
| 2018 | ai | 1,206 | 78.9 / 89.5 | 94.8 / 99.4 | 100.0 / 100.0 | 89.7 / 95.3 | 93.9 / 99.6 | 99.3 / 99.9 | 98.7 / 100.0 | 68.1 / – | 97.6 |
| 2019 | ai | 1,229 | 77.9 / 88.9 | 95.0 / 99.3 | 100.0 / 100.0 | 87.2 / 92.8 | 91.0 / 99.3 | 99.8 / 99.9 | 99.2 / 100.0 | 69.3 / – | 97.9 |
| 2020 | ai | 1,224 | 80.9 / 90.6 | 95.6 / 99.2 | 100.0 / 100.0 | 88.2 / 93.8 | 91.4 / 99.3 | 99.8 / 100.0 | 99.2 / 99.9 | 69.4 / – | 96.9 |
| 2021 | ai | 1,560 | 92.8 / 97.7 | 99.0 / 99.9 | 99.9 / 100.0 | 95.4 / 98.1 | 97.7 / 99.9 | 99.9 / 100.0 | 99.9 / 99.9 | 70.5 / – | 97.3 |
| 2022 | ai | 1,535 | 62.6 / 84.4 | 65.3 / 97.8 | 99.4 / 100.0 | 86.5 / 94.6 | 91.3 / 99.7 | 98.8 / 99.9 | 89.9 / 99.5 | 70.6 / – | 96.7 |
| 2023 | ai | 475 | 2.5 / 9.9 | 0.4 / 20.6 | 78.7 / 96.6 | 11.2 / 29.3 | 6.7 / 70.3 | 39.2 / 90.7 | 46.3 / 81.9 | 14.9 / – | 54.3 |
| 2017 | human | 190 | 0.0 / 0.5 | 0.0 / 0.0 | 0.0 / 0.0 | 1.6 / 4.2 | 0.0 / 3.2 | 0.5 / 2.1 | 0.5 / 1.6 | 1.1 / – | 0.0 |
| 2018 | human | 238 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.8 / 2.5 | 0.0 / 1.3 | 0.0 / 1.3 | 0.0 / 0.0 | 0.8 / – | 0.0 |
| 2019 | human | 242 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.4 | 0.4 / 1.2 | 0.0 / 1.2 | 0.0 / 2.5 | 0.0 / 0.4 | 0.4 / – | 0.0 |
| 2020 | human | 244 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.8 / 1.6 | 0.0 / 1.2 | 0.0 / 0.8 | 0.0 / 0.4 | 0.8 / – | 0.0 |
| 2021 | human | 308 | 0.0 / 0.6 | 0.0 / 0.0 | 0.0 / 0.0 | 1.9 / 2.9 | 0.0 / 1.0 | 0.0 / 0.6 | 0.0 / 1.0 | 0.0 / – | 0.0 |
| 2022 | human | 307 | 0.0 / 0.7 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 1.0 | 0.0 / 0.7 | 0.0 / 1.0 | 0.0 / 0.3 | 1.0 / – | 0.0 |
| 2023 | human | 93 | 1.1 / 2.2 | 0.0 / 0.0 | 0.0 / 11.8 | 3.2 / 11.8 | 0.0 / 32.3 | 1.1 / 24.7 | 0.0 / 1.1 | 2.2 / – | 0.0 |

**Other model x input columns.** Fire rate % at the 1% cut.

| Arm | n | ProseLens · raw outline |
|---|---|---|
| ai | 8,334 | 98.2 / 99.9 |
| human | 1,622 | 83.1 / 98.0 |
