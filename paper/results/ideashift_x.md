### IdeaShift-X (24 languages): main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Model-ideas arm is level 0 (2026-09-16 rebuild): a model writes from one line naming the document type and broad subject, in the page's language (the IdeaShift level-0 brief, gemini-3.7-flash); it replaces level 1.
- ModernBERT reading the document is '–': an English-only model.
- EditLens and Binoculars cover every language.
- Human arm: the FineWeb2 pages IdeaShift-X was built from (10,160). Length split leaves out Chinese, Japanese, Thai and Khmer (no word spacing).
- Resource groups by FineWeb2 size: high 540 GB to 2 TB, mid 24 to 152 GB, low 0.1 to 9.4 GB. Chinese combines two generation runs over the same FineWeb2 subset (cmn_Hani), one of them generated as Traditional Chinese.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| high-resource · level 0 | model ideas (TPR) | 3,729 | 94.2 | 98.3 | 99.6 | 70.6 | – | – | 29.1 | 0.0 | 100.0 |
| high-resource · level 5 | human ideas, AI prose (FPR) | 3,721 | 0.8 | 6.3 | 79.3 | 1.2 | – | – | 3.4 | 0.0 | 96.6 |
| high-resource · human | human ideas (FPR) | 3,729 | 0.0 | 0.0 | 0.0 | 0.1 | – | – | 0.1 | 0.0 | 0.0 |
| mid-resource · level 0 | model ideas (TPR) | 2,971 | 96.4 | 96.7 | 97.0 | 78.1 | – | – | 14.7 | 0.0 | 99.1 |
| mid-resource · level 5 | human ideas, AI prose (FPR) | 2,965 | 0.8 | 3.7 | 50.9 | 1.2 | – | – | 1.1 | 0.0 | 80.5 |
| mid-resource · human | human ideas (FPR) | 2,976 | 0.0 | 0.0 | 0.0 | 0.1 | – | – | 0.0 | 0.0 | 0.0 |
| low-resource · level 0 | model ideas (TPR) | 3,452 | 95.4 | 49.9 | 51.6 | 78.9 | – | – | 1.1 | 0.0 | 58.0 |
| low-resource · level 5 | human ideas, AI prose (FPR) | 3,430 | 0.6 | 0.0 | 1.2 | 1.0 | – | – | 0.0 | 0.0 | 8.1 |
| low-resource · human | human ideas (FPR) | 3,455 | 0.2 | 0.0 | 0.0 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |
| All languages · level 0 | model ideas (TPR) | 10,152 | 95.3 | 81.4 | 82.5 | 75.6 | – | – | 15.4 | 0.0 | 85.4 |
| All languages · level 5 | human ideas, AI prose (FPR) | 10,116 | 0.7 | 3.4 | 44.5 | 1.2 | – | – | 1.6 | 0.0 | 61.9 |
| All languages · human | human ideas (FPR) | 10,160 | 0.1 | 0.0 | 0.0 | 0.2 | – | – | 0.0 | 0.0 | 0.0 |
| AUC, high, level 0 vs human | | | 0.998 | 1.000 | 1.000 | 0.988 | – | – | 0.987 | 0.267 | 1.000 |
| AUC, mid, level 0 vs human | | | 0.999 | 1.000 | 0.999 | 0.990 | – | – | 0.976 | 0.188 | 0.997 |
| AUC, low, level 0 vs human | | | 0.998 | 0.982 | 0.956 | 0.989 | – | – | 0.826 | 0.333 | 0.853 |
| AUC, all, level 0 vs human | | | 0.998 | 0.997 | 0.985 | 0.989 | – | – | 0.940 | 0.277 | 0.949 |

**Length.** Share under 500 words: high-resource · level 0 14.8%, high-resource · level 5 7.3%, high-resource · human 0.0%, mid-resource · level 0 11.8%, mid-resource · level 5 5.2%, mid-resource · human 0.0%, low-resource · level 0 8.3%, low-resource · level 5 4.1%, low-resource · human 0.0%, All languages · level 0 11.3%, All languages · level 5 5.4%, All languages · human 0.0%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| high-resource · level 0 · < 500 | model ideas (TPR) | 354 | 96.3 | 98.0 | 99.7 | 70.6 | – | – | 48.9 | 0.0 | 100.0 |
| high-resource · level 0 · >= 500 | model ideas (TPR) | 2,032 | 94.1 | 98.9 | 99.7 | 67.8 | – | – | 33.8 | 0.0 | 100.0 |
| high-resource · level 5 · < 500 | human ideas, AI prose (FPR) | 173 | 0.0 | 0.6 | 61.8 | 0.6 | – | – | 13.3 | 0.0 | 93.1 |
| high-resource · level 5 · >= 500 | human ideas, AI prose (FPR) | 2,208 | 0.8 | 6.0 | 84.0 | 1.0 | – | – | 4.4 | 0.0 | 96.1 |
| high-resource · human · >= 500 | human ideas (FPR) | 2,386 | 0.0 | 0.0 | 0.0 | 0.1 | – | – | 0.0 | 0.0 | 0.0 |
| mid-resource · level 0 · < 500 | model ideas (TPR) | 321 | 97.5 | 98.1 | 99.1 | 80.4 | – | – | 25.9 | 0.3 | 100.0 |
| mid-resource · level 0 · >= 500 | model ideas (TPR) | 2,400 | 96.1 | 96.4 | 96.6 | 77.9 | – | – | 14.7 | 0.0 | 98.8 |
| mid-resource · level 5 · < 500 | human ideas, AI prose (FPR) | 142 | 0.0 | 0.0 | 41.5 | 0.7 | – | – | 6.3 | 0.0 | 81.7 |
| mid-resource · level 5 · >= 500 | human ideas, AI prose (FPR) | 2,573 | 0.9 | 3.8 | 54.5 | 1.2 | – | – | 0.9 | 0.0 | 81.7 |
| mid-resource · human · >= 500 | human ideas (FPR) | 2,726 | 0.0 | 0.0 | 0.0 | 0.1 | – | – | 0.0 | 0.0 | 0.0 |
| low-resource · level 0 · < 500 | model ideas (TPR) | 265 | 94.7 | 56.6 | 57.7 | 75.5 | – | – | 0.0 | 0.0 | 67.5 |
| low-resource · level 0 · >= 500 | model ideas (TPR) | 2,937 | 95.6 | 53.4 | 55.3 | 79.0 | – | – | 1.3 | 0.0 | 62.1 |
| low-resource · level 5 · < 500 | human ideas, AI prose (FPR) | 131 | 0.8 | 0.8 | 0.8 | 0.8 | – | – | 0.0 | 0.0 | 4.6 |
| low-resource · level 5 · >= 500 | human ideas, AI prose (FPR) | 3,049 | 0.7 | 0.0 | 1.3 | 1.1 | – | – | 0.0 | 0.0 | 8.9 |
| low-resource · human · >= 500 | human ideas (FPR) | 3,205 | 0.2 | 0.0 | 0.0 | 0.2 | – | – | 0.0 | 0.0 | 0.0 |
| All languages · level 0 · < 500 | model ideas (TPR) | 940 | 96.3 | 86.4 | 87.7 | 75.3 | – | – | 27.2 | 0.1 | 90.9 |
| All languages · level 0 · >= 500 | model ideas (TPR) | 7,369 | 95.3 | 79.9 | 81.0 | 75.6 | – | – | 14.6 | 0.0 | 84.5 |
| All languages · level 5 · < 500 | human ideas, AI prose (FPR) | 446 | 0.2 | 0.4 | 37.4 | 0.7 | – | – | 7.2 | 0.0 | 63.5 |
| All languages · level 5 · >= 500 | human ideas, AI prose (FPR) | 7,830 | 0.8 | 2.9 | 42.1 | 1.1 | – | – | 1.6 | 0.0 | 57.4 |
| All languages · human · >= 500 | human ideas (FPR) | 8,317 | 0.1 | 0.0 | 0.0 | 0.2 | – | – | 0.0 | 0.0 | 0.0 |

### IdeaShift-X (24 languages): appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| high-resource · level 0 | IdeaLens · outline | 84.2 | 91.9 | 96.6 | 98.2 |
| high-resource · level 0 | IdeaLens · document | 94.3 | 97.0 | 99.6 | 99.8 |
| high-resource · level 0 | ProseLens | 99.2 | 99.6 | 99.8 | 99.9 |
| high-resource · level 0 | IdeaLens-ModernBERT-L · outline | 40.0 | 61.4 | 81.0 | 91.6 |
| high-resource · level 0 | IdeaLens-ModernBERT-L · document | – | – | – | – |
| high-resource · level 0 | ProseLens-ModernBERT-L | – | – | – | – |
| high-resource · level 0 | EditLens-Llama-3B (cal.) | 0.0 | 8.9 | 76.5 | 99.8 |
| high-resource · level 0 | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.1 |
| high-resource · level 5 | IdeaLens · outline | 0.1 | 0.4 | 2.1 | 6.2 |
| high-resource · level 5 | IdeaLens · document | 0.9 | 2.7 | 21.7 | 50.9 |
| high-resource · level 5 | ProseLens | 46.8 | 67.0 | 91.8 | 98.4 |
| high-resource · level 5 | IdeaLens-ModernBERT-L · outline | 0.2 | 0.6 | 2.4 | 7.8 |
| high-resource · level 5 | IdeaLens-ModernBERT-L · document | – | – | – | – |
| high-resource · level 5 | ProseLens-ModernBERT-L | – | – | – | – |
| high-resource · level 5 | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 42.4 | 97.1 |
| high-resource · level 5 | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.2 |
| high-resource · human | IdeaLens · outline | 0.0 | 0.0 | 0.1 | 0.6 |
| high-resource · human | IdeaLens · document | 0.0 | 0.0 | 0.0 | 0.1 |
| high-resource · human | ProseLens | 0.0 | 0.0 | 0.1 | 1.5 |
| high-resource · human | IdeaLens-ModernBERT-L · outline | 0.0 | 0.1 | 0.5 | 2.3 |
| high-resource · human | IdeaLens-ModernBERT-L · document | – | – | – | – |
| high-resource · human | ProseLens-ModernBERT-L | – | – | – | – |
| high-resource · human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.9 | 31.5 |
| high-resource · human | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.7 |
| mid-resource · level 0 | IdeaLens · outline | 89.4 | 94.9 | 97.7 | 99.1 |
| mid-resource · level 0 | IdeaLens · document | 92.4 | 95.2 | 98.8 | 99.6 |
| mid-resource · level 0 | ProseLens | 94.2 | 96.1 | 98.0 | 98.8 |
| mid-resource · level 0 | IdeaLens-ModernBERT-L · outline | 47.2 | 68.9 | 87.0 | 94.6 |
| mid-resource · level 0 | IdeaLens-ModernBERT-L · document | – | – | – | – |
| mid-resource · level 0 | ProseLens-ModernBERT-L | – | – | – | – |
| mid-resource · level 0 | EditLens-Llama-3B (cal.) | 0.0 | 1.9 | 63.8 | 98.7 |
| mid-resource · level 0 | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.0 |
| mid-resource · level 5 | IdeaLens · outline | 0.1 | 0.6 | 1.9 | 5.4 |
| mid-resource · level 5 | IdeaLens · document | 0.5 | 1.4 | 14.4 | 43.8 |
| mid-resource · level 5 | ProseLens | 20.2 | 37.6 | 67.2 | 83.6 |
| mid-resource · level 5 | IdeaLens-ModernBERT-L · outline | 0.0 | 0.5 | 3.3 | 9.6 |
| mid-resource · level 5 | IdeaLens-ModernBERT-L · document | – | – | – | – |
| mid-resource · level 5 | ProseLens-ModernBERT-L | – | – | – | – |
| mid-resource · level 5 | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 33.2 | 93.6 |
| mid-resource · level 5 | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.1 |
| mid-resource · human | IdeaLens · outline | 0.0 | 0.0 | 0.0 | 0.5 |
| mid-resource · human | IdeaLens · document | 0.0 | 0.0 | 0.0 | 0.1 |
| mid-resource · human | ProseLens | 0.0 | 0.0 | 0.0 | 0.2 |
| mid-resource · human | IdeaLens-ModernBERT-L · outline | 0.0 | 0.1 | 0.4 | 2.9 |
| mid-resource · human | IdeaLens-ModernBERT-L · document | – | – | – | – |
| mid-resource · human | ProseLens-ModernBERT-L | – | – | – | – |
| mid-resource · human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.3 | 26.9 |
| mid-resource · human | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.4 |
| low-resource · level 0 | IdeaLens · outline | 85.7 | 93.7 | 97.3 | 98.7 |
| low-resource · level 0 | IdeaLens · document | 31.7 | 42.0 | 61.2 | 89.4 |
| low-resource · level 0 | ProseLens | 34.3 | 44.5 | 59.6 | 70.4 |
| low-resource · level 0 | IdeaLens-ModernBERT-L · outline | 46.8 | 70.6 | 88.6 | 94.6 |
| low-resource · level 0 | IdeaLens-ModernBERT-L · document | – | – | – | – |
| low-resource · level 0 | ProseLens-ModernBERT-L | – | – | – | – |
| low-resource · level 0 | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 18.6 | 86.6 |
| low-resource · level 0 | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.0 |
| low-resource · level 5 | IdeaLens · outline | 0.1 | 0.3 | 1.2 | 4.3 |
| low-resource · level 5 | IdeaLens · document | 0.0 | 0.0 | 0.5 | 26.4 |
| low-resource · level 5 | ProseLens | 0.0 | 0.2 | 5.4 | 32.6 |
| low-resource · level 5 | IdeaLens-ModernBERT-L · outline | 0.1 | 0.5 | 2.9 | 9.2 |
| low-resource · level 5 | IdeaLens-ModernBERT-L · document | – | – | – | – |
| low-resource · level 5 | ProseLens-ModernBERT-L | – | – | – | – |
| low-resource · level 5 | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 5.8 | 79.9 |
| low-resource · level 5 | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.0 |
| low-resource · human | IdeaLens · outline | 0.1 | 0.1 | 0.3 | 0.6 |
| low-resource · human | IdeaLens · document | 0.0 | 0.0 | 0.1 | 3.8 |
| low-resource · human | ProseLens | 0.0 | 0.0 | 0.1 | 0.8 |
| low-resource · human | IdeaLens-ModernBERT-L · outline | 0.0 | 0.2 | 0.6 | 3.2 |
| low-resource · human | IdeaLens-ModernBERT-L · document | – | – | – | – |
| low-resource · human | ProseLens-ModernBERT-L | – | – | – | – |
| low-resource · human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.3 | 50.9 |
| low-resource · human | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.0 |
| All languages · level 0 | IdeaLens · outline | 86.2 | 93.4 | 97.2 | 98.6 |
| All languages · level 0 | IdeaLens · document | 72.5 | 77.8 | 86.3 | 96.2 |
| All languages · level 0 | ProseLens | 75.7 | 79.8 | 85.6 | 89.5 |
| All languages · level 0 | IdeaLens-ModernBERT-L · outline | 44.4 | 66.7 | 85.3 | 93.5 |
| All languages · level 0 | IdeaLens-ModernBERT-L · document | – | – | – | – |
| All languages · level 0 | ProseLens-ModernBERT-L | – | – | – | – |
| All languages · level 0 | EditLens-Llama-3B (cal.) | 0.0 | 3.8 | 53.1 | 95.0 |
| All languages · level 0 | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.0 |
| All languages · level 5 | IdeaLens · outline | 0.1 | 0.4 | 1.7 | 5.3 |
| All languages · level 5 | IdeaLens · document | 0.5 | 1.4 | 12.4 | 40.5 |
| All languages · level 5 | ProseLens | 23.2 | 35.7 | 55.3 | 71.7 |
| All languages · level 5 | IdeaLens-ModernBERT-L · outline | 0.1 | 0.6 | 2.8 | 8.8 |
| All languages · level 5 | IdeaLens-ModernBERT-L · document | – | – | – | – |
| All languages · level 5 | ProseLens-ModernBERT-L | – | – | – | – |
| All languages · level 5 | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 27.3 | 90.2 |
| All languages · level 5 | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.1 |
| All languages · human | IdeaLens · outline | 0.0 | 0.1 | 0.2 | 0.6 |
| All languages · human | IdeaLens · document | 0.0 | 0.0 | 0.0 | 1.3 |
| All languages · human | ProseLens | 0.0 | 0.0 | 0.0 | 0.9 |
| All languages · human | IdeaLens-ModernBERT-L · outline | 0.0 | 0.1 | 0.5 | 2.8 |
| All languages · human | IdeaLens-ModernBERT-L · document | – | – | – | – |
| All languages · human | ProseLens-ModernBERT-L | – | – | – | – |
| All languages · human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.5 | 36.8 |
| All languages · human | Binoculars (cal.) | 0.0 | 0.0 | 0.0 | 0.4 |

**By language.** Fire rate % at the 1% cut.

| Language | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Chinese | high-resource · level 0 | 614 | 92.2 | 95.8 | 99.0 | 71.2 | – | – | 19.4 | 0.0 | 99.8 |
| French | high-resource · level 0 | 250 | 93.6 | 99.6 | 100.0 | 72.8 | – | – | 39.2 | 0.0 | 100.0 |
| German | high-resource · level 0 | 704 | 93.0 | 98.4 | 99.6 | 68.2 | – | – | 38.5 | 0.0 | 100.0 |
| Japanese | high-resource · level 0 | 729 | 95.2 | 99.2 | 99.9 | 77.8 | – | – | 14.8 | 0.0 | 100.0 |
| Russian | high-resource · level 0 | 699 | 92.1 | 97.4 | 99.4 | 56.9 | – | – | 12.3 | 0.0 | 100.0 |
| Spanish | high-resource · level 0 | 733 | 98.4 | 100.0 | 100.0 | 77.5 | – | – | 55.3 | 0.0 | 100.0 |
| Chinese | high-resource · level 5 | 611 | 1.3 | 14.1 | 88.5 | 1.6 | – | – | 0.8 | 0.0 | 98.4 |
| French | high-resource · level 5 | 250 | 0.4 | 4.0 | 90.4 | 1.6 | – | – | 7.2 | 0.0 | 94.0 |
| German | high-resource · level 5 | 703 | 0.3 | 5.8 | 81.1 | 0.7 | – | – | 6.7 | 0.0 | 98.3 |
| Japanese | high-resource · level 5 | 729 | 0.4 | 2.3 | 61.7 | 1.6 | – | – | 0.1 | 0.0 | 97.8 |
| Russian | high-resource · level 5 | 695 | 1.2 | 4.7 | 72.8 | 1.0 | – | – | 0.1 | 0.0 | 93.1 |
| Spanish | high-resource · level 5 | 733 | 0.8 | 6.7 | 89.9 | 1.1 | – | – | 7.5 | 0.0 | 96.7 |
| Chinese | high-resource · human | 614 | 0.0 | 0.0 | 0.0 | 0.2 | – | – | 0.0 | 0.0 | 0.0 |
| French | high-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.4 | 0.0 | 0.0 |
| German | high-resource · human | 704 | 0.0 | 0.0 | 0.0 | 0.1 | – | – | 0.0 | 0.0 | 0.0 |
| Japanese | high-resource · human | 729 | 0.0 | 0.0 | 0.0 | 0.1 | – | – | 0.1 | 0.0 | 0.0 |
| Russian | high-resource · human | 699 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Spanish | high-resource · human | 733 | 0.0 | 0.0 | 0.0 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |
| Bengali | mid-resource · level 0 | 248 | 97.6 | 83.1 | 76.6 | 81.9 | – | – | 0.4 | 0.4 | 89.1 |
| Hindi | mid-resource · level 0 | 250 | 98.4 | 99.2 | 99.6 | 86.8 | – | – | 6.8 | 0.0 | 100.0 |
| Indonesian | mid-resource · level 0 | 740 | 97.4 | 98.9 | 99.5 | 77.0 | – | – | 27.7 | 0.0 | 100.0 |
| Modern Standard Arabic | mid-resource · level 0 | 734 | 97.3 | 98.5 | 98.8 | 83.2 | – | – | 20.4 | 0.0 | 100.0 |
| Persian | mid-resource · level 0 | 250 | 96.8 | 99.6 | 99.2 | 80.4 | – | – | 2.8 | 0.0 | 100.0 |
| Thai | mid-resource · level 0 | 250 | 98.0 | 98.4 | 98.4 | 77.2 | – | – | 0.4 | 0.0 | 100.0 |
| Ukrainian | mid-resource · level 0 | 250 | 86.4 | 91.2 | 96.4 | 54.0 | – | – | 7.6 | 0.0 | 99.6 |
| Vietnamese | mid-resource · level 0 | 249 | 95.6 | 97.2 | 99.6 | 76.7 | – | – | 14.5 | 0.0 | 100.0 |
| Bengali | mid-resource · level 5 | 243 | 0.4 | 0.0 | 2.9 | 0.4 | – | – | 0.0 | 0.0 | 28.4 |
| Hindi | mid-resource · level 5 | 250 | 0.8 | 3.2 | 47.6 | 1.6 | – | – | 0.4 | 0.0 | 91.2 |
| Indonesian | mid-resource · level 5 | 741 | 1.2 | 5.7 | 64.2 | 1.5 | – | – | 2.4 | 0.0 | 88.4 |
| Modern Standard Arabic | mid-resource · level 5 | 734 | 0.1 | 2.6 | 67.2 | 1.0 | – | – | 0.1 | 0.0 | 89.4 |
| Persian | mid-resource · level 5 | 248 | 1.2 | 4.0 | 45.2 | 0.8 | – | – | 0.8 | 0.0 | 70.6 |
| Thai | mid-resource · level 5 | 250 | 0.8 | 5.2 | 19.2 | 2.0 | – | – | 0.0 | 0.0 | 68.0 |
| Ukrainian | mid-resource · level 5 | 250 | 0.4 | 1.2 | 41.6 | 0.8 | – | – | 0.4 | 0.0 | 88.8 |
| Vietnamese | mid-resource · level 5 | 249 | 2.4 | 6.4 | 59.8 | 1.6 | – | – | 3.6 | 0.0 | 85.1 |
| Bengali | mid-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Hindi | mid-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Indonesian | mid-resource · human | 742 | 0.1 | 0.0 | 0.0 | 0.1 | – | – | 0.0 | 0.0 | 0.0 |
| Modern Standard Arabic | mid-resource · human | 734 | 0.0 | 0.0 | 0.0 | 0.1 | – | – | 0.0 | 0.0 | 0.0 |
| Persian | mid-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Thai | mid-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| Ukrainian | mid-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Vietnamese | mid-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Amharic | low-resource · level 0 | 250 | 96.0 | 0.0 | 1.2 | 84.8 | – | – | 0.0 | 0.0 | 0.0 |
| Khmer | low-resource · level 0 | 250 | 94.4 | 0.8 | 1.2 | 81.2 | – | – | 0.0 | 0.0 | 0.0 |
| Malayalam | low-resource · level 0 | 249 | 97.2 | 66.7 | 40.6 | 81.1 | – | – | 0.0 | 0.0 | 54.2 |
| Marathi | low-resource · level 0 | 250 | 94.8 | 62.8 | 54.4 | 73.2 | – | – | 0.8 | 0.0 | 72.8 |
| Nepali | low-resource · level 0 | 250 | 97.2 | 85.6 | 88.0 | 85.6 | – | – | 0.0 | 0.0 | 86.8 |
| Sinhala | low-resource · level 0 | 250 | 97.2 | 1.2 | 2.8 | 80.4 | – | – | 0.0 | 0.0 | 0.4 |
| Swahili | low-resource · level 0 | 249 | 95.2 | 13.7 | 47.4 | 76.7 | – | – | 0.4 | 0.0 | 96.4 |
| Tamil | low-resource · level 0 | 717 | 95.8 | 67.5 | 67.1 | 80.5 | – | – | 0.0 | 0.0 | 69.0 |
| Urdu | low-resource · level 0 | 737 | 96.2 | 87.0 | 84.0 | 79.8 | – | – | 4.6 | 0.0 | 98.2 |
| Yoruba | low-resource · level 0 | 250 | 88.0 | 8.0 | 36.8 | 61.2 | – | – | 0.0 | 0.0 | 3.2 |
| Amharic | low-resource · level 5 | 250 | 0.8 | 0.0 | 0.0 | 1.2 | – | – | 0.0 | 0.0 | 0.0 |
| Khmer | low-resource · level 5 | 250 | 0.0 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| Malayalam | low-resource · level 5 | 242 | 0.8 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| Marathi | low-resource · level 5 | 247 | 2.0 | 0.0 | 0.8 | 2.4 | – | – | 0.0 | 0.0 | 0.4 |
| Nepali | low-resource · level 5 | 250 | 0.8 | 0.0 | 6.8 | 1.2 | – | – | 0.0 | 0.0 | 0.4 |
| Sinhala | low-resource · level 5 | 250 | 0.4 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| Swahili | low-resource · level 5 | 249 | 0.8 | 0.0 | 0.0 | 0.8 | – | – | 0.0 | 0.0 | 1.2 |
| Tamil | low-resource · level 5 | 706 | 0.1 | 0.1 | 1.6 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| Urdu | low-resource · level 5 | 736 | 0.0 | 0.0 | 1.4 | 1.4 | – | – | 0.1 | 0.0 | 37.0 |
| Yoruba | low-resource · level 5 | 250 | 2.4 | 0.0 | 0.0 | 2.0 | – | – | 0.0 | 0.0 | 0.0 |
| Amharic | low-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| Khmer | low-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| Malayalam | low-resource · human | 249 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Marathi | low-resource · human | 250 | 0.4 | 0.4 | 0.4 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| Nepali | low-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Sinhala | low-resource · human | 250 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Swahili | low-resource · human | 250 | 0.8 | 0.0 | 0.0 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| Tamil | low-resource · human | 719 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |
| Urdu | low-resource · human | 737 | 0.0 | 0.0 | 0.0 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |
| Yoruba | low-resource · human | 250 | 1.2 | 0.0 | 0.0 | 1.2 | – | – | 0.0 | 0.0 | 0.0 |
