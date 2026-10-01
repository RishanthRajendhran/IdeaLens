### StoryScope: main table

Fire rate % at the 1% cut (global / per-format). TPR on model-idea rows, FPR on human-idea rows.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AI, five StoryScope models | model ideas (TPR) | 6,911 | 97.0 / 98.5 | 99.8 / 99.9 | 99.8 / 99.9 | 86.6 / 91.6 | 97.0 / 99.6 | 99.9 / 99.9 | 21.6 / 91.9 | 9.7 / – | 100.0 |
| human | human ideas (FPR) | 1,380 | 0.1 / 0.7 | 0.0 / 0.0 | 0.0 / 0.0 | 1.6 / 3.2 | 0.0 / 0.4 | 0.4 / 1.6 | 0.0 / 0.1 | 0.0 / – | 0.0 |
| AUC, five models vs human | | | 0.999 | 1.000 | 1.000 | 0.988 | 0.999 | 1.000 | 0.999 | 0.806 | 1.000 |

**Length.** Share under 500 words: AI, five StoryScope models 0.4%, human 0.0%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AI, five StoryScope models · < 500 | model ideas (TPR) | 29 | 72.4 / 82.8 | 89.7 / 93.1 | 89.7 / 93.1 | 17.2 / 48.3 | 24.1 / 86.2 | 86.2 / 93.1 | 65.5 / 86.2 | 10.3 / – | 100.0 |
| AI, five StoryScope models · >= 500 | model ideas (TPR) | 6,882 | 97.1 / 98.5 | 99.9 / 100.0 | 99.8 / 99.9 | 86.9 / 91.7 | 97.3 / 99.6 | 99.9 / 99.9 | 21.5 / 91.9 | 9.7 / – | 100.0 |
| human · >= 500 | human ideas (FPR) | 1,380 | 0.1 / 0.7 | 0.0 / 0.0 | 0.0 / 0.0 | 1.6 / 3.2 | 0.0 / 0.4 | 0.4 / 1.6 | 0.0 / 0.1 | 0.0 / – | 0.0 |

### StoryScope: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global / per-format).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| AI, five StoryScope models | IdeaLens · outline | 92.4 / – | 95.8 / 97.9 | 98.2 / 99.0 | 99.3 / 99.4 |
| AI, five StoryScope models | IdeaLens · document | 99.5 / – | 99.8 / 99.9 | 99.9 / 100.0 | 100.0 / 100.0 |
| AI, five StoryScope models | ProseLens | 99.6 / – | 99.7 / 99.9 | 99.9 / 99.9 | 99.9 / 99.9 |
| AI, five StoryScope models | IdeaLens-ModernBERT-L · outline | 72.9 / – | 82.3 / 87.2 | 91.4 / 94.7 | 96.5 / 97.2 |
| AI, five StoryScope models | IdeaLens-ModernBERT-L · document | 94.9 / – | 96.1 / 99.4 | 98.4 / 99.7 | 99.6 / 99.9 |
| AI, five StoryScope models | ProseLens-ModernBERT-L | 99.4 / – | 99.8 / 99.9 | 99.9 / 99.9 | 99.9 / 100.0 |
| AI, five StoryScope models | EditLens-Llama-3B (cal.) | 0.0 / – | 2.4 / 69.1 | 71.8 / 99.4 | 99.8 / 99.9 |
| AI, five StoryScope models | Binoculars (cal.) | 0.0 / – | 10.8 / 34.6 | 68.4 / 71.7 | 77.8 / 78.4 |
| human | IdeaLens · outline | 0.0 / – | 0.1 / 0.3 | 0.6 / 0.9 | 1.3 / 1.8 |
| human | IdeaLens · document | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.1 | 0.1 / 0.1 |
| human | ProseLens | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 |
| human | IdeaLens-ModernBERT-L · outline | 0.4 / – | 1.1 / 1.8 | 3.1 / 5.1 | 6.8 / 8.5 |
| human | IdeaLens-ModernBERT-L · document | 0.0 / – | 0.0 / 0.2 | 0.0 / 0.8 | 0.5 / 1.7 |
| human | ProseLens-ModernBERT-L | 0.1 / – | 0.2 / 1.2 | 0.8 / 2.5 | 1.9 / 3.7 |
| human | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 0.0 | 0.0 / 1.5 | 5.1 / 19.9 |
| human | Binoculars (cal.) | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.1 | 0.3 / 0.4 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude_sonnet_4_6 | AI, five StoryScope models | 1,383 | 95.5 / 97.4 | 99.9 / 99.9 | 99.4 / 99.8 | 71.1 / 80.5 | 89.9 / 98.6 | 99.7 / 99.8 | 1.7 / 82.6 | 2.6 / – | 99.9 |
| deepseek_v3_2 | AI, five StoryScope models | 1,380 | 98.5 / 99.1 | 99.6 / 99.9 | 99.9 / 99.9 | 95.1 / 97.8 | 99.3 / 99.7 | 99.9 / 99.9 | 37.5 / 98.6 | 2.0 / – | 99.9 |
| gemini | AI, five StoryScope models | 1,380 | 98.0 / 98.9 | 99.9 / 99.9 | 99.9 / 99.9 | 90.8 / 94.5 | 99.7 / 99.9 | 99.9 / 99.9 | 25.1 / 98.3 | 42.4 / – | 99.9 |
| gpt_5_4 | AI, five StoryScope models | 1,384 | 97.4 / 98.9 | 99.9 / 100.0 | 99.7 / 99.9 | 91.8 / 95.4 | 97.0 / 99.7 | 99.9 / 100.0 | 2.7 / 80.7 | 0.1 / – | 100.0 |
| kimi_k2_5 | AI, five StoryScope models | 1,384 | 95.8 / 98.0 | 100.0 / 100.0 | 100.0 / 100.0 | 84.2 / 89.7 | 98.9 / 99.9 | 100.0 / 100.0 | 41.3 / 99.1 | 1.7 / – | 100.0 |

**Other model x input columns.** Fire rate % at the 1% cut.

| Arm | n | IdeaLens · paraphrased outline | IdeaLens-ModernBERT-L · paraphrased outline | IdeaLens-LogisticClassifier · paraphrased outline |
|---|---|---|---|---|
| AI, five StoryScope models | 6,911 | 93.9 / 97.4 | 80.0 / 87.5 | 6.4 / 15.7 |
| human | 1,380 | 0.7 / 2.0 | 2.5 / 5.6 | 0.4 / 2.0 |
