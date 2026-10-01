### ELLIPSE: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Essays by English-language learners; every row is human, so every flag is a false positive. Bands 1 and 5 hold 8 and 28 essays.
- The surface-bias hypothesis predicts FPR rising as proficiency falls; see the band and sub-score tables in the appendix.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all essays | human ideas (FPR) | 3,909 | 0.4 | 0.0 | 0.0 | 3.6 | 0.0 | 0.1 | 0.0 | 0.3 | 0.0 |

**Length.** Share under 500 words: all essays 70.5%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all essays · < 500 | human ideas (FPR) | 2,757 | 0.4 | 0.0 | 0.0 | 3.9 | 0.0 | 0.1 | 0.0 | 0.4 | 0.0 |
| all essays · >= 500 | human ideas (FPR) | 1,152 | 0.3 | 0.0 | 0.0 | 3.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 |

### ELLIPSE: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| all essays | IdeaLens · outline | 0.0 | 0.3 | 1.4 | 9.8 |
| all essays | IdeaLens · document | 0.0 | 0.0 | 0.0 | 16.2 |
| all essays | ProseLens | 0.0 | 0.0 | 0.0 | 5.5 |
| all essays | IdeaLens-ModernBERT-L · outline | 0.1 | 1.7 | 9.6 | 27.8 |
| all essays | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 0.0 | 5.7 |
| all essays | ProseLens-ModernBERT-L | 0.0 | 0.0 | 0.8 | 8.9 |
| all essays | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.0 | 0.1 |
| all essays | Binoculars (cal.) | 0.0 | 0.4 | 5.5 | 14.2 |

**By proficiency band.** Fire rate % at the 1% cut.

| Proficiency band | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 (lowest) | all essays | 8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 2 | all essays | 1,052 | 0.3 | 0.0 | 0.0 | 2.4 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 |
| 3 | all essays | 1,386 | 0.2 | 0.0 | 0.0 | 3.5 | 0.0 | 0.1 | 0.0 | 0.6 | 0.0 |
| 4 | all essays | 1,435 | 0.7 | 0.0 | 0.0 | 4.7 | 0.0 | 0.1 | 0.0 | 0.1 | 0.0 |
| 5 (highest) | all essays | 28 | 0.0 | 0.0 | 0.0 | 3.6 | 0.0 | 3.6 | 0.0 | 0.0 | 0.0 |

**By grade.** Fire rate % at the 1% cut.

| Grade | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | all essays | 214 | 0.9 | 0.0 | 0.0 | 3.3 | 0.0 | 0.5 | 0.0 | 0.0 | 0.0 |
| 11 | all essays | 1,377 | 0.2 | 0.0 | 0.0 | 3.6 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 |
| 12 | all essays | 1,319 | 0.3 | 0.0 | 0.0 | 2.8 | 0.0 | 0.1 | 0.0 | 0.2 | 0.0 |
| 8 | all essays | 973 | 0.7 | 0.0 | 0.0 | 5.0 | 0.0 | 0.2 | 0.0 | 0.5 | 0.0 |
| 9 | all essays | 26 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

**By grammar score.** Fire rate % at the 1% cut.

| Grammar score | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.0 | all essays | 7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 1.5 | all essays | 20 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 2.0 | all essays | 544 | 0.2 | 0.0 | 0.0 | 2.6 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 |
| 2.5 | all essays | 854 | 0.4 | 0.0 | 0.0 | 3.3 | 0.0 | 0.1 | 0.0 | 0.2 | 0.0 |
| 3.0 | all essays | 994 | 0.3 | 0.0 | 0.0 | 3.0 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 |
| 3.5 | all essays | 880 | 0.3 | 0.0 | 0.0 | 4.4 | 0.0 | 0.1 | 0.0 | 0.5 | 0.0 |
| 4.0 | all essays | 447 | 0.9 | 0.0 | 0.0 | 6.0 | 0.0 | 0.2 | 0.0 | 0.2 | 0.0 |
| 4.5 | all essays | 134 | 1.5 | 0.0 | 0.0 | 2.2 | 0.0 | 0.7 | 0.0 | 0.0 | 0.0 |
| 5.0 | all essays | 29 | 0.0 | 0.0 | 0.0 | 3.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

**By vocabulary score.** Fire rate % at the 1% cut.

| Vocabulary score | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.0 | all essays | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 1.5 | all essays | 13 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 2.0 | all essays | 124 | 0.0 | 0.0 | 0.0 | 2.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 2.5 | all essays | 528 | 0.0 | 0.0 | 0.0 | 2.5 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 |
| 3.0 | all essays | 1,502 | 0.3 | 0.0 | 0.0 | 3.5 | 0.0 | 0.1 | 0.0 | 0.5 | 0.0 |
| 3.5 | all essays | 1,007 | 0.5 | 0.0 | 0.0 | 4.5 | 0.0 | 0.1 | 0.0 | 0.3 | 0.0 |
| 4.0 | all essays | 577 | 0.7 | 0.0 | 0.0 | 4.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 4.5 | all essays | 115 | 0.9 | 0.0 | 0.0 | 1.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 5.0 | all essays | 41 | 2.4 | 0.0 | 0.0 | 7.3 | 0.0 | 2.4 | 0.0 | 0.0 | 0.0 |
