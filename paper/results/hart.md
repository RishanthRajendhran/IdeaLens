### HART: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- HART's level-2 task (is the content AI?) is our label rule; their best published level-2 AUROC is 0.855, beside the level-2 AUC rows below.
- ModernBERT reading the document is '–' off English (English-only model). ai_human_edited (248, English) is in the appendix.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| English · clear AI (ai_plain) | model ideas (TPR) | 3,953 | 96.5 | 97.7 | 100.0 | 84.5 | 85.1 | 99.6 | 96.1 | 67.9 | 100.0 |
| English · attacked AI (humanized) | model ideas (TPR) | 3,592 | 84.6 | 82.0 | 93.5 | 71.4 | 59.6 | 86.3 | 71.0 | 10.4 | 94.9 |
| English · rephrase (h2l_rephrase) | human ideas, AI prose (FPR) | 3,904 | 4.9 | 4.9 | 44.5 | 5.9 | 5.0 | 34.6 | 20.1 | 6.9 | 42.8 |
| English · clear human | human ideas (FPR) | 3,922 | 0.6 | 0.2 | 0.4 | 1.1 | 0.1 | 0.4 | 0.3 | 0.3 | 0.1 |
| non-English · clear AI (ai_plain) | model ideas (TPR) | 3,877 | 93.1 | 89.9 | 99.1 | 85.2 | – | – | 89.5 | 27.1 | 99.7 |
| non-English · attacked AI (humanized) | model ideas (TPR) | 3,536 | 79.2 | 72.3 | 87.4 | 71.3 | – | – | 64.5 | 2.5 | 88.6 |
| non-English · rephrase (h2l_rephrase) | human ideas, AI prose (FPR) | 3,800 | 1.8 | 0.7 | 12.8 | 1.3 | – | – | 3.9 | 0.7 | 14.9 |
| non-English · clear human | human ideas (FPR) | 3,806 | 0.6 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.2 | 0.0 |
| AUC, level 2, English (model-idea arms vs human + rephrase) | | | 0.978 | 0.979 | 0.964 | 0.958 | 0.957 | 0.949 | 0.934 | 0.689 | 0.971 |
| AUC, level 2, non-English | | | 0.970 | 0.975 | 0.973 | 0.964 | – | – | 0.949 | 0.675 | 0.967 |

**Length.** Share under 500 words: English · clear AI (ai_plain) 87.1%, English · attacked AI (humanized) 88.1%, English · rephrase (h2l_rephrase) 89.9%, English · clear human 88.4%, non-English · clear AI (ai_plain) 85.5%, non-English · attacked AI (humanized) 85.9%, non-English · rephrase (h2l_rephrase) 88.9%, non-English · clear human 89.6%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| English · clear AI (ai_plain) · < 500 | model ideas (TPR) | 3,444 | 96.3 | 97.4 | 100.0 | 84.1 | 84.4 | 99.5 | 96.7 | 67.5 | 100.0 |
| English · clear AI (ai_plain) · >= 500 | model ideas (TPR) | 509 | 98.0 | 99.6 | 100.0 | 87.0 | 89.6 | 100.0 | 91.6 | 70.7 | 100.0 |
| English · attacked AI (humanized) · < 500 | model ideas (TPR) | 3,165 | 82.8 | 80.1 | 92.7 | 69.3 | 58.8 | 85.2 | 71.6 | 9.7 | 94.2 |
| English · attacked AI (humanized) · >= 500 | model ideas (TPR) | 427 | 97.4 | 96.7 | 100.0 | 87.4 | 65.6 | 94.8 | 66.5 | 16.2 | 100.0 |
| English · rephrase (h2l_rephrase) · < 500 | human ideas, AI prose (FPR) | 3,510 | 5.3 | 5.3 | 47.6 | 6.4 | 5.4 | 36.7 | 21.6 | 7.5 | 45.0 |
| English · rephrase (h2l_rephrase) · >= 500 | human ideas, AI prose (FPR) | 394 | 1.3 | 1.3 | 16.5 | 1.8 | 1.0 | 16.0 | 6.6 | 1.0 | 23.6 |
| English · clear human · < 500 | human ideas (FPR) | 3,466 | 0.7 | 0.1 | 0.3 | 1.1 | 0.1 | 0.4 | 0.3 | 0.3 | 0.1 |
| English · clear human · >= 500 | human ideas (FPR) | 456 | 0.4 | 0.2 | 0.4 | 1.5 | 0.2 | 0.4 | 0.4 | 0.0 | 0.0 |
| non-English · clear AI (ai_plain) · < 500 | model ideas (TPR) | 3,316 | 92.7 | 88.6 | 99.0 | 83.9 | – | – | 90.0 | 26.9 | 99.7 |
| non-English · clear AI (ai_plain) · >= 500 | model ideas (TPR) | 561 | 95.4 | 97.9 | 99.8 | 92.7 | – | – | 85.9 | 28.3 | 100.0 |
| non-English · attacked AI (humanized) · < 500 | model ideas (TPR) | 3,036 | 77.7 | 69.8 | 86.3 | 68.9 | – | – | 65.7 | 2.6 | 87.5 |
| non-English · attacked AI (humanized) · >= 500 | model ideas (TPR) | 500 | 88.6 | 87.6 | 94.0 | 85.6 | – | – | 57.2 | 1.6 | 95.4 |
| non-English · rephrase (h2l_rephrase) · < 500 | human ideas, AI prose (FPR) | 3,380 | 2.0 | 0.7 | 13.6 | 1.3 | – | – | 4.1 | 0.7 | 14.4 |
| non-English · rephrase (h2l_rephrase) · >= 500 | human ideas, AI prose (FPR) | 420 | 0.5 | 0.7 | 6.0 | 0.7 | – | – | 1.9 | 0.0 | 19.0 |
| non-English · clear human · < 500 | human ideas (FPR) | 3,410 | 0.6 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.2 | 0.0 |
| non-English · clear human · >= 500 | human ideas (FPR) | 396 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |

### HART: appendix

**Rows reported in the appendix only.** Fire rate % at the 1% cut.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| English · ai_human_edited (a person rewrote model content) | model ideas, human prose (TPR) | 248 | 95.6 | 93.5 | 99.6 | 83.1 | 72.6 | 92.3 | 69.4 | 22.6 | 100.0 |

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| English · clear AI (ai_plain) | IdeaLens · outline | 74.4 | 92.6 | 98.8 | 99.6 |
| English · clear AI (ai_plain) | IdeaLens · document | 71.1 | 91.8 | 99.5 | 99.9 |
| English · clear AI (ai_plain) | ProseLens | 99.2 | 99.8 | 100.0 | 100.0 |
| English · clear AI (ai_plain) | IdeaLens-ModernBERT-L · outline | 44.1 | 74.2 | 93.6 | 98.6 |
| English · clear AI (ai_plain) | IdeaLens-ModernBERT-L · document | 27.6 | 68.3 | 95.6 | 99.7 |
| English · clear AI (ai_plain) | ProseLens-ModernBERT-L | 82.1 | 98.6 | 100.0 | 100.0 |
| English · clear AI (ai_plain) | EditLens-Llama-3B (cal.) | 0.0 | 88.1 | 98.6 | 99.5 |
| English · clear AI (ai_plain) | Binoculars (cal.) | 42.1 | 68.5 | 82.5 | 85.7 |
| English · attacked AI (humanized) | IdeaLens · outline | 61.1 | 80.0 | 89.0 | 92.5 |
| English · attacked AI (humanized) | IdeaLens · document | 47.4 | 70.6 | 89.9 | 95.1 |
| English · attacked AI (humanized) | ProseLens | 87.4 | 91.4 | 95.2 | 97.6 |
| English · attacked AI (humanized) | IdeaLens-ModernBERT-L · outline | 36.8 | 61.7 | 81.9 | 91.4 |
| English · attacked AI (humanized) | IdeaLens-ModernBERT-L · document | 20.4 | 42.5 | 77.8 | 94.5 |
| English · attacked AI (humanized) | ProseLens-ModernBERT-L | 61.6 | 81.2 | 92.3 | 97.0 |
| English · attacked AI (humanized) | EditLens-Llama-3B (cal.) | 0.0 | 49.6 | 82.2 | 91.7 |
| English · attacked AI (humanized) | Binoculars (cal.) | 1.3 | 11.0 | 28.9 | 36.3 |
| English · rephrase (h2l_rephrase) | IdeaLens · outline | 0.8 | 2.9 | 9.7 | 21.0 |
| English · rephrase (h2l_rephrase) | IdeaLens · document | 0.8 | 2.4 | 13.0 | 38.6 |
| English · rephrase (h2l_rephrase) | ProseLens | 25.2 | 36.1 | 57.7 | 80.3 |
| English · rephrase (h2l_rephrase) | IdeaLens-ModernBERT-L · outline | 0.7 | 3.4 | 11.6 | 29.8 |
| English · rephrase (h2l_rephrase) | IdeaLens-ModernBERT-L · document | 0.3 | 2.3 | 13.8 | 56.2 |
| English · rephrase (h2l_rephrase) | ProseLens-ModernBERT-L | 7.7 | 22.0 | 55.7 | 81.9 |
| English · rephrase (h2l_rephrase) | EditLens-Llama-3B (cal.) | 0.0 | 7.9 | 41.2 | 78.0 |
| English · rephrase (h2l_rephrase) | Binoculars (cal.) | 1.3 | 7.1 | 24.7 | 37.7 |
| English · clear human | IdeaLens · outline | 0.2 | 0.3 | 1.8 | 7.5 |
| English · clear human | IdeaLens · document | 0.1 | 0.1 | 0.4 | 7.5 |
| English · clear human | ProseLens | 0.2 | 0.3 | 0.7 | 6.6 |
| English · clear human | IdeaLens-ModernBERT-L · outline | 0.1 | 0.5 | 3.3 | 15.2 |
| English · clear human | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 0.6 | 21.6 |
| English · clear human | ProseLens-ModernBERT-L | 0.1 | 0.2 | 2.1 | 15.6 |
| English · clear human | EditLens-Llama-3B (cal.) | 0.0 | 0.1 | 1.0 | 4.0 |
| English · clear human | Binoculars (cal.) | 0.1 | 0.3 | 2.8 | 7.8 |
| non-English · clear AI (ai_plain) | IdeaLens · outline | 72.2 | 88.4 | 97.0 | 99.0 |
| non-English · clear AI (ai_plain) | IdeaLens · document | 46.2 | 75.2 | 98.1 | 99.9 |
| non-English · clear AI (ai_plain) | ProseLens | 94.7 | 98.2 | 99.9 | 99.9 |
| non-English · clear AI (ai_plain) | IdeaLens-ModernBERT-L · outline | 49.1 | 76.9 | 93.5 | 98.9 |
| non-English · clear AI (ai_plain) | IdeaLens-ModernBERT-L · document | – | – | – | – |
| non-English · clear AI (ai_plain) | ProseLens-ModernBERT-L | – | – | – | – |
| non-English · clear AI (ai_plain) | EditLens-Llama-3B (cal.) | 0.0 | 60.5 | 96.6 | 98.7 |
| non-English · clear AI (ai_plain) | Binoculars (cal.) | 7.3 | 27.8 | 51.3 | 57.9 |
| non-English · attacked AI (humanized) | IdeaLens · outline | 57.4 | 74.3 | 84.9 | 89.5 |
| non-English · attacked AI (humanized) | IdeaLens · document | 30.3 | 55.3 | 84.7 | 91.2 |
| non-English · attacked AI (humanized) | ProseLens | 79.0 | 85.2 | 90.1 | 94.3 |
| non-English · attacked AI (humanized) | IdeaLens-ModernBERT-L · outline | 38.0 | 62.1 | 79.5 | 88.2 |
| non-English · attacked AI (humanized) | IdeaLens-ModernBERT-L · document | – | – | – | – |
| non-English · attacked AI (humanized) | ProseLens-ModernBERT-L | – | – | – | – |
| non-English · attacked AI (humanized) | EditLens-Llama-3B (cal.) | 0.0 | 28.3 | 80.1 | 90.0 |
| non-English · attacked AI (humanized) | Binoculars (cal.) | 0.0 | 2.6 | 15.4 | 25.2 |
| non-English · rephrase (h2l_rephrase) | IdeaLens · outline | 0.1 | 0.8 | 5.8 | 16.3 |
| non-English · rephrase (h2l_rephrase) | IdeaLens · document | 0.0 | 0.1 | 4.6 | 22.4 |
| non-English · rephrase (h2l_rephrase) | ProseLens | 2.6 | 6.3 | 28.3 | 65.3 |
| non-English · rephrase (h2l_rephrase) | IdeaLens-ModernBERT-L · outline | 0.1 | 0.6 | 4.4 | 17.1 |
| non-English · rephrase (h2l_rephrase) | IdeaLens-ModernBERT-L · document | – | – | – | – |
| non-English · rephrase (h2l_rephrase) | ProseLens-ModernBERT-L | – | – | – | – |
| non-English · rephrase (h2l_rephrase) | EditLens-Llama-3B (cal.) | 0.0 | 0.6 | 17.4 | 56.3 |
| non-English · rephrase (h2l_rephrase) | Binoculars (cal.) | 0.0 | 0.7 | 6.7 | 16.0 |
| non-English · clear human | IdeaLens · outline | 0.0 | 0.1 | 2.8 | 11.4 |
| non-English · clear human | IdeaLens · document | 0.0 | 0.0 | 0.0 | 6.5 |
| non-English · clear human | ProseLens | 0.0 | 0.0 | 0.2 | 10.3 |
| non-English · clear human | IdeaLens-ModernBERT-L · outline | 0.0 | 0.1 | 1.5 | 10.0 |
| non-English · clear human | IdeaLens-ModernBERT-L · document | – | – | – | – |
| non-English · clear human | ProseLens-ModernBERT-L | – | – | – | – |
| non-English · clear human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.2 | 7.3 |
| non-English · clear human | Binoculars (cal.) | 0.0 | 0.2 | 2.2 | 5.9 |
| English · ai_human_edited (a person rewrote model content) | IdeaLens · outline | 67.3 | 89.9 | 98.8 | 99.6 |
| English · ai_human_edited (a person rewrote model content) | IdeaLens · document | 37.1 | 73.8 | 99.6 | 100.0 |
| English · ai_human_edited (a person rewrote model content) | ProseLens | 92.7 | 98.4 | 100.0 | 100.0 |
| English · ai_human_edited (a person rewrote model content) | IdeaLens-ModernBERT-L · outline | 44.8 | 72.2 | 94.0 | 98.4 |
| English · ai_human_edited (a person rewrote model content) | IdeaLens-ModernBERT-L · document | 22.6 | 54.4 | 92.3 | 100.0 |
| English · ai_human_edited (a person rewrote model content) | ProseLens-ModernBERT-L | 51.6 | 84.7 | 99.6 | 100.0 |
| English · ai_human_edited (a person rewrote model content) | EditLens-Llama-3B (cal.) | 0.0 | 39.5 | 89.5 | 98.4 |
| English · ai_human_edited (a person rewrote model content) | Binoculars (cal.) | 8.5 | 22.6 | 52.0 | 62.5 |

**By arm.** Fire rate % at the 1% cut.

| Arm | Description | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai_plain | English · clear AI (ai_plain) | 3,953 | 96.5 | 97.7 | 100.0 | 84.5 | 85.1 | 99.6 | 96.1 | 67.9 | 100.0 |
| ai_humanized | English · attacked AI (humanized) | 2,845 | 82.6 | 84.2 | 92.7 | 70.0 | 63.8 | 89.3 | 79.5 | 11.9 | 93.7 |
| ai_tool_humanized | English · attacked AI (humanized) | 747 | 92.0 | 73.8 | 96.9 | 77.0 | 43.8 | 74.7 | 38.8 | 5.0 | 99.6 |
| h2l_rephrase | English · rephrase (h2l_rephrase) | 3,904 | 4.9 | 4.9 | 44.5 | 5.9 | 5.0 | 34.6 | 20.1 | 6.9 | 42.8 |
| human | English · clear human | 3,922 | 0.6 | 0.2 | 0.4 | 1.1 | 0.1 | 0.4 | 0.3 | 0.3 | 0.1 |
| ai_plain | non-English · clear AI (ai_plain) | 3,877 | 93.1 | 89.9 | 99.1 | 85.2 | – | – | 89.5 | 27.1 | 99.7 |
| ai_humanized | non-English · attacked AI (humanized) | 3,536 | 79.2 | 72.3 | 87.4 | 71.3 | – | – | 64.5 | 2.5 | 88.6 |
| h2l_rephrase | non-English · rephrase (h2l_rephrase) | 3,800 | 1.8 | 0.7 | 12.8 | 1.3 | – | – | 3.9 | 0.7 | 14.9 |
| human | non-English · clear human | 3,806 | 0.6 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.2 | 0.0 |
| ai_human_edited | English · ai_human_edited (a person rewrote model content) | 248 | 95.6 | 93.5 | 99.6 | 83.1 | 72.6 | 92.3 | 69.4 | 22.6 | 100.0 |

**By language.** Fire rate % at the 1% cut.

| Language | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Arabic | non-English · clear AI (ai_plain) | 944 | 87.8 | 78.2 | 97.8 | 80.4 | – | – | 82.7 | 0.1 | 99.7 |
| Chinese | non-English · clear AI (ai_plain) | 982 | 94.5 | 95.1 | 99.3 | 90.7 | – | – | 87.1 | 16.1 | 100.0 |
| French | non-English · clear AI (ai_plain) | 978 | 94.1 | 91.7 | 99.4 | 83.6 | – | – | 95.3 | 48.4 | 99.4 |
| Spanish | non-English · clear AI (ai_plain) | 973 | 95.8 | 94.2 | 99.9 | 85.8 | – | – | 92.5 | 43.0 | 99.8 |
| Arabic | non-English · attacked AI (humanized) | 812 | 69.2 | 53.0 | 82.0 | 61.3 | – | – | 55.0 | 0.0 | 84.9 |
| Chinese | non-English · attacked AI (humanized) | 936 | 83.1 | 80.3 | 90.1 | 78.7 | – | – | 57.1 | 0.7 | 91.6 |
| French | non-English · attacked AI (humanized) | 860 | 80.5 | 75.5 | 87.2 | 70.5 | – | – | 72.3 | 5.7 | 88.1 |
| Spanish | non-English · attacked AI (humanized) | 928 | 83.0 | 78.2 | 89.4 | 73.3 | – | – | 73.0 | 3.3 | 89.2 |
| Arabic | non-English · rephrase (h2l_rephrase) | 959 | 1.7 | 0.4 | 15.3 | 1.1 | – | – | 2.4 | 0.0 | 14.9 |
| Chinese | non-English · rephrase (h2l_rephrase) | 972 | 0.8 | 0.8 | 8.1 | 0.9 | – | – | 1.1 | 0.1 | 27.4 |
| French | non-English · rephrase (h2l_rephrase) | 918 | 2.5 | 1.0 | 16.8 | 1.7 | – | – | 9.4 | 1.5 | 10.7 |
| Spanish | non-English · rephrase (h2l_rephrase) | 951 | 2.2 | 0.4 | 11.1 | 1.3 | – | – | 2.9 | 1.1 | 6.3 |
| Arabic | non-English · clear human | 972 | 0.6 | 0.0 | 0.0 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |
| Chinese | non-English · clear human | 971 | 0.3 | 0.0 | 0.0 | 0.1 | – | – | 0.0 | 0.0 | 0.0 |
| French | non-English · clear human | 918 | 1.1 | 0.0 | 0.0 | 0.5 | – | – | 0.0 | 0.5 | 0.0 |
| Spanish | non-English · clear human | 945 | 0.3 | 0.0 | 0.0 | 0.5 | – | – | 0.0 | 0.2 | 0.0 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-3-5-sonnet-20241022 | English · clear AI (ai_plain) | 767 | 96.2 | 97.5 | 100.0 | 78.4 | 84.7 | 99.9 | 98.8 | 66.9 | 100.0 |
| gemini-1.5-pro-002 | English · clear AI (ai_plain) | 703 | 97.4 | 97.9 | 99.9 | 82.1 | 91.9 | 99.4 | 98.3 | 87.2 | 99.9 |
| gpt-3.5-turbo-0125 | English · clear AI (ai_plain) | 685 | 98.5 | 99.6 | 100.0 | 95.2 | 91.1 | 99.7 | 97.5 | 59.9 | 100.0 |
| gpt-4o-2024-11-20 | English · clear AI (ai_plain) | 583 | 95.0 | 96.6 | 100.0 | 84.0 | 70.0 | 99.7 | 90.7 | 26.6 | 100.0 |
| llama-3.3-70b-instruct | English · clear AI (ai_plain) | 548 | 94.7 | 95.1 | 100.0 | 83.8 | 84.9 | 98.7 | 93.2 | 86.9 | 100.0 |
| qwen2.5-72b-instruct | English · clear AI (ai_plain) | 667 | 96.7 | 99.1 | 100.0 | 84.1 | 85.5 | 99.9 | 96.0 | 77.4 | 100.0 |
| claude-3-5-sonnet-20241022 | English · attacked AI (humanized) | 711 | 84.2 | 84.0 | 94.1 | 66.1 | 58.9 | 87.2 | 73.4 | 4.9 | 95.1 |
| gemini-1.5-pro-002 | English · attacked AI (humanized) | 636 | 83.6 | 82.1 | 93.6 | 67.6 | 59.9 | 87.1 | 69.3 | 9.6 | 93.9 |
| gpt-3.5-turbo-0125 | English · attacked AI (humanized) | 607 | 86.7 | 85.0 | 94.4 | 79.6 | 67.1 | 87.0 | 74.6 | 12.0 | 96.0 |
| gpt-4o-2024-11-20 | English · attacked AI (humanized) | 540 | 82.0 | 79.4 | 92.2 | 73.9 | 57.0 | 84.1 | 69.6 | 7.4 | 94.6 |
| llama-3.3-70b-instruct | English · attacked AI (humanized) | 486 | 82.5 | 75.7 | 92.2 | 69.3 | 55.6 | 82.9 | 67.1 | 17.3 | 94.0 |
| qwen2.5-72b-instruct | English · attacked AI (humanized) | 612 | 87.7 | 84.2 | 94.3 | 73.0 | 58.2 | 88.4 | 70.8 | 13.4 | 95.8 |
| claude-3-5-sonnet-20241022 | non-English · clear AI (ai_plain) | 737 | 92.8 | 90.2 | 99.6 | 80.1 | – | – | 94.8 | 17.6 | 100.0 |
| gemini-1.5-pro-002 | non-English · clear AI (ai_plain) | 685 | 95.3 | 90.7 | 99.4 | 89.1 | – | – | 95.2 | 35.9 | 99.9 |
| gpt-3.5-turbo-0125 | non-English · clear AI (ai_plain) | 547 | 91.8 | 85.0 | 96.7 | 88.1 | – | – | 83.9 | 26.0 | 99.6 |
| gpt-4o-2024-11-20 | non-English · clear AI (ai_plain) | 689 | 96.7 | 97.0 | 100.0 | 90.4 | – | – | 93.3 | 10.0 | 100.0 |
| llama-3.3-70b-instruct | non-English · clear AI (ai_plain) | 463 | 90.5 | 85.3 | 98.3 | 83.8 | – | – | 82.3 | 67.4 | 98.5 |
| qwen2.5-72b-instruct | non-English · clear AI (ai_plain) | 756 | 90.6 | 88.9 | 99.7 | 80.7 | – | – | 83.9 | 20.0 | 99.9 |
| claude-3-5-sonnet-20241022 | non-English · attacked AI (humanized) | 681 | 79.1 | 70.5 | 87.1 | 64.8 | – | – | 62.4 | 1.8 | 88.5 |
| gemini-1.5-pro-002 | non-English · attacked AI (humanized) | 604 | 80.8 | 71.7 | 87.4 | 72.2 | – | – | 62.7 | 3.1 | 89.2 |
| gpt-3.5-turbo-0125 | non-English · attacked AI (humanized) | 523 | 80.9 | 72.8 | 88.5 | 76.3 | – | – | 68.5 | 1.9 | 90.2 |
| gpt-4o-2024-11-20 | non-English · attacked AI (humanized) | 609 | 80.8 | 77.5 | 88.0 | 76.8 | – | – | 64.2 | 1.0 | 89.7 |
| llama-3.3-70b-instruct | non-English · attacked AI (humanized) | 427 | 77.3 | 69.1 | 86.9 | 72.8 | – | – | 66.5 | 6.6 | 85.7 |
| qwen2.5-72b-instruct | non-English · attacked AI (humanized) | 692 | 76.6 | 71.7 | 86.4 | 67.3 | – | – | 64.0 | 1.7 | 87.6 |
| claude-3-5-sonnet-20241022 | English · ai_human_edited (a person rewrote model content) | 44 | 97.7 | 95.5 | 100.0 | 84.1 | 72.7 | 86.4 | 75.0 | 15.9 | 100.0 |
| gemini-1.5-pro-002 | English · ai_human_edited (a person rewrote model content) | 51 | 96.1 | 94.1 | 98.0 | 74.5 | 66.7 | 90.2 | 64.7 | 25.5 | 100.0 |
| gpt-3.5-turbo-0125 | English · ai_human_edited (a person rewrote model content) | 50 | 96.0 | 96.0 | 100.0 | 92.0 | 84.0 | 96.0 | 80.0 | 24.0 | 100.0 |
| gpt-4o-2024-11-20 | English · ai_human_edited (a person rewrote model content) | 31 | 100.0 | 90.3 | 100.0 | 80.6 | 67.7 | 93.5 | 64.5 | 9.7 | 100.0 |
| llama-3.3-70b-instruct | English · ai_human_edited (a person rewrote model content) | 34 | 85.3 | 85.3 | 100.0 | 79.4 | 64.7 | 94.1 | 61.8 | 35.3 | 100.0 |
| qwen2.5-72b-instruct | English · ai_human_edited (a person rewrote model content) | 38 | 97.4 | 97.4 | 100.0 | 86.8 | 76.3 | 94.7 | 65.8 | 23.7 | 100.0 |

**By domain.** Fire rate % at the 1% cut.

| Domain | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| arxiv | English · clear AI (ai_plain) | 987 | 97.9 | 99.0 | 100.0 | 76.7 | 84.8 | 99.7 | 98.2 | 73.9 | 100.0 |
| essay | English · clear AI (ai_plain) | 999 | 95.6 | 98.5 | 100.0 | 88.8 | 93.5 | 99.9 | 99.5 | 77.3 | 100.0 |
| news | English · clear AI (ai_plain) | 971 | 95.6 | 94.1 | 99.9 | 84.7 | 75.6 | 98.8 | 96.0 | 58.9 | 99.9 |
| writing | English · clear AI (ai_plain) | 996 | 97.1 | 99.2 | 100.0 | 87.8 | 86.1 | 99.9 | 90.6 | 61.2 | 100.0 |
| arxiv | English · attacked AI (humanized) | 914 | 86.5 | 82.9 | 93.4 | 67.0 | 54.3 | 86.7 | 75.1 | 11.2 | 97.3 |
| essay | English · attacked AI (humanized) | 916 | 76.0 | 75.2 | 92.0 | 68.1 | 61.9 | 83.2 | 72.6 | 12.9 | 92.4 |
| news | English · attacked AI (humanized) | 829 | 87.0 | 81.7 | 93.2 | 73.5 | 57.3 | 85.5 | 73.0 | 8.1 | 95.9 |
| writing | English · attacked AI (humanized) | 933 | 89.0 | 88.2 | 95.4 | 77.3 | 64.6 | 89.7 | 63.8 | 9.4 | 94.3 |
| arxiv | English · rephrase (h2l_rephrase) | 991 | 1.7 | 1.6 | 10.8 | 1.3 | 1.0 | 11.6 | 15.8 | 0.6 | 41.3 |
| essay | English · rephrase (h2l_rephrase) | 980 | 9.6 | 11.8 | 86.7 | 12.1 | 14.3 | 63.9 | 48.5 | 21.9 | 81.6 |
| news | English · rephrase (h2l_rephrase) | 944 | 5.0 | 3.0 | 33.1 | 3.8 | 1.5 | 23.4 | 11.1 | 3.4 | 31.8 |
| writing | English · rephrase (h2l_rephrase) | 989 | 3.3 | 3.0 | 47.3 | 6.3 | 3.0 | 39.4 | 4.8 | 1.5 | 16.5 |
| arxiv | English · clear human | 999 | 0.7 | 0.6 | 1.1 | 0.9 | 0.3 | 0.8 | 1.0 | 0.5 | 0.2 |
| essay | English · clear human | 992 | 0.2 | 0.0 | 0.0 | 0.7 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 |
| news | English · clear human | 933 | 0.3 | 0.0 | 0.2 | 0.3 | 0.0 | 0.0 | 0.2 | 0.3 | 0.1 |
| writing | English · clear human | 998 | 1.3 | 0.0 | 0.1 | 2.6 | 0.0 | 0.7 | 0.0 | 0.2 | 0.0 |
| news | non-English · clear AI (ai_plain) | 3,877 | 93.1 | 89.9 | 99.1 | 85.2 | – | – | 89.5 | 27.1 | 99.7 |
| news | non-English · attacked AI (humanized) | 3,536 | 79.2 | 72.3 | 87.4 | 71.3 | – | – | 64.5 | 2.5 | 88.6 |
| news | non-English · rephrase (h2l_rephrase) | 3,800 | 1.8 | 0.7 | 12.8 | 1.3 | – | – | 3.9 | 0.7 | 14.9 |
| news | non-English · clear human | 3,806 | 0.6 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.2 | 0.0 |
| arxiv | English · ai_human_edited (a person rewrote model content) | 58 | 96.6 | 96.6 | 98.3 | 72.4 | 56.9 | 89.7 | 70.7 | 6.9 | 100.0 |
| essay | English · ai_human_edited (a person rewrote model content) | 62 | 91.9 | 90.3 | 100.0 | 79.0 | 75.8 | 93.5 | 75.8 | 35.5 | 100.0 |
| news | English · ai_human_edited (a person rewrote model content) | 64 | 98.4 | 90.6 | 100.0 | 93.8 | 76.6 | 95.3 | 73.4 | 18.8 | 100.0 |
| writing | English · ai_human_edited (a person rewrote model content) | 64 | 95.3 | 96.9 | 100.0 | 85.9 | 79.7 | 90.6 | 57.8 | 28.1 | 100.0 |

**By split.** Fire rate % at the 1% cut.

| Split | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dev | English · clear AI (ai_plain) | 1,980 | 96.2 | 97.9 | 99.9 | 84.2 | 83.9 | 99.4 | 95.8 | 67.8 | 99.9 |
| test | English · clear AI (ai_plain) | 1,973 | 96.9 | 97.5 | 100.0 | 84.7 | 86.3 | 99.7 | 96.3 | 68.0 | 100.0 |
| dev | English · attacked AI (humanized) | 1,920 | 85.1 | 83.7 | 93.9 | 71.8 | 60.9 | 87.1 | 72.8 | 10.2 | 95.5 |
| test | English · attacked AI (humanized) | 1,672 | 84.0 | 80.1 | 93.2 | 71.1 | 58.1 | 85.3 | 69.0 | 10.7 | 94.3 |
| dev | English · rephrase (h2l_rephrase) | 1,944 | 4.8 | 5.0 | 45.8 | 6.2 | 5.3 | 34.1 | 19.5 | 6.3 | 41.3 |
| test | English · rephrase (h2l_rephrase) | 1,960 | 5.0 | 4.7 | 43.2 | 5.6 | 4.6 | 35.2 | 20.7 | 7.4 | 44.4 |
| dev | English · clear human | 1,957 | 0.8 | 0.3 | 0.5 | 1.2 | 0.2 | 0.5 | 0.4 | 0.4 | 0.1 |
| test | English · clear human | 1,965 | 0.5 | 0.1 | 0.2 | 1.1 | 0.0 | 0.3 | 0.3 | 0.3 | 0.1 |
| dev | non-English · clear AI (ai_plain) | 1,931 | 92.9 | 91.4 | 99.3 | 84.8 | – | – | 88.1 | 26.6 | 99.8 |
| test | non-English · clear AI (ai_plain) | 1,946 | 93.3 | 88.5 | 98.9 | 85.6 | – | – | 90.8 | 27.6 | 99.6 |
| dev | non-English · attacked AI (humanized) | 1,765 | 79.2 | 73.8 | 87.5 | 71.2 | – | – | 63.9 | 2.5 | 88.4 |
| test | non-English · attacked AI (humanized) | 1,771 | 79.3 | 70.8 | 87.2 | 71.4 | – | – | 65.0 | 2.4 | 88.7 |
| dev | non-English · rephrase (h2l_rephrase) | 1,902 | 1.7 | 0.7 | 13.5 | 1.2 | – | – | 4.3 | 0.7 | 14.4 |
| test | non-English · rephrase (h2l_rephrase) | 1,898 | 1.9 | 0.6 | 12.1 | 1.3 | – | – | 3.5 | 0.6 | 15.5 |
| dev | non-English · clear human | 1,888 | 0.6 | 0.0 | 0.0 | 0.5 | – | – | 0.0 | 0.2 | 0.0 |
| test | non-English · clear human | 1,918 | 0.5 | 0.0 | 0.0 | 0.2 | – | – | 0.0 | 0.2 | 0.0 |
| test | English · ai_human_edited (a person rewrote model content) | 248 | 95.6 | 93.5 | 99.6 | 83.1 | 72.6 | 92.3 | 69.4 | 22.6 | 100.0 |
