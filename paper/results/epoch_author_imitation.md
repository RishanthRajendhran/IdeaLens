### Epoch author imitation: main table

Fire rate % at the 1% cut (global / per-format). TPR on model-idea rows, FPR on human-idea rows.

- style_transfer (a model imitating the author from five passages) is mixed, AI-leaning: it is reported in the shared P(AI) table, not as a TPR; its fire rates are in the appendix.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| vanilla | model ideas (TPR) | 297 | 97.6 / 98.7 | 100.0 / 99.0 | 100.0 / 100.0 | 65.7 / 62.6 | 85.2 / 91.9 | 99.7 / 99.7 | 93.9 / 82.5 | 3.0 / – | 100.0 |
| human | human ideas (FPR) | 495 | 0.0 / 0.8 | 0.0 / 0.0 | 0.0 / 1.6 | 0.0 / 0.4 | 0.0 / 0.2 | 0.0 / 2.4 | 0.0 / 5.5 | 0.0 / – | 0.0 |
| AUC, vanilla vs human | | | 1.000 | 1.000 | 1.000 | 0.985 | 1.000 | 1.000 | 1.000 | 0.836 | 1.000 |

**Length.** Share under 500 words: vanilla 40.4%, human 49.5%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| vanilla · < 500 | model ideas (TPR) | 120 | 95.8 / 97.5 | 100.0 / 97.5 | 100.0 / 100.0 | 68.3 / 65.0 | 87.5 / 88.3 | 100.0 / 99.2 | 99.2 / 85.8 | 5.8 / – | 100.0 |
| vanilla · >= 500 | model ideas (TPR) | 177 | 98.9 / 99.4 | 100.0 / 100.0 | 100.0 / 100.0 | 63.8 / 61.0 | 83.6 / 94.4 | 99.4 / 100.0 | 90.4 / 80.2 | 1.1 / – | 100.0 |
| human · < 500 | human ideas (FPR) | 245 | 0.0 / 1.6 | 0.0 / 0.0 | 0.0 / 2.0 | 0.0 / 0.4 | 0.0 / 0.0 | 0.0 / 3.3 | 0.0 / 6.5 | 0.0 / – | 0.0 |
| human · >= 500 | human ideas (FPR) | 250 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 1.2 | 0.0 / 0.4 | 0.0 / 0.4 | 0.0 / 1.6 | 0.0 / 4.4 | 0.0 / – | 0.0 |

**Shared P(AI) table, Epoch rows.** P(AI) % (1 - P(human); Pangram: its derived P(AI)); the statistic is named per row where a level shows more than the mean.

| Level | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| vanilla · mean | model ideas | 297 | 97.9 | 99.7 | 100.0 | 86.6 | 94.1 | 99.7 | – | – | 100.0 |
| vanilla · median | model ideas | 297 | 99.5 | 99.9 | 100.0 | 97.8 | 99.8 | 100.0 | – | – | 100.0 |
| style_transfer · mean | mixed, AI-leaning | 297 | 68.5 | 82.8 | 90.2 | 38.3 | 44.9 | 86.9 | – | – | 97.1 |
| style_transfer · median | mixed, AI-leaning | 297 | 84.3 | 98.7 | 99.9 | 23.6 | 34.0 | 99.2 | – | – | 100.0 |
| style_transfer · min | mixed, AI-leaning | 297 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 |
| style_transfer · max | mixed, AI-leaning | 297 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | – | – | 100.0 |
| human · mean | human ideas | 495 | 4.7 | 0.3 | 0.1 | 6.4 | 0.1 | 0.4 | – | – | 0.0 |
| human · median | human ideas | 495 | 1.5 | 0.1 | 0.0 | 1.5 | 0.1 | 0.0 | – | – | 0.0 |

### Epoch author imitation: appendix

**Rows reported in the appendix only.** Fire rate % at the 1% cut.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| style_transfer | mixed, AI-leaning (fire rate) | 297 | 48.1 / 55.2 | 70.0 / 72.1 | 92.9 / 91.9 | 12.8 / 14.8 | 25.9 / 45.1 | 81.8 / 85.9 | 32.0 / 54.5 | 0.0 / – | 97.0 |

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global / per-format).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| vanilla | IdeaLens · outline | 73.1 / – | 93.9 / 96.0 | 99.3 / 99.0 | 100.0 / 100.0 |
| vanilla | IdeaLens · document | 96.3 / – | 99.0 / 99.0 | 100.0 / 99.3 | 100.0 / 100.0 |
| vanilla | ProseLens | 100.0 / – | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 |
| vanilla | IdeaLens-ModernBERT-L · outline | 21.5 / – | 51.2 / 49.5 | 79.5 / 76.8 | 92.6 / 91.6 |
| vanilla | IdeaLens-ModernBERT-L · document | 66.0 / – | 77.4 / 88.2 | 93.3 / 96.0 | 99.3 / 99.3 |
| vanilla | ProseLens-ModernBERT-L | 92.6 / – | 99.3 / 99.7 | 100.0 / 100.0 | 100.0 / 100.0 |
| vanilla | EditLens-Llama-3B (cal.) | 0.0 / – | 66.7 / 61.6 | 100.0 / 99.0 | 100.0 / 100.0 |
| vanilla | Binoculars (cal.) | 0.0 / – | 3.4 / 4.0 | 33.3 / 21.9 | 52.2 / 49.2 |
| human | IdeaLens · outline | 0.0 / – | 0.0 / 0.6 | 0.8 / 1.2 | 3.2 / 6.1 |
| human | IdeaLens · document | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.4 | 0.4 / 1.6 |
| human | ProseLens | 0.0 / – | 0.0 / 0.2 | 0.2 / 5.9 | 8.9 / 26.7 |
| human | IdeaLens-ModernBERT-L · outline | 0.0 / – | 0.0 / 0.0 | 0.6 / 1.6 | 5.1 / 7.3 |
| human | IdeaLens-ModernBERT-L · document | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.8 | 0.6 / 7.5 |
| human | ProseLens-ModernBERT-L | 0.0 / – | 0.0 / 1.0 | 1.0 / 6.7 | 6.1 / 20.4 |
| human | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 1.4 | 1.6 / 17.2 | 26.9 / 30.9 |
| human | Binoculars (cal.) | 0.0 / – | 0.0 / 0.0 | 0.2 / 1.2 | 4.6 / 6.5 |
| style_transfer | IdeaLens · outline | 22.6 / – | 41.8 / 45.1 | 62.0 / 64.6 | 81.8 / 80.1 |
| style_transfer | IdeaLens · document | 46.5 / – | 61.3 / 64.3 | 84.5 / 77.4 | 93.3 / 91.9 |
| style_transfer | ProseLens | 80.1 / – | 89.2 / 90.9 | 95.3 / 96.3 | 98.3 / 98.7 |
| style_transfer | IdeaLens-ModernBERT-L · outline | 3.0 / – | 7.4 / 9.1 | 22.2 / 24.2 | 40.7 / 40.7 |
| style_transfer | IdeaLens-ModernBERT-L · document | 14.8 / – | 19.2 / 37.7 | 39.1 / 54.5 | 74.7 / 72.1 |
| style_transfer | ProseLens-ModernBERT-L | 45.1 / – | 72.7 / 79.1 | 92.9 / 90.9 | 97.0 / 97.3 |
| style_transfer | EditLens-Llama-3B (cal.) | 0.0 / – | 7.7 / 45.8 | 70.0 / 63.6 | 92.3 / 82.2 |
| style_transfer | Binoculars (cal.) | 0.0 / – | 0.0 / 2.4 | 11.1 / 12.5 | 28.3 / 28.3 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude | vanilla | 99 | 97.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 66.7 / 67.7 | 86.9 / 93.9 | 99.0 / 100.0 | 97.0 / 85.9 | 3.0 / – | 100.0 |
| gemini | vanilla | 99 | 97.0 / 97.0 | 100.0 / 97.0 | 100.0 / 100.0 | 65.7 / 63.6 | 90.9 / 89.9 | 100.0 / 99.0 | 98.0 / 85.9 | 5.1 / – | 100.0 |
| gpt | vanilla | 99 | 99.0 / 99.0 | 100.0 / 100.0 | 100.0 / 100.0 | 64.6 / 56.6 | 77.8 / 91.9 | 100.0 / 100.0 | 86.9 / 75.8 | 1.0 / – | 100.0 |
| claude | style_transfer | 99 | 58.6 / 63.6 | 73.7 / 79.8 | 93.9 / 96.0 | 15.2 / 16.2 | 28.3 / 50.5 | 84.8 / 90.9 | 21.2 / 54.5 | 0.0 / – | 100.0 |
| gemini | style_transfer | 99 | 45.5 / 49.5 | 62.6 / 63.6 | 92.9 / 86.9 | 14.1 / 18.2 | 35.4 / 52.5 | 78.8 / 78.8 | 57.6 / 59.6 | 0.0 / – | 91.9 |
| gpt | style_transfer | 99 | 40.4 / 52.5 | 73.7 / 72.7 | 91.9 / 92.9 | 9.1 / 10.1 | 14.1 / 32.3 | 81.8 / 87.9 | 17.2 / 49.5 | 0.0 / – | 99.0 |

**By genre.** Fire rate % at the 1% cut.

| Genre | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| blog | vanilla | 99 | 99.0 / 99.0 | 100.0 / 99.0 | 100.0 / 100.0 | 67.7 / 53.5 | 93.9 / 89.9 | 100.0 / 100.0 | 100.0 / 62.6 | 7.1 / – | 100.0 |
| fiction | vanilla | 99 | 96.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 | 48.5 / 59.6 | 72.7 / 97.0 | 99.0 / 100.0 | 81.8 / 100.0 | 0.0 / – | 100.0 |
| scientific | vanilla | 99 | 98.0 / 97.0 | 100.0 / 98.0 | 100.0 / 100.0 | 80.8 / 74.7 | 88.9 / 88.9 | 100.0 / 99.0 | 100.0 / 84.8 | 2.0 / – | 100.0 |
| blog | human | 165 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.6 | 0.0 / 0.0 | 0.0 / 1.2 | 0.0 / 1.2 | 0.0 / – | 0.0 |
| fiction | human | 165 | 0.0 / 2.4 | 0.0 / 0.0 | 0.0 / 4.8 | 0.0 / 0.6 | 0.0 / 0.6 | 0.0 / 6.1 | 0.0 / 15.2 | 0.0 / – | 0.0 |
| scientific | human | 165 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / – | 0.0 |
| blog | style_transfer | 99 | 52.5 / 51.5 | 79.8 / 74.7 | 98.0 / 93.9 | 19.2 / 18.2 | 36.4 / 42.4 | 86.9 / 78.8 | 32.3 / 36.4 | 0.0 / – | 100.0 |
| fiction | style_transfer | 99 | 64.6 / 81.8 | 94.9 / 100.0 | 96.0 / 100.0 | 11.1 / 21.2 | 29.3 / 77.8 | 89.9 / 99.0 | 46.5 / 100.0 | 0.0 / – | 100.0 |
| scientific | style_transfer | 99 | 27.3 / 32.3 | 35.4 / 41.4 | 84.8 / 81.8 | 8.1 / 5.1 | 12.1 / 15.2 | 68.7 / 79.8 | 17.2 / 27.3 | 0.0 / – | 90.9 |

**Commercial verdicts shipped with the corpus** (identical documents; share of each arm).

| Arm | n | GPTZero: ai | GPTZero: ai or mixed | Originality.ai: ai | Pangram (as shipped): AI | Pangram (as shipped): AI or Mixed |
|---|---|---|---|---|---|---|
| vanilla | 297 | 99.3 | 99.7 | 99.7 | 100.0 | 100.0 |
| style_transfer | 297 | 89.2 | 91.2 | 82.2 | 89.9 | 93.9 |
| human | 495 | 0.0 | 0.0 | 3.8 | 0.0 | 0.0 |
