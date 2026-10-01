### PeerPrism: main table

Fire rate % at the 1% cut (global / per-format). TPR on model-idea rows, FPR on human-idea rows.

- Labels follow the benchmark's own idea-origin field: rewritten and extract_regenerate carry the reviewer's ideas (extract_regenerate: ideas extracted from the review, a new review written from them); expanded and hybrid are mixed and reported in the P(AI) table.
- Human FPR rises with review year for every detector (2024 reviews may contain model-written text); see the year table.
- As released, 544 of the 4,800 transformed reviews are byte-identical to the human review they transform (expanded 228 of 900, hybrid 152 of 900, extract_regenerate 135 of 1,500, rewritten 29 of 1,500; mostly gpt-5, also o4-mini and llama-4-scout). They are failed upstream generations, not copies: the call raised and the pipeline wrote the human review in its place, or the reasoning model returned empty text and the loader fell back to the human review. They are evaluated as released; every detector fires on them at 0 to 3.5%, which lowers each transformed row (e.g. extract_regenerate, IdeaLens outline 61.0% with them, 66.9% without).

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| synthetic_reviews | model ideas (TPR) | 798 | 63.3 / 82.1 | 86.7 / 97.9 | 99.0 / 99.6 | 57.8 / 70.9 | 69.7 / 96.9 | 97.2 / 99.0 | 33.5 / 91.6 | 15.0 / – | 87.1 |
| rewritten | human ideas, AI prose (FPR) | 1,500 | 7.6 / 14.8 | 8.8 / 27.8 | 76.3 / 92.1 | 11.5 / 18.7 | 15.7 / 44.3 | 69.7 / 90.9 | 58.0 / 89.7 | 4.7 / – | 76.3 |
| extract_regenerate | human ideas, AI prose (FPR) | 1,499 | 61.0 / 77.9 | 81.9 / 90.2 | 90.6 / 90.9 | 74.5 / 82.2 | 86.1 / 90.5 | 90.7 / 90.9 | 86.6 / 91.1 | 16.5 / – | 89.3 |
| human | human ideas (FPR) | 671 | 1.0 / 2.1 | 1.5 / 3.3 | 2.8 / 3.9 | 3.1 / 4.5 | 2.5 / 6.7 | 2.4 / 4.8 | 1.5 / 11.0 | 0.7 / – | 0.4 |
| AUC, synthetic vs human | | | 0.983 | 0.993 | 0.995 | 0.954 | 0.977 | 0.991 | 0.966 | 0.647 | 0.970 |
| AUC, synthetic vs human + rewritten + extract_regenerate | | | 0.769 | 0.755 | 0.715 | 0.682 | 0.648 | 0.594 | 0.385 | 0.474 | 0.684 |

**Length.** Share under 500 words: synthetic_reviews 51.5%, rewritten 69.0%, extract_regenerate 37.5%, human 65.7%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| synthetic_reviews · < 500 | model ideas (TPR) | 411 | 60.1 / 80.3 | 76.2 / 95.9 | 98.1 / 99.3 | 61.1 / 72.3 | 67.4 / 96.1 | 94.6 / 98.1 | 35.0 / 96.4 | 29.2 / – | 83.0 |
| synthetic_reviews · >= 500 | model ideas (TPR) | 387 | 66.7 / 84.0 | 97.9 / 100.0 | 100.0 / 100.0 | 54.3 / 69.5 | 72.1 / 97.7 | 100.0 / 100.0 | 31.8 / 86.6 | 0.0 / – | 91.5 |
| rewritten · < 500 | human ideas, AI prose (FPR) | 1,035 | 8.3 / 16.2 | 10.1 / 30.0 | 77.5 / 93.9 | 13.0 / 21.0 | 18.6 / 51.2 | 71.1 / 92.3 | 59.5 / 91.4 | 6.2 / – | 79.7 |
| rewritten · >= 500 | human ideas, AI prose (FPR) | 465 | 6.0 / 11.6 | 5.8 / 23.0 | 73.5 / 88.2 | 8.0 / 13.5 | 9.5 / 28.8 | 66.7 / 87.7 | 54.6 / 85.8 | 1.5 / – | 68.6 |
| extract_regenerate · < 500 | human ideas, AI prose (FPR) | 562 | 59.3 / 78.3 | 78.6 / 91.5 | 92.0 / 92.5 | 76.5 / 85.8 | 85.8 / 92.0 | 92.0 / 92.5 | 89.9 / 93.4 | 35.8 / – | 91.5 |
| extract_regenerate · >= 500 | human ideas, AI prose (FPR) | 937 | 62.1 / 77.6 | 83.8 / 89.4 | 89.8 / 90.0 | 73.3 / 80.0 | 86.3 / 89.6 | 89.9 / 90.0 | 84.6 / 89.8 | 5.0 / – | 87.9 |
| human · < 500 | human ideas (FPR) | 441 | 1.1 / 2.3 | 1.8 / 3.6 | 3.4 / 4.5 | 4.3 / 5.7 | 3.2 / 7.9 | 2.9 / 5.4 | 2.0 / 12.9 | 1.1 / – | 0.7 |
| human · >= 500 | human ideas (FPR) | 230 | 0.9 / 1.7 | 0.9 / 2.6 | 1.7 / 2.6 | 0.9 / 2.2 | 1.3 / 4.3 | 1.3 / 3.5 | 0.4 / 7.4 | 0.0 / – | 0.0 |

**Shared P(AI) table, PeerPrism rows.** P(AI) % (1 - P(human); Pangram: its derived P(AI)); the statistic is named per row where a level shows more than the mean.

| Level | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| synthetic_reviews · mean | model ideas | 798 | 81.2 | 94.0 | 97.7 | 86.6 | 91.8 | 97.3 | – | – | 81.0 |
| synthetic_reviews · median | model ideas | 798 | 92.8 | 98.8 | 99.7 | 96.6 | 98.5 | 99.7 | – | – | 95.7 |
| hybrid · mean | mixed | 866 | 62.8 | 74.8 | 77.2 | 70.0 | 73.2 | 77.4 | – | – | 62.5 |
| hybrid · median | mixed | 866 | 82.5 | 98.7 | 99.7 | 92.7 | 98.5 | 99.8 | – | – | 83.3 |
| hybrid · min | mixed | 866 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 |
| hybrid · max | mixed | 866 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | – | – | 100.0 |
| expanded · mean | mixed, human-leaning | 846 | 39.8 | 57.9 | 59.2 | 48.6 | 49.8 | 61.0 | – | – | 54.8 |
| expanded · median | mixed, human-leaning | 846 | 23.8 | 86.9 | 95.6 | 45.5 | 46.8 | 98.2 | – | – | 64.1 |
| expanded · min | mixed, human-leaning | 846 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 |
| expanded · max | mixed, human-leaning | 846 | 99.9 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | – | – | 100.0 |
| human · mean | human ideas | 671 | 4.0 | 2.9 | 2.7 | 19.4 | 10.5 | 3.1 | – | – | 1.2 |
| human · median | human ideas | 671 | 0.2 | 0.0 | 0.0 | 7.9 | 1.8 | 0.0 | – | – | 0.0 |

### PeerPrism: appendix

**Rows reported in the appendix only.** Fire rate % at the 1% cut.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| expanded | mixed, human-leaning (fire rate) | 846 | 24.7 / 38.3 | 47.6 / 63.6 | 60.9 / 66.4 | 21.6 / 30.9 | 30.7 / 50.7 | 58.3 / 67.1 | 26.0 / 59.1 | 8.3 / – | 58.4 |
| hybrid | mixed (fire rate) | 866 | 46.9 / 62.5 | 66.9 / 78.6 | 79.0 / 80.9 | 47.3 / 58.0 | 59.4 / 74.5 | 75.6 / 80.8 | 41.3 / 75.2 | 11.2 / – | 64.0 |

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global / per-format).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| synthetic_reviews | IdeaLens · outline | 20.7 / – | 50.1 / 64.5 | 80.3 / 90.0 | 93.1 / 96.2 |
| synthetic_reviews | IdeaLens · document | 43.7 / – | 72.1 / 94.6 | 96.5 / 99.0 | 99.5 / 99.6 |
| synthetic_reviews | ProseLens | 95.2 / – | 97.7 / 99.2 | 99.6 / 100.0 | 100.0 / 100.0 |
| synthetic_reviews | IdeaLens-ModernBERT-L · outline | 18.5 / – | 44.9 / 52.0 | 76.2 / 87.8 | 95.2 / 98.5 |
| synthetic_reviews | IdeaLens-ModernBERT-L · document | 25.9 / – | 51.1 / 85.2 | 93.4 / 100.0 | 100.0 / 100.0 |
| synthetic_reviews | ProseLens-ModernBERT-L | 64.4 / – | 93.1 / 98.0 | 99.0 / 99.9 | 100.0 / 100.0 |
| synthetic_reviews | EditLens-Llama-3B (cal.) | 0.0 / – | 4.0 / 73.1 | 87.1 / 99.1 | 99.7 / 99.9 |
| synthetic_reviews | Binoculars (cal.) | 11.8 / – | 15.2 / 19.8 | 23.2 / 31.0 | 33.3 / 37.7 |
| rewritten | IdeaLens · outline | 1.2 / – | 5.2 / 8.5 | 13.4 / 23.7 | 24.7 / 34.7 |
| rewritten | IdeaLens · document | 2.3 / – | 5.3 / 17.9 | 20.1 / 37.9 | 40.9 / 52.9 |
| rewritten | ProseLens | 46.9 / – | 64.9 / 86.7 | 90.5 / 96.3 | 97.1 / 97.7 |
| rewritten | IdeaLens-ModernBERT-L · outline | 1.7 / – | 6.5 / 10.0 | 21.7 / 33.4 | 47.4 / 60.4 |
| rewritten | IdeaLens-ModernBERT-L · document | 3.4 / – | 9.1 / 25.5 | 36.0 / 76.0 | 82.0 / 92.3 |
| rewritten | ProseLens-ModernBERT-L | 28.0 / – | 54.7 / 79.6 | 87.0 / 96.5 | 97.1 / 97.7 |
| rewritten | EditLens-Llama-3B (cal.) | 0.0 / – | 21.6 / 75.0 | 86.3 / 97.7 | 98.2 / 98.3 |
| rewritten | Binoculars (cal.) | 1.7 / – | 4.9 / 10.7 | 13.3 / 18.9 | 21.3 / 28.1 |
| extract_regenerate | IdeaLens · outline | 20.2 / – | 49.9 / 65.0 | 74.4 / 84.0 | 85.1 / 88.5 |
| extract_regenerate | IdeaLens · document | 55.9 / – | 74.0 / 87.8 | 88.7 / 90.9 | 90.9 / 91.1 |
| extract_regenerate | ProseLens | 87.6 / – | 90.5 / 90.8 | 90.9 / 90.9 | 90.9 / 90.9 |
| extract_regenerate | IdeaLens-ModernBERT-L · outline | 35.3 / – | 63.0 / 70.7 | 83.3 / 87.7 | 90.1 / 91.9 |
| extract_regenerate | IdeaLens-ModernBERT-L · document | 64.4 / – | 80.5 / 89.0 | 90.3 / 92.0 | 92.9 / 94.9 |
| extract_regenerate | ProseLens-ModernBERT-L | 85.6 / – | 90.0 / 90.8 | 90.9 / 91.2 | 91.4 / 92.3 |
| extract_regenerate | EditLens-Llama-3B (cal.) | 0.0 / – | 66.2 / 89.2 | 90.8 / 91.9 | 92.1 / 92.7 |
| extract_regenerate | Binoculars (cal.) | 9.7 / – | 16.9 / 34.3 | 41.3 / 55.3 | 58.2 / 65.4 |
| human | IdeaLens · outline | 0.6 / – | 0.9 / 1.3 | 1.9 / 3.3 | 4.3 / 7.3 |
| human | IdeaLens · document | 0.4 / – | 0.9 / 2.8 | 3.0 / 3.6 | 4.0 / 5.2 |
| human | ProseLens | 1.5 / – | 2.4 / 3.4 | 3.9 / 4.9 | 5.4 / 7.0 |
| human | IdeaLens-ModernBERT-L · outline | 0.4 / – | 1.6 / 2.2 | 5.1 / 9.5 | 20.1 / 29.2 |
| human | IdeaLens-ModernBERT-L · document | 1.0 / – | 1.6 / 4.0 | 5.1 / 33.1 | 47.2 / 69.0 |
| human | ProseLens-ModernBERT-L | 1.0 / – | 1.8 / 2.8 | 3.9 / 9.5 | 13.7 / 29.1 |
| human | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 3.6 | 7.9 / 20.9 | 25.9 / 34.4 |
| human | Binoculars (cal.) | 0.4 / – | 0.9 / 2.5 | 4.0 / 6.9 | 8.3 / 10.7 |
| expanded | IdeaLens · outline | 6.4 / – | 18.0 / 26.4 | 35.3 / 46.9 | 49.1 / 56.0 |
| expanded | IdeaLens · document | 25.9 / – | 38.9 / 56.6 | 59.1 / 66.4 | 66.7 / 68.3 |
| expanded | ProseLens | 52.4 / – | 57.6 / 64.3 | 65.1 / 68.2 | 69.3 / 70.1 |
| expanded | IdeaLens-ModernBERT-L · outline | 5.4 / – | 14.9 / 19.3 | 33.7 / 44.3 | 54.6 / 62.9 |
| expanded | IdeaLens-ModernBERT-L · document | 14.7 / – | 24.2 / 40.4 | 46.7 / 69.4 | 76.5 / 85.6 |
| expanded | ProseLens-ModernBERT-L | 42.6 / – | 53.3 / 61.6 | 64.3 / 69.9 | 71.3 / 76.6 |
| expanded | EditLens-Llama-3B (cal.) | 0.0 / – | 5.0 / 41.4 | 54.8 / 73.0 | 76.6 / 79.6 |
| expanded | Binoculars (cal.) | 3.9 / – | 8.3 / 13.7 | 16.0 / 22.7 | 25.7 / 32.3 |
| hybrid | IdeaLens · outline | 22.5 / – | 40.2 / 50.1 | 60.4 / 70.8 | 71.9 / 77.1 |
| hybrid | IdeaLens · document | 46.1 / – | 59.5 / 74.6 | 75.9 / 80.9 | 80.9 / 82.2 |
| hybrid | ProseLens | 71.5 / – | 76.6 / 80.4 | 80.5 / 81.9 | 82.3 / 82.4 |
| hybrid | IdeaLens-ModernBERT-L · outline | 19.1 / – | 38.8 / 44.0 | 61.0 / 68.1 | 75.3 / 80.5 |
| hybrid | IdeaLens-ModernBERT-L · document | 35.8 / – | 50.5 / 66.7 | 71.9 / 85.7 | 87.2 / 92.8 |
| hybrid | ProseLens-ModernBERT-L | 59.6 / – | 70.8 / 78.5 | 80.0 / 83.1 | 83.8 / 86.4 |
| hybrid | EditLens-Llama-3B (cal.) | 0.0 / – | 18.9 / 56.7 | 72.2 / 83.7 | 85.7 / 87.0 |
| hybrid | Binoculars (cal.) | 5.9 / – | 11.4 / 15.4 | 16.5 / 20.4 | 22.6 / 27.9 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-4.5 | synthetic_reviews | 134 | 64.2 / 85.8 | 96.3 / 100.0 | 100.0 / 100.0 | 48.5 / 72.4 | 78.4 / 97.8 | 100.0 / 100.0 | 38.1 / 87.3 | 0.0 / – | 88.8 |
| deepseek/deepseek-r1 | synthetic_reviews | 134 | 60.4 / 80.6 | 81.3 / 99.3 | 100.0 / 100.0 | 56.0 / 67.9 | 59.0 / 97.0 | 99.3 / 100.0 | 42.5 / 100.0 | 0.0 / – | 94.0 |
| gemini-2.5-flash | synthetic_reviews | 133 | 45.9 / 69.9 | 95.5 / 100.0 | 100.0 / 100.0 | 46.6 / 56.4 | 63.2 / 97.7 | 100.0 / 100.0 | 39.1 / 94.0 | 0.0 / – | 85.7 |
| gpt-5 | synthetic_reviews | 133 | 84.2 / 91.7 | 94.0 / 100.0 | 100.0 / 100.0 | 66.9 / 76.7 | 66.2 / 94.7 | 99.2 / 100.0 | 21.8 / 79.7 | 0.0 / – | 99.2 |
| meta-llama/llama-4-scout | synthetic_reviews | 131 | 48.9 / 69.5 | 59.5 / 88.5 | 93.9 / 97.7 | 54.2 / 65.6 | 66.4 / 93.9 | 84.7 / 93.9 | 14.5 / 89.3 | 91.6 / – | 63.4 |
| o4-mini | synthetic_reviews | 133 | 75.9 / 94.7 | 93.2 / 99.2 | 100.0 / 100.0 | 74.4 / 86.5 | 85.0 / 100.0 | 100.0 / 100.0 | 44.4 / 99.2 | 0.0 / – | 91.0 |
| claude-haiku-4-5 | rewritten | 250 | 9.6 / 18.0 | 6.8 / 37.6 | 99.2 / 100.0 | 14.0 / 22.4 | 20.0 / 58.0 | 94.4 / 100.0 | 86.4 / 99.2 | 0.0 / – | 96.4 |
| deepseek/deepseek-r1 | rewritten | 250 | 9.2 / 19.2 | 13.2 / 41.2 | 93.2 / 98.8 | 13.2 / 22.0 | 22.4 / 55.2 | 90.4 / 99.6 | 72.8 / 97.2 | 0.0 / – | 86.4 |
| gemini-2.5-flash | rewritten | 250 | 7.6 / 14.4 | 6.0 / 26.4 | 94.4 / 99.6 | 8.8 / 20.0 | 12.8 / 42.8 | 80.8 / 95.6 | 63.6 / 96.4 | 0.0 / – | 87.6 |
| gpt-5 | rewritten | 250 | 0.8 / 1.2 | 0.4 / 3.6 | 29.6 / 69.6 | 3.2 / 6.0 | 5.2 / 21.2 | 16.0 / 59.2 | 12.4 / 60.4 | 0.0 / – | 46.8 |
| llama-4-scout | rewritten | 1 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / – | 0.0 |
| meta-llama/llama-4-scout | rewritten | 250 | 14.8 / 27.6 | 22.8 / 44.4 | 68.4 / 88.8 | 19.6 / 28.0 | 23.6 / 52.8 | 73.2 / 95.6 | 80.0 / 97.6 | 28.4 / – | 56.8 |
| o4-mini | rewritten | 249 | 3.6 / 8.4 | 3.6 / 13.7 | 73.1 / 96.4 | 10.0 / 13.7 | 10.4 / 35.7 | 63.9 / 95.6 | 32.9 / 87.6 | 0.0 / – | 83.9 |
| claude-haiku-4.5 | extract_regenerate | 250 | 79.2 / 94.0 | 98.8 / 98.8 | 98.8 / 98.8 | 89.2 / 94.0 | 98.8 / 98.8 | 98.8 / 98.8 | 94.8 / 98.0 | 7.2 / – | 98.8 |
| deepseek-r1 | extract_regenerate | 250 | 78.8 / 92.8 | 97.2 / 97.6 | 97.6 / 97.6 | 84.0 / 91.6 | 96.4 / 97.6 | 97.6 / 97.6 | 96.0 / 97.6 | 0.4 / – | 97.6 |
| gemini-2.5-flash | extract_regenerate | 250 | 51.2 / 70.8 | 90.0 / 97.2 | 97.6 / 98.0 | 66.8 / 77.2 | 87.6 / 96.4 | 98.0 / 98.0 | 87.6 / 97.2 | 6.8 / – | 92.0 |
| gpt-5 | extract_regenerate | 249 | 40.2 / 60.6 | 45.4 / 73.1 | 75.1 / 75.5 | 63.5 / 69.1 | 71.5 / 75.9 | 75.1 / 75.5 | 73.1 / 76.7 | 0.4 / – | 74.3 |
| llama-4-scout | extract_regenerate | 250 | 55.2 / 70.4 | 79.6 / 86.8 | 86.8 / 87.6 | 68.8 / 79.2 | 75.6 / 86.4 | 86.4 / 87.6 | 83.6 / 88.4 | 84.4 / – | 85.2 |
| o4-mini | extract_regenerate | 250 | 61.6 / 78.4 | 80.0 / 87.6 | 87.6 / 88.0 | 74.8 / 82.0 | 86.8 / 88.0 | 88.0 / 88.0 | 84.4 / 88.8 | 0.0 / – | 87.6 |
| claude-haiku-4.5 | expanded | 116 | 21.6 / 40.5 | 75.9 / 94.0 | 98.3 / 100.0 | 10.3 / 22.4 | 29.3 / 64.7 | 98.3 / 100.0 | 25.9 / 83.6 | 0.0 / – | 96.6 |
| deepseek-r1 | expanded | 150 | 59.3 / 84.0 | 97.3 / 100.0 | 100.0 / 100.0 | 48.7 / 62.7 | 78.7 / 97.3 | 100.0 / 100.0 | 60.7 / 98.0 | 0.0 / – | 100.0 |
| gemini-2.5-flash | expanded | 150 | 10.0 / 20.0 | 31.3 / 74.7 | 63.3 / 81.3 | 8.0 / 12.7 | 12.7 / 34.7 | 46.7 / 78.7 | 10.0 / 56.7 | 0.0 / – | 80.0 |
| gpt-5 | expanded | 149 | 2.7 / 3.4 | 2.0 / 3.4 | 2.7 / 4.7 | 4.7 / 6.0 | 2.7 / 4.0 | 2.7 / 5.4 | 2.0 / 10.1 | 0.0 / – | 0.7 |
| llama-4-scout | expanded | 131 | 42.0 / 58.0 | 51.9 / 75.6 | 67.9 / 79.4 | 43.5 / 55.0 | 42.7 / 71.0 | 70.2 / 86.3 | 50.4 / 74.8 | 52.7 / – | 38.2 |
| o4-mini | expanded | 150 | 14.0 / 26.7 | 34.0 / 42.0 | 42.0 / 42.0 | 14.7 / 27.3 | 19.3 / 38.0 | 42.0 / 42.0 | 10.0 / 38.7 | 0.7 / – | 40.7 |
| claude-haiku-4.5 | hybrid | 121 | 50.4 / 73.6 | 88.4 / 100.0 | 100.0 / 100.0 | 30.6 / 45.5 | 68.6 / 90.9 | 100.0 / 100.0 | 18.2 / 85.1 | 0.0 / – | 100.0 |
| deepseek-r1 | hybrid | 150 | 76.0 / 94.7 | 94.0 / 99.3 | 100.0 / 100.0 | 74.0 / 87.3 | 91.3 / 99.3 | 100.0 / 100.0 | 86.0 / 98.7 | 0.0 / – | 100.0 |
| gemini-2.5-flash | hybrid | 149 | 17.4 / 43.0 | 72.5 / 94.0 | 94.6 / 96.0 | 29.5 / 40.9 | 53.7 / 79.2 | 89.3 / 97.3 | 20.8 / 81.9 | 0.0 / – | 38.9 |
| gpt-5 | hybrid | 148 | 2.7 / 4.1 | 3.4 / 4.7 | 4.7 / 4.7 | 4.7 / 7.4 | 4.7 / 8.1 | 3.4 / 4.7 | 3.4 / 12.8 | 0.0 / – | 2.7 |
| llama-4-scout | hybrid | 148 | 48.6 / 69.6 | 52.7 / 83.8 | 84.5 / 94.6 | 58.1 / 73.6 | 48.0 / 77.7 | 71.6 / 92.6 | 52.7 / 83.8 | 65.5 / – | 54.7 |
| o4-mini | hybrid | 150 | 86.0 / 91.3 | 93.3 / 93.3 | 93.3 / 93.3 | 83.3 / 90.0 | 90.7 / 94.0 | 93.3 / 93.3 | 62.0 / 90.0 | 0.0 / – | 93.3 |

**By venue.** Fire rate % at the 1% cut.

| Venue | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ICLR | synthetic_reviews | 406 | 67.5 / 85.2 | 84.5 / 97.5 | 98.3 / 99.3 | 65.5 / 76.6 | 77.1 / 97.0 | 97.0 / 98.8 | 42.9 / 91.9 | 14.3 / – | 87.2 |
| NeurIPS | synthetic_reviews | 392 | 58.9 / 78.8 | 89.0 / 98.2 | 99.7 / 100.0 | 49.7 / 65.1 | 62.0 / 96.7 | 97.4 / 99.2 | 23.7 / 91.3 | 15.8 / – | 87.0 |
| ICLR | rewritten | 756 | 7.0 / 13.2 | 8.6 / 26.1 | 78.3 / 92.5 | 8.7 / 16.0 | 13.1 / 39.4 | 69.7 / 90.5 | 48.9 / 85.2 | 6.0 / – | 78.0 |
| NeurIPS | rewritten | 744 | 8.2 / 16.4 | 9.0 / 29.6 | 74.2 / 91.8 | 14.2 / 21.4 | 18.4 / 49.2 | 69.8 / 91.3 | 67.2 / 94.2 | 3.5 / – | 74.5 |
| ICLR | extract_regenerate | 755 | 59.7 / 78.1 | 81.2 / 90.9 | 91.4 / 91.5 | 73.1 / 81.1 | 86.1 / 91.0 | 91.3 / 91.5 | 87.0 / 90.9 | 16.3 / – | 89.9 |
| NeurIPS | extract_regenerate | 744 | 62.4 / 77.6 | 82.5 / 89.5 | 89.8 / 90.3 | 75.9 / 83.3 | 86.2 / 90.1 | 90.1 / 90.3 | 86.2 / 91.4 | 16.8 / – | 88.6 |
| ICLR | human | 318 | 0.3 / 1.3 | 0.6 / 0.6 | 0.6 / 1.3 | 2.2 / 2.5 | 0.6 / 2.8 | 0.9 / 2.2 | 0.3 / 0.9 | 0.0 / – | 0.0 |
| NeurIPS | human | 353 | 1.7 / 2.8 | 2.3 / 5.7 | 4.8 / 6.2 | 4.0 / 6.2 | 4.2 / 10.2 | 3.7 / 7.1 | 2.5 / 20.1 | 1.4 / – | 0.8 |
| ICLR | expanded | 429 | 22.6 / 36.6 | 44.8 / 62.0 | 59.7 / 66.0 | 19.1 / 27.7 | 27.7 / 46.4 | 56.9 / 68.5 | 20.3 / 52.4 | 7.7 / – | 58.7 |
| NeurIPS | expanded | 417 | 26.9 / 40.0 | 50.6 / 65.2 | 62.1 / 66.9 | 24.2 / 34.1 | 33.8 / 55.2 | 59.7 / 65.7 | 31.9 / 65.9 | 8.9 / – | 58.0 |
| ICLR | hybrid | 435 | 44.1 / 60.5 | 64.6 / 77.7 | 77.0 / 80.2 | 45.7 / 56.8 | 56.3 / 73.8 | 75.6 / 80.2 | 37.5 / 72.0 | 9.9 / – | 64.4 |
| NeurIPS | hybrid | 431 | 49.7 / 64.5 | 69.1 / 79.6 | 81.0 / 81.7 | 49.0 / 59.2 | 62.4 / 75.2 | 75.6 / 81.4 | 45.2 / 78.4 | 12.5 / – | 63.6 |

**By year.** Fire rate % at the 1% cut.

| Year | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | synthetic_reviews | 204 | 49.0 / 71.6 | 75.5 / 93.6 | 98.0 / 99.0 | 49.0 / 60.3 | 55.9 / 93.1 | 94.1 / 97.1 | 32.4 / 96.1 | 13.2 / – | 92.6 |
| 2022 | synthetic_reviews | 200 | 66.0 / 86.5 | 90.0 / 100.0 | 99.5 / 100.0 | 69.0 / 82.5 | 77.0 / 98.5 | 100.0 / 100.0 | 40.5 / 90.5 | 16.5 / – | 91.0 |
| 2023 | synthetic_reviews | 196 | 69.9 / 82.1 | 91.3 / 99.5 | 99.5 / 100.0 | 56.1 / 67.9 | 74.0 / 99.0 | 96.4 / 100.0 | 32.7 / 92.9 | 14.8 / – | 83.2 |
| 2024 | synthetic_reviews | 198 | 68.7 / 88.4 | 90.4 / 98.5 | 99.0 / 99.5 | 57.1 / 73.2 | 72.2 / 97.0 | 98.5 / 99.0 | 28.3 / 86.9 | 15.7 / – | 81.3 |
| 2021 | rewritten | 378 | 3.2 / 9.3 | 4.0 / 20.1 | 75.7 / 91.5 | 4.5 / 8.7 | 5.6 / 28.8 | 68.5 / 90.7 | 48.1 / 86.5 | 4.0 / – | 78.8 |
| 2022 | rewritten | 378 | 8.2 / 16.7 | 9.3 / 25.4 | 73.3 / 90.7 | 16.4 / 23.5 | 18.8 / 43.1 | 69.6 / 91.5 | 58.5 / 88.6 | 6.1 / – | 71.4 |
| 2023 | rewritten | 372 | 7.0 / 14.5 | 9.1 / 29.8 | 78.8 / 93.8 | 12.6 / 24.5 | 17.5 / 54.8 | 70.7 / 90.6 | 65.9 / 90.9 | 5.1 / – | 75.3 |
| 2024 | rewritten | 372 | 12.1 / 18.8 | 12.9 / 36.0 | 77.4 / 92.5 | 12.4 / 18.0 | 21.2 / 50.5 | 70.2 / 90.6 | 59.7 / 92.7 | 3.8 / – | 79.6 |
| 2021 | extract_regenerate | 378 | 57.9 / 74.6 | 78.3 / 89.9 | 90.5 / 90.5 | 72.5 / 81.5 | 84.9 / 90.5 | 90.5 / 90.5 | 86.5 / 90.2 | 15.6 / – | 89.7 |
| 2022 | extract_regenerate | 378 | 55.0 / 74.3 | 78.0 / 87.3 | 88.4 / 88.9 | 70.6 / 78.6 | 82.0 / 87.8 | 88.6 / 88.9 | 84.1 / 89.4 | 15.9 / – | 87.0 |
| 2023 | extract_regenerate | 372 | 59.1 / 76.9 | 83.3 / 89.5 | 90.1 / 90.3 | 72.8 / 79.8 | 85.2 / 90.1 | 90.1 / 90.3 | 85.8 / 91.7 | 16.1 / – | 88.2 |
| 2024 | extract_regenerate | 371 | 72.2 / 85.7 | 87.9 / 94.1 | 93.5 / 94.1 | 82.2 / 88.9 | 92.5 / 93.8 | 93.5 / 94.1 | 90.0 / 93.3 | 18.6 / – | 92.2 |
| 2021 | human | 163 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.6 / 0.6 | 0.0 / 1.8 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / – | 0.0 |
| 2022 | human | 159 | 0.0 / 1.9 | 0.0 / 0.0 | 0.0 / 0.0 | 4.4 / 7.5 | 0.0 / 5.7 | 0.0 / 1.3 | 0.0 / 5.7 | 0.0 / – | 0.0 |
| 2023 | human | 180 | 0.6 / 1.1 | 0.0 / 1.7 | 1.1 / 2.2 | 1.7 / 2.8 | 1.1 / 5.0 | 0.0 / 2.8 | 1.1 / 18.3 | 0.0 / – | 0.0 |
| 2024 | human | 169 | 3.6 / 5.3 | 5.9 / 11.2 | 10.1 / 13.0 | 5.9 / 7.1 | 8.9 / 14.2 | 9.5 / 14.8 | 4.7 / 18.9 | 3.0 / – | 1.8 |
| 2021 | expanded | 212 | 21.2 / 33.5 | 41.0 / 61.3 | 59.9 / 67.0 | 21.7 / 31.6 | 23.1 / 46.2 | 58.5 / 66.5 | 24.5 / 53.8 | 9.0 / – | 59.9 |
| 2022 | expanded | 216 | 22.7 / 34.7 | 44.9 / 59.3 | 54.2 / 59.7 | 23.1 / 30.1 | 28.2 / 46.3 | 50.5 / 61.6 | 22.7 / 51.4 | 6.9 / – | 51.9 |
| 2023 | expanded | 211 | 24.6 / 42.2 | 52.1 / 65.4 | 65.4 / 70.1 | 19.9 / 30.8 | 33.6 / 55.9 | 62.6 / 69.7 | 26.1 / 66.8 | 9.5 / – | 62.1 |
| 2024 | expanded | 207 | 30.4 / 43.0 | 52.7 / 68.6 | 64.3 / 69.1 | 21.7 / 30.9 | 38.2 / 54.6 | 61.8 / 71.0 | 30.9 / 64.7 | 7.7 / – | 59.9 |
| 2021 | hybrid | 217 | 42.9 / 56.2 | 61.3 / 75.1 | 78.3 / 81.1 | 47.5 / 53.5 | 52.5 / 68.7 | 72.8 / 80.6 | 41.0 / 69.6 | 11.5 / – | 59.9 |
| 2022 | hybrid | 220 | 44.1 / 60.0 | 60.9 / 76.4 | 76.4 / 78.6 | 48.2 / 59.1 | 56.8 / 73.2 | 73.2 / 78.6 | 40.0 / 73.2 | 10.5 / – | 62.7 |
| 2023 | hybrid | 215 | 50.2 / 66.5 | 73.5 / 81.4 | 80.5 / 81.9 | 48.4 / 60.9 | 64.7 / 79.1 | 77.2 / 81.9 | 40.9 / 81.4 | 12.6 / – | 67.4 |
| 2024 | hybrid | 214 | 50.5 / 67.3 | 72.0 / 81.8 | 80.8 / 82.2 | 45.3 / 58.4 | 63.6 / 77.1 | 79.4 / 82.2 | 43.5 / 76.6 | 10.3 / – | 65.9 |
