### MELD: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Attacks: homoglyph, number, synonym, upper_lower (case flip), whitespace, zero-width space, each applied to model text.
- Length is our whitespace word count; the benchmark describes its documents as 500+ words (likely tokens).

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai_none | model ideas (TPR) | 1,546 | 88.1 | 97.0 | 99.9 | 73.9 | 80.1 | 96.2 | 98.0 | 47.9 | 100.0 |
| ai_adversarial (6 attacks) | model ideas (TPR) | 9,249 | 84.2 | 71.6 | 72.9 | 70.9 | 41.2 | 76.0 | 53.1 | 7.9 | 100.0 |
| human | human ideas (FPR) | 3,918 | 0.2 | 0.0 | 0.0 | 0.8 | 0.1 | 0.4 | 0.0 | 0.3 | 0.0 |
| AUC, ai_none vs human | | | 0.995 | 1.000 | 1.000 | 0.968 | 0.990 | 0.999 | 1.000 | 0.978 | 1.000 |
| AUC, ai_adversarial vs human | | | 0.994 | 0.997 | 0.964 | 0.965 | 0.693 | 0.982 | 0.983 | 0.769 | 1.000 |

**Length.** Share under 500 words: ai_none 57.2%, ai_adversarial (6 attacks) 57.2%, human 89.2%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai_none · < 500 | model ideas (TPR) | 884 | 85.6 | 96.0 | 99.8 | 66.2 | 73.9 | 94.0 | 97.4 | 43.8 | 100.0 |
| ai_none · >= 500 | model ideas (TPR) | 662 | 91.4 | 98.3 | 100.0 | 84.3 | 88.5 | 99.2 | 98.8 | 53.5 | 100.0 |
| ai_adversarial (6 attacks) · < 500 | model ideas (TPR) | 5,290 | 79.9 | 68.8 | 70.5 | 61.7 | 36.7 | 72.7 | 52.7 | 6.7 | 100.0 |
| ai_adversarial (6 attacks) · >= 500 | model ideas (TPR) | 3,959 | 89.9 | 75.5 | 76.2 | 83.3 | 47.1 | 80.4 | 53.6 | 9.4 | 100.0 |
| human · < 500 | human ideas (FPR) | 3,493 | 0.2 | 0.0 | 0.0 | 0.8 | 0.1 | 0.4 | 0.0 | 0.3 | 0.0 |
| human · >= 500 | human ideas (FPR) | 425 | 0.0 | 0.0 | 0.0 | 0.2 | 0.2 | 0.2 | 0.0 | 0.0 | 0.0 |

### MELD: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| ai_none | IdeaLens · outline | 70.6 | 83.4 | 92.2 | 96.4 |
| ai_none | IdeaLens · document | 90.9 | 95.5 | 99.4 | 99.9 |
| ai_none | ProseLens | 98.8 | 99.4 | 99.9 | 100.0 |
| ai_none | IdeaLens-ModernBERT-L · outline | 41.0 | 64.9 | 82.5 | 92.1 |
| ai_none | IdeaLens-ModernBERT-L · document | 55.8 | 71.0 | 90.4 | 98.6 |
| ai_none | ProseLens-ModernBERT-L | 81.6 | 93.6 | 98.3 | 99.9 |
| ai_none | EditLens-Llama-3B (cal.) | 0.0 | 88.8 | 99.5 | 99.9 |
| ai_none | Binoculars (cal.) | 7.5 | 49.3 | 88.0 | 95.2 |
| ai_adversarial (6 attacks) | IdeaLens · outline | 67.5 | 79.8 | 90.1 | 95.2 |
| ai_adversarial (6 attacks) | IdeaLens · document | 58.1 | 66.1 | 78.8 | 97.4 |
| ai_adversarial (6 attacks) | ProseLens | 64.6 | 70.0 | 76.1 | 79.6 |
| ai_adversarial (6 attacks) | IdeaLens-ModernBERT-L · outline | 40.3 | 63.8 | 80.1 | 91.1 |
| ai_adversarial (6 attacks) | IdeaLens-ModernBERT-L · document | 22.7 | 33.5 | 52.5 | 64.2 |
| ai_adversarial (6 attacks) | ProseLens-ModernBERT-L | 60.1 | 71.7 | 79.8 | 98.5 |
| ai_adversarial (6 attacks) | EditLens-Llama-3B (cal.) | 0.0 | 40.9 | 63.4 | 83.1 |
| ai_adversarial (6 attacks) | Binoculars (cal.) | 1.0 | 8.2 | 39.4 | 48.9 |
| human | IdeaLens · outline | 0.0 | 0.1 | 0.6 | 2.6 |
| human | IdeaLens · document | 0.0 | 0.0 | 0.0 | 2.7 |
| human | ProseLens | 0.0 | 0.0 | 0.0 | 0.8 |
| human | IdeaLens-ModernBERT-L · outline | 0.1 | 0.4 | 2.2 | 10.8 |
| human | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 0.8 | 20.5 |
| human | ProseLens-ModernBERT-L | 0.1 | 0.3 | 1.4 | 16.1 |
| human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.4 | 4.7 |
| human | Binoculars (cal.) | 0.0 | 0.3 | 4.5 | 11.5 |

**By attack.** Fire rate % at the 1% cut.

| Attack | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| homoglyph | ai_adversarial (6 attacks) | 1,533 | 86.5 | 64.9 | 48.8 | 71.5 | 0.0 | 95.8 | 4.0 | 0.0 | 100.0 |
| number | ai_adversarial (6 attacks) | 1,553 | 84.4 | 95.6 | 99.4 | 71.2 | 77.3 | 94.7 | 96.1 | 40.7 | 100.0 |
| synonym | ai_adversarial (6 attacks) | 1,543 | 76.3 | 71.8 | 91.7 | 66.6 | 40.6 | 80.6 | 43.6 | 0.7 | 100.0 |
| upper_lower | ai_adversarial (6 attacks) | 1,564 | 86.4 | 97.3 | 97.8 | 72.3 | 63.2 | 91.4 | 82.4 | 0.0 | 100.0 |
| whitespace | ai_adversarial (6 attacks) | 1,556 | 85.5 | 97.5 | 96.9 | 71.5 | 63.9 | 91.2 | 89.6 | 5.1 | 100.0 |
| zero_width_space | ai_adversarial (6 attacks) | 1,500 | 86.4 | 0.1 | 0.0 | 72.6 | 0.0 | 0.0 | 0.0 | 0.3 | 100.0 |

**By domain.** Fire rate % at the 1% cut.

| Domain | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abstracts | ai_none | 156 | 97.4 | 96.2 | 100.0 | 87.2 | 78.8 | 98.1 | 100.0 | 19.9 | 100.0 |
| books | ai_none | 259 | 93.4 | 99.6 | 100.0 | 81.9 | 91.5 | 99.6 | 98.1 | 55.6 | 100.0 |
| news | ai_none | 258 | 87.6 | 96.1 | 100.0 | 92.2 | 83.3 | 100.0 | 99.2 | 54.3 | 100.0 |
| poetry | ai_none | 186 | 93.5 | 100.0 | 100.0 | 75.8 | 88.7 | 100.0 | 100.0 | 43.5 | 100.0 |
| recipes | ai_none | 139 | 59.7 | 84.2 | 99.3 | 24.5 | 64.0 | 64.7 | 90.6 | 51.1 | 100.0 |
| reddit | ai_none | 146 | 63.0 | 95.9 | 99.3 | 15.8 | 19.2 | 97.3 | 92.5 | 29.5 | 100.0 |
| reviews | ai_none | 147 | 100.0 | 100.0 | 100.0 | 96.6 | 100.0 | 100.0 | 100.0 | 65.3 | 100.0 |
| wiki | ai_none | 255 | 96.5 | 99.6 | 100.0 | 85.1 | 92.2 | 99.6 | 100.0 | 52.9 | 100.0 |
| abstracts | ai_adversarial (6 attacks) | 1,002 | 95.9 | 65.7 | 74.2 | 83.2 | 39.0 | 80.7 | 62.5 | 2.9 | 100.0 |
| books | ai_adversarial (6 attacks) | 1,486 | 91.3 | 76.9 | 74.6 | 80.9 | 53.3 | 83.3 | 51.3 | 10.6 | 100.0 |
| news | ai_adversarial (6 attacks) | 1,530 | 86.9 | 73.2 | 77.1 | 91.6 | 40.1 | 83.4 | 57.2 | 9.0 | 100.0 |
| poetry | ai_adversarial (6 attacks) | 976 | 89.2 | 73.7 | 71.9 | 70.0 | 50.8 | 82.0 | 69.8 | 9.8 | 100.0 |
| recipes | ai_adversarial (6 attacks) | 1,061 | 47.2 | 52.7 | 58.6 | 19.1 | 19.2 | 36.4 | 29.0 | 3.1 | 100.0 |
| reddit | ai_adversarial (6 attacks) | 891 | 61.5 | 66.8 | 63.0 | 20.3 | 7.7 | 72.4 | 37.9 | 4.9 | 100.0 |
| reviews | ai_adversarial (6 attacks) | 871 | 99.2 | 82.1 | 79.7 | 96.4 | 57.4 | 82.5 | 59.2 | 12.2 | 100.0 |
| wiki | ai_adversarial (6 attacks) | 1,432 | 95.0 | 78.1 | 79.2 | 84.8 | 52.0 | 80.8 | 56.1 | 8.7 | 100.0 |
| abstracts | human | 484 | 0.0 | 0.0 | 0.0 | 0.6 | 0.0 | 0.0 | 0.0 | 0.6 | 0.0 |
| books | human | 530 | 0.2 | 0.0 | 0.0 | 1.9 | 0.2 | 0.0 | 0.0 | 0.2 | 0.0 |
| news | human | 512 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| poetry | human | 510 | 0.4 | 0.0 | 0.0 | 1.8 | 0.2 | 2.7 | 0.0 | 1.0 | 0.0 |
| recipes | human | 527 | 0.0 | 0.0 | 0.0 | 0.4 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| reddit | human | 434 | 0.5 | 0.0 | 0.0 | 0.5 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 |
| reviews | human | 435 | 0.5 | 0.0 | 0.0 | 0.7 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 |
| wiki | human | 486 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-haiku | ai_none | 388 | 89.4 | 99.2 | 100.0 | 77.1 | 82.0 | 97.7 | 99.5 | 63.1 | 100.0 |
| gemini-3-flash | ai_none | 388 | 80.7 | 92.0 | 100.0 | 63.7 | 68.6 | 92.5 | 96.9 | 40.2 | 100.0 |
| gpt-5.4-mini | ai_none | 382 | 90.1 | 97.1 | 99.5 | 76.7 | 80.9 | 96.1 | 95.8 | 19.9 | 100.0 |
| qwen-3.6-plus | ai_none | 388 | 92.3 | 99.7 | 100.0 | 78.4 | 89.2 | 98.7 | 99.7 | 68.0 | 100.0 |
| claude-haiku | ai_adversarial (6 attacks) | 2,286 | 87.1 | 73.8 | 74.5 | 72.6 | 42.3 | 77.6 | 56.4 | 9.8 | 100.0 |
| gemini-3-flash | ai_adversarial (6 attacks) | 2,325 | 76.3 | 65.4 | 71.2 | 62.1 | 33.8 | 73.4 | 49.9 | 7.2 | 100.0 |
| gpt-5.4-mini | ai_adversarial (6 attacks) | 2,314 | 84.3 | 69.2 | 67.2 | 74.1 | 40.8 | 74.6 | 46.5 | 2.0 | 100.0 |
| qwen-3.6-plus | ai_adversarial (6 attacks) | 2,324 | 89.3 | 78.3 | 78.7 | 75.0 | 47.9 | 78.5 | 59.5 | 12.4 | 100.0 |
