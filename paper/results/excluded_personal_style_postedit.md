### personal_style_postedit: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Every document is under 500 words (median 150 to 165), below the length every detector is calibrated at: the control FPR is a floor effect. Read the arm-to-arm step.
- The source dataset labels every row human; by the idea-level rule both draft arms carry the model's ideas.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_draft | model ideas (TPR) | 283 | 96.5 | 98.6 | 100.0 | 67.8 | 66.4 | 99.3 | 97.9 | 46.6 | 99.3 |
| postedit | model ideas, person-edited (TPR) | 273 | 85.7 | 88.6 | 91.9 | 62.3 | 47.6 | 90.1 | 78.8 | 26.7 | 93.0 |
| control | human ideas (FPR) | 147 | 27.9 | 25.2 | 22.4 | 20.4 | 5.4 | 16.3 | 6.1 | 6.8 | 30.6 |
| AUC, llm_draft vs control | | | 0.885 | 0.943 | 0.967 | 0.828 | 0.946 | 0.968 | 0.985 | 0.838 | 0.848 |
| AUC, postedit vs control | | | 0.841 | 0.893 | 0.919 | 0.787 | 0.896 | 0.927 | 0.951 | 0.706 | 0.816 |

**Length.** Share under 500 words: llm_draft 100.0%, postedit 100.0%, control 100.0%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_draft · < 500 | model ideas (TPR) | 283 | 96.5 | 98.6 | 100.0 | 67.8 | 66.4 | 99.3 | 97.9 | 46.6 | 99.3 |
| postedit · < 500 | model ideas, person-edited (TPR) | 273 | 85.7 | 88.6 | 91.9 | 62.3 | 47.6 | 90.1 | 78.8 | 26.7 | 93.0 |
| control · < 500 | human ideas (FPR) | 147 | 27.9 | 25.2 | 22.4 | 20.4 | 5.4 | 16.3 | 6.1 | 6.8 | 30.6 |

### personal_style_postedit: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| llm_draft | IdeaLens · outline | 76.3 | 91.9 | 98.6 | 99.3 |
| llm_draft | IdeaLens · document | 90.5 | 97.9 | 99.6 | 100.0 |
| llm_draft | ProseLens | 99.3 | 99.6 | 100.0 | 100.0 |
| llm_draft | IdeaLens-ModernBERT-L · outline | 16.6 | 51.6 | 86.9 | 98.9 |
| llm_draft | IdeaLens-ModernBERT-L · document | 3.5 | 36.4 | 94.0 | 100.0 |
| llm_draft | ProseLens-ModernBERT-L | 91.2 | 98.6 | 100.0 | 100.0 |
| llm_draft | EditLens-Llama-3B (cal.) | 0.0 | 85.2 | 100.0 | 100.0 |
| llm_draft | Binoculars (cal.) | 15.2 | 47.7 | 78.1 | 88.0 |
| postedit | IdeaLens · outline | 63.4 | 81.7 | 91.6 | 97.1 |
| postedit | IdeaLens · document | 71.8 | 85.3 | 94.5 | 98.9 |
| postedit | ProseLens | 90.1 | 90.1 | 93.8 | 96.7 |
| postedit | IdeaLens-ModernBERT-L · outline | 13.9 | 46.5 | 78.8 | 96.0 |
| postedit | IdeaLens-ModernBERT-L · document | 2.2 | 22.0 | 83.2 | 98.2 |
| postedit | ProseLens-ModernBERT-L | 71.4 | 86.1 | 93.4 | 97.8 |
| postedit | EditLens-Llama-3B (cal.) | 0.0 | 49.8 | 90.1 | 93.8 |
| postedit | Binoculars (cal.) | 5.9 | 27.1 | 59.7 | 69.6 |
| control | IdeaLens · outline | 15.0 | 25.2 | 36.7 | 53.7 |
| control | IdeaLens · document | 10.9 | 19.7 | 31.3 | 74.8 |
| control | ProseLens | 18.4 | 20.4 | 27.2 | 34.7 |
| control | IdeaLens-ModernBERT-L · outline | 6.8 | 12.2 | 34.7 | 59.9 |
| control | IdeaLens-ModernBERT-L · document | 0.7 | 1.4 | 17.7 | 68.7 |
| control | ProseLens-ModernBERT-L | 6.1 | 12.2 | 21.1 | 34.0 |
| control | EditLens-Llama-3B (cal.) | 0.0 | 2.0 | 10.9 | 15.0 |
| control | Binoculars (cal.) | 1.4 | 6.8 | 30.6 | 44.9 |

**By scenario.** Fire rate % at the 1% cut.

| Scenario | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| apology | llm_draft | 46 | 100.0 | 100.0 | 100.0 | 71.7 | 84.8 | 100.0 | 100.0 | 67.4 | 100.0 |
| condolence | llm_draft | 36 | 91.7 | 97.2 | 100.0 | 61.1 | 83.3 | 97.2 | 94.4 | 52.8 | 97.2 |
| eulogy | llm_draft | 9 | 100.0 | 100.0 | 100.0 | 77.8 | 88.9 | 100.0 | 100.0 | 55.6 | 100.0 |
| letter | llm_draft | 46 | 95.7 | 100.0 | 100.0 | 45.7 | 21.7 | 100.0 | 95.7 | 41.3 | 100.0 |
| reassurance | llm_draft | 38 | 97.4 | 97.4 | 100.0 | 78.9 | 63.2 | 97.4 | 97.4 | 21.1 | 97.4 |
| speech | llm_draft | 22 | 90.9 | 95.5 | 100.0 | 72.7 | 63.6 | 100.0 | 95.5 | 22.7 | 100.0 |
| thank | llm_draft | 53 | 100.0 | 100.0 | 100.0 | 81.1 | 75.5 | 100.0 | 100.0 | 64.2 | 100.0 |
| wedding | llm_draft | 33 | 93.9 | 97.0 | 100.0 | 60.6 | 69.7 | 100.0 | 100.0 | 33.3 | 100.0 |
| apology | postedit | 43 | 93.0 | 88.4 | 93.0 | 76.7 | 65.1 | 97.7 | 76.7 | 41.9 | 97.7 |
| condolence | postedit | 36 | 80.6 | 88.9 | 91.7 | 55.6 | 61.1 | 91.7 | 69.4 | 33.3 | 91.7 |
| eulogy | postedit | 7 | 85.7 | 85.7 | 85.7 | 42.9 | 42.9 | 85.7 | 57.1 | 0.0 | 85.7 |
| letter | postedit | 46 | 87.0 | 84.8 | 87.0 | 43.5 | 21.7 | 82.6 | 82.6 | 19.6 | 89.1 |
| reassurance | postedit | 38 | 84.2 | 86.8 | 89.5 | 68.4 | 47.4 | 86.8 | 76.3 | 10.5 | 89.5 |
| speech | postedit | 21 | 81.0 | 90.5 | 95.2 | 61.9 | 47.6 | 90.5 | 71.4 | 9.5 | 95.2 |
| thank | postedit | 52 | 84.6 | 92.3 | 92.3 | 71.2 | 48.1 | 92.3 | 86.5 | 44.2 | 94.2 |
| wedding | postedit | 30 | 86.7 | 90.0 | 100.0 | 60.0 | 46.7 | 90.0 | 86.7 | 16.7 | 96.7 |
| apology | control | 30 | 30.0 | 23.3 | 23.3 | 16.7 | 3.3 | 13.3 | 6.7 | 6.7 | 33.3 |
| condolence | control | 24 | 37.5 | 37.5 | 37.5 | 33.3 | 16.7 | 33.3 | 8.3 | 4.2 | 41.7 |
| eulogy | control | 6 | 50.0 | 50.0 | 50.0 | 33.3 | 16.7 | 33.3 | 16.7 | 0.0 | 50.0 |
| letter | control | 18 | 27.8 | 22.2 | 16.7 | 11.1 | 5.6 | 11.1 | 11.1 | 0.0 | 27.8 |
| reassurance | control | 22 | 40.9 | 27.3 | 22.7 | 31.8 | 0.0 | 13.6 | 4.5 | 27.3 | 36.4 |
| speech | control | 13 | 30.8 | 30.8 | 23.1 | 30.8 | 7.7 | 23.1 | 7.7 | 7.7 | 30.8 |
| thank | control | 24 | 4.2 | 8.3 | 4.2 | 4.2 | 0.0 | 4.2 | 0.0 | 0.0 | 12.5 |
| wedding | control | 10 | 10.0 | 20.0 | 20.0 | 10.0 | 0.0 | 10.0 | 0.0 | 0.0 | 20.0 |
