### ARB: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- free_llm: a model writes freely on the topic; llm2l: a model rewrites that free generation; h2l: a model rewrites the human article (ARB labels it AI; by the idea-level rule it carries the person's ideas).
- ARB has no document in the model-ideas, human-prose cell. Every document is under 500 words.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| free_llm | model ideas (TPR) | 6,904 | 97.9 | 97.3 | 100.0 | 95.0 | 94.0 | 99.7 | 98.4 | 90.9 | 99.9 |
| llm2l | model ideas (TPR) | 7,043 | 97.5 | 96.5 | 99.9 | 94.6 | 91.5 | 99.0 | 98.1 | 77.6 | 99.9 |
| h2l | human ideas, AI prose (FPR) | 7,027 | 1.9 | 0.5 | 40.3 | 2.6 | 0.5 | 22.9 | 3.3 | 5.4 | 53.3 |
| human | human ideas (FPR) | 1,752 | 0.5 | 0.0 | 0.1 | 0.6 | 0.0 | 0.5 | 0.1 | 0.2 | 0.0 |
| AUC, model ideas vs human | | | 0.999 | 1.000 | 1.000 | 0.997 | 1.000 | 1.000 | 1.000 | 0.971 | 0.999 |
| AUC, model ideas vs human + h2l | | | 0.998 | 0.999 | 0.991 | 0.994 | 0.997 | 0.978 | 0.997 | 0.948 | 0.983 |

**Length.** Share under 500 words: free_llm 100.0%, llm2l 100.0%, h2l 100.0%, human 99.7%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| free_llm · < 500 | model ideas (TPR) | 6,904 | 97.9 | 97.3 | 100.0 | 95.0 | 94.0 | 99.7 | 98.4 | 90.9 | 99.9 |
| llm2l · < 500 | model ideas (TPR) | 7,043 | 97.5 | 96.5 | 99.9 | 94.6 | 91.5 | 99.0 | 98.1 | 77.6 | 99.9 |
| h2l · < 500 | human ideas, AI prose (FPR) | 7,027 | 1.9 | 0.5 | 40.3 | 2.6 | 0.5 | 22.9 | 3.3 | 5.4 | 53.3 |
| human · < 500 | human ideas (FPR) | 1,747 | 0.5 | 0.0 | 0.1 | 0.6 | 0.0 | 0.5 | 0.1 | 0.2 | 0.0 |
| human · >= 500 | human ideas (FPR) | 5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

### ARB: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| free_llm | IdeaLens · outline | 77.0 | 95.1 | 99.4 | 99.8 |
| free_llm | IdeaLens · document | 59.6 | 89.9 | 99.5 | 100.0 |
| free_llm | ProseLens | 98.7 | 99.8 | 100.0 | 100.0 |
| free_llm | IdeaLens-ModernBERT-L · outline | 68.8 | 89.7 | 98.1 | 99.7 |
| free_llm | IdeaLens-ModernBERT-L · document | 46.9 | 82.2 | 98.8 | 99.9 |
| free_llm | ProseLens-ModernBERT-L | 85.4 | 98.9 | 100.0 | 100.0 |
| free_llm | EditLens-Llama-3B (cal.) | 0.0 | 93.3 | 99.8 | 100.0 |
| free_llm | Binoculars (cal.) | 78.3 | 91.1 | 96.4 | 97.3 |
| llm2l | IdeaLens · outline | 75.9 | 94.4 | 99.2 | 99.8 |
| llm2l | IdeaLens · document | 50.8 | 86.4 | 99.4 | 99.9 |
| llm2l | ProseLens | 96.8 | 99.6 | 100.0 | 100.0 |
| llm2l | IdeaLens-ModernBERT-L · outline | 68.3 | 89.1 | 97.9 | 99.6 |
| llm2l | IdeaLens-ModernBERT-L · document | 40.4 | 77.2 | 98.3 | 99.9 |
| llm2l | ProseLens-ModernBERT-L | 75.4 | 96.7 | 99.9 | 100.0 |
| llm2l | EditLens-Llama-3B (cal.) | 0.0 | 92.0 | 99.6 | 99.9 |
| llm2l | Binoculars (cal.) | 53.7 | 77.9 | 89.4 | 92.7 |
| h2l | IdeaLens · outline | 0.1 | 1.1 | 5.7 | 18.8 |
| h2l | IdeaLens · document | 0.0 | 0.1 | 4.8 | 32.9 |
| h2l | ProseLens | 8.8 | 22.3 | 77.6 | 99.0 |
| h2l | IdeaLens-ModernBERT-L · outline | 0.3 | 1.3 | 6.8 | 23.3 |
| h2l | IdeaLens-ModernBERT-L · document | 0.1 | 0.2 | 3.2 | 39.4 |
| h2l | ProseLens-ModernBERT-L | 4.2 | 12.1 | 55.9 | 94.6 |
| h2l | EditLens-Llama-3B (cal.) | 0.0 | 0.4 | 19.1 | 76.2 |
| h2l | Binoculars (cal.) | 0.7 | 5.7 | 25.1 | 39.6 |
| human | IdeaLens · outline | 0.0 | 0.1 | 1.8 | 7.9 |
| human | IdeaLens · document | 0.0 | 0.0 | 0.1 | 10.7 |
| human | ProseLens | 0.0 | 0.0 | 0.3 | 9.4 |
| human | IdeaLens-ModernBERT-L · outline | 0.1 | 0.3 | 2.2 | 11.9 |
| human | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 0.3 | 13.6 |
| human | ProseLens-ModernBERT-L | 0.1 | 0.3 | 1.6 | 17.9 |
| human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.2 | 1.1 |
| human | Binoculars (cal.) | 0.0 | 0.2 | 5.5 | 14.4 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma2_9b | free_llm | 1,777 | 98.4 | 98.3 | 100.0 | 94.6 | 94.7 | 99.9 | 99.5 | 95.3 | 99.9 |
| llama32_3b | free_llm | 1,712 | 98.7 | 99.5 | 100.0 | 96.0 | 97.3 | 100.0 | 99.0 | 99.9 | 100.0 |
| mistral7b | free_llm | 1,673 | 99.5 | 99.7 | 100.0 | 98.2 | 98.7 | 99.9 | 97.4 | 98.4 | 100.0 |
| qwen25_7b | free_llm | 1,742 | 95.0 | 91.7 | 99.9 | 91.2 | 85.7 | 99.1 | 97.4 | 70.3 | 99.6 |
| gemma2_9b | llm2l | 1,779 | 97.9 | 96.3 | 99.9 | 93.8 | 89.5 | 98.9 | 98.3 | 77.3 | 99.8 |
| llama32_3b | llm2l | 1,769 | 98.1 | 99.2 | 100.0 | 95.4 | 96.4 | 100.0 | 99.8 | 98.8 | 100.0 |
| mistral7b | llm2l | 1,755 | 99.2 | 99.7 | 99.9 | 98.2 | 98.7 | 99.9 | 99.2 | 93.6 | 100.0 |
| qwen25_7b | llm2l | 1,740 | 94.8 | 90.7 | 99.8 | 91.2 | 81.3 | 97.4 | 95.2 | 40.2 | 99.7 |
| gemma2_9b | h2l | 1,766 | 1.8 | 0.2 | 33.9 | 2.8 | 0.3 | 19.2 | 3.8 | 2.8 | 50.1 |
| llama32_3b | h2l | 1,765 | 2.8 | 1.6 | 48.3 | 3.6 | 1.2 | 31.9 | 5.3 | 15.2 | 45.7 |
| mistral7b | h2l | 1,732 | 1.3 | 0.2 | 40.3 | 2.3 | 0.3 | 21.0 | 2.1 | 2.6 | 56.4 |
| qwen25_7b | h2l | 1,764 | 1.9 | 0.1 | 38.6 | 1.8 | 0.2 | 19.4 | 1.9 | 0.8 | 61.0 |

**By domain.** Fire rate % at the 1% cut.

| Domain | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| owt | free_llm | 2,263 | 95.1 | 93.9 | 99.9 | 92.1 | 90.9 | 99.3 | 97.6 | 85.9 | 99.8 |
| wp | free_llm | 2,318 | 99.0 | 99.0 | 100.0 | 94.2 | 95.8 | 99.8 | 98.1 | 97.8 | 99.9 |
| xsum | free_llm | 2,323 | 99.4 | 98.8 | 100.0 | 98.5 | 95.4 | 100.0 | 99.4 | 88.9 | 100.0 |
| owt | llm2l | 2,313 | 95.0 | 92.8 | 99.7 | 91.5 | 88.1 | 98.0 | 96.0 | 71.8 | 99.7 |
| wp | llm2l | 2,354 | 98.3 | 98.6 | 100.0 | 94.2 | 93.5 | 99.4 | 99.2 | 89.8 | 100.0 |
| xsum | llm2l | 2,376 | 99.2 | 98.0 | 100.0 | 98.1 | 92.8 | 99.7 | 99.2 | 71.2 | 100.0 |
| owt | h2l | 2,269 | 0.7 | 0.1 | 27.6 | 1.8 | 0.3 | 13.2 | 2.5 | 3.8 | 60.7 |
| wp | h2l | 2,381 | 4.4 | 1.5 | 72.4 | 5.5 | 1.3 | 47.0 | 6.8 | 11.2 | 41.9 |
| xsum | h2l | 2,377 | 0.6 | 0.0 | 20.2 | 0.5 | 0.0 | 8.0 | 0.4 | 1.1 | 57.7 |
| owt | human | 564 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.4 | 0.2 | 0.4 | 0.0 |
| wp | human | 593 | 1.5 | 0.0 | 0.2 | 1.2 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| xsum | human | 595 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 |
