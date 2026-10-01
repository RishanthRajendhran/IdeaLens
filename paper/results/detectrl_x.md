### DetectRL-X (with the attack sweep): main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| English · ai_none | model ideas (TPR) | 7,451 | 87.3 | 98.6 | 100.0 | 67.3 | 85.3 | 97.6 | 92.9 | 26.1 | 99.7 |
| English · ai_adversarial | model ideas (TPR) | 5,296 | 83.8 | 93.1 | 97.1 | 64.4 | 75.4 | 90.9 | 84.1 | 20.0 | 97.9 |
| English · human | human ideas (FPR) | 7,169 | 4.8 | 4.1 | 11.3 | 2.4 | 1.1 | 6.1 | 1.0 | 11.4 | 3.3 |
| non-English · ai_none | model ideas (TPR) | 6,865 | 86.8 | 95.6 | 99.9 | 73.2 | – | – | 73.8 | 4.0 | 98.5 |
| non-English · human | human ideas (FPR) | 6,594 | 0.3 | 0.1 | 0.2 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |
| AUC, English | | | 0.974 | 0.989 | 0.991 | 0.960 | 0.985 | 0.985 | 0.993 | 0.704 | 0.994 |
| AUC, non-English | | | 0.998 | 1.000 | 1.000 | 0.994 | – | – | 0.999 | 0.708 | 0.997 |

**Length.** Share under 500 words: English · ai_none 80.3%, English · ai_adversarial 75.8%, English · human 82.2%, non-English · ai_none 77.1%, non-English · human 74.7%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| English · ai_none · < 500 | model ideas (TPR) | 5,984 | 85.5 | 98.2 | 100.0 | 62.4 | 82.0 | 97.0 | 95.4 | 22.5 | 99.7 |
| English · ai_none · >= 500 | model ideas (TPR) | 1,467 | 94.9 | 100.0 | 100.0 | 87.5 | 98.8 | 100.0 | 83.0 | 40.9 | 99.9 |
| English · ai_adversarial · < 500 | model ideas (TPR) | 4,016 | 80.8 | 92.2 | 96.3 | 57.7 | 70.4 | 89.4 | 83.8 | 14.1 | 97.4 |
| English · ai_adversarial · >= 500 | model ideas (TPR) | 1,280 | 93.0 | 95.7 | 99.5 | 85.3 | 90.8 | 95.5 | 85.3 | 38.4 | 99.5 |
| English · human · < 500 | human ideas (FPR) | 5,895 | 5.7 | 5.0 | 13.6 | 2.6 | 1.3 | 7.4 | 1.2 | 13.8 | 4.0 |
| English · human · >= 500 | human ideas (FPR) | 1,274 | 0.5 | 0.2 | 0.3 | 1.0 | 0.0 | 0.2 | 0.0 | 0.1 | 0.0 |
| non-English · ai_none · < 500 | model ideas (TPR) | 5,290 | 84.3 | 94.4 | 99.8 | 70.1 | – | – | 81.7 | 2.0 | 98.3 |
| non-English · ai_none · >= 500 | model ideas (TPR) | 1,575 | 95.2 | 99.9 | 100.0 | 83.7 | – | – | 47.0 | 10.6 | 98.9 |
| non-English · human · < 500 | human ideas (FPR) | 4,928 | 0.2 | 0.0 | 0.1 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |
| non-English · human · >= 500 | human ideas (FPR) | 1,666 | 0.3 | 0.1 | 0.4 | 0.3 | – | – | 0.1 | 0.0 | 0.0 |

### DetectRL-X (with the attack sweep): appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| English · ai_none | IdeaLens · outline | 52.7 | 78.8 | 94.5 | 97.8 |
| English · ai_none | IdeaLens · document | 77.3 | 94.6 | 99.8 | 100.0 |
| English · ai_none | ProseLens | 98.4 | 99.9 | 100.0 | 100.0 |
| English · ai_none | IdeaLens-ModernBERT-L · outline | 32.1 | 55.1 | 81.1 | 93.8 |
| English · ai_none | IdeaLens-ModernBERT-L · document | 36.3 | 64.1 | 97.7 | 99.9 |
| English · ai_none | ProseLens-ModernBERT-L | 56.6 | 89.6 | 99.9 | 100.0 |
| English · ai_none | EditLens-Llama-3B (cal.) | 0.0 | 74.5 | 99.4 | 100.0 |
| English · ai_none | Binoculars (cal.) | 12.9 | 26.6 | 57.0 | 72.1 |
| English · ai_adversarial | IdeaLens · outline | 49.3 | 75.1 | 91.1 | 95.0 |
| English · ai_adversarial | IdeaLens · document | 71.1 | 87.2 | 95.7 | 97.2 |
| English · ai_adversarial | ProseLens | 92.1 | 95.5 | 98.2 | 99.4 |
| English · ai_adversarial | IdeaLens-ModernBERT-L · outline | 30.6 | 52.9 | 78.3 | 91.0 |
| English · ai_adversarial | IdeaLens-ModernBERT-L · document | 29.9 | 54.7 | 91.2 | 97.0 |
| English · ai_adversarial | ProseLens-ModernBERT-L | 51.7 | 81.6 | 96.2 | 98.5 |
| English · ai_adversarial | EditLens-Llama-3B (cal.) | 0.0 | 64.7 | 92.3 | 96.4 |
| English · ai_adversarial | Binoculars (cal.) | 10.0 | 20.3 | 44.7 | 57.6 |
| English · human | IdeaLens · outline | 0.8 | 3.2 | 7.4 | 11.5 |
| English · human | IdeaLens · document | 0.9 | 2.1 | 9.3 | 15.1 |
| English · human | ProseLens | 5.6 | 9.2 | 13.4 | 15.2 |
| English · human | IdeaLens-ModernBERT-L · outline | 0.0 | 1.0 | 5.5 | 14.0 |
| English · human | IdeaLens-ModernBERT-L · document | 0.0 | 0.4 | 5.0 | 23.9 |
| English · human | ProseLens-ModernBERT-L | 0.2 | 2.6 | 12.5 | 26.9 |
| English · human | EditLens-Llama-3B (cal.) | 0.0 | 0.5 | 2.4 | 6.4 |
| English · human | Binoculars (cal.) | 4.4 | 11.6 | 22.1 | 29.9 |
| non-English · ai_none | IdeaLens · outline | 51.6 | 78.8 | 93.6 | 97.2 |
| non-English · ai_none | IdeaLens · document | 73.2 | 89.5 | 99.4 | 99.9 |
| non-English · ai_none | ProseLens | 97.8 | 99.6 | 100.0 | 100.0 |
| non-English · ai_none | IdeaLens-ModernBERT-L · outline | 26.9 | 58.4 | 87.2 | 96.4 |
| non-English · ai_none | IdeaLens-ModernBERT-L · document | – | – | – | – |
| non-English · ai_none | ProseLens-ModernBERT-L | – | – | – | – |
| non-English · ai_none | EditLens-Llama-3B (cal.) | 0.0 | 38.2 | 94.5 | 99.9 |
| non-English · ai_none | Binoculars (cal.) | 0.4 | 4.1 | 16.6 | 28.0 |
| non-English · human | IdeaLens · outline | 0.1 | 0.2 | 0.5 | 1.3 |
| non-English · human | IdeaLens · document | 0.0 | 0.0 | 0.2 | 0.8 |
| non-English · human | ProseLens | 0.1 | 0.1 | 0.3 | 0.6 |
| non-English · human | IdeaLens-ModernBERT-L · outline | 0.0 | 0.2 | 0.7 | 3.6 |
| non-English · human | IdeaLens-ModernBERT-L · document | – | – | – | – |
| non-English · human | ProseLens-ModernBERT-L | – | – | – | – |
| non-English · human | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.4 | 11.1 |
| non-English · human | Binoculars (cal.) | 0.0 | 0.0 | 0.7 | 3.7 |

**By language.** Fire rate % at the 1% cut.

| Language | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| arabic | non-English · ai_none | 995 | 87.0 | 92.1 | 99.8 | 78.0 | – | – | 59.6 | 0.1 | 97.9 |
| chinese | non-English · ai_none | 984 | 77.5 | 94.0 | 99.9 | 66.1 | – | – | 64.5 | 0.0 | 99.7 |
| french | non-English · ai_none | 998 | 90.0 | 99.4 | 100.0 | 75.4 | – | – | 81.6 | 13.8 | 99.5 |
| german | non-English · ai_none | 996 | 85.5 | 96.9 | 100.0 | 71.4 | – | – | 81.3 | 0.1 | 98.8 |
| portuguese | non-English · ai_none | 999 | 94.6 | 99.4 | 100.0 | 78.4 | – | – | 84.6 | 4.6 | 96.5 |
| russian | non-English · ai_none | 993 | 81.6 | 89.4 | 99.3 | 63.4 | – | – | 58.2 | 0.0 | 98.5 |
| spanish | non-English · ai_none | 900 | 91.4 | 98.6 | 100.0 | 80.4 | – | – | 87.8 | 9.6 | 98.3 |
| arabic | non-English · human | 968 | 0.3 | 0.1 | 0.1 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |
| chinese | non-English · human | 881 | 0.5 | 0.0 | 0.2 | 0.5 | – | – | 0.0 | 0.0 | 0.1 |
| french | non-English · human | 958 | 0.4 | 0.2 | 0.6 | 0.3 | – | – | 0.1 | 0.0 | 0.0 |
| german | non-English · human | 988 | 0.2 | 0.1 | 0.3 | 0.2 | – | – | 0.0 | 0.0 | 0.0 |
| portuguese | non-English · human | 991 | 0.4 | 0.0 | 0.0 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |
| russian | non-English · human | 981 | 0.0 | 0.0 | 0.0 | 0.2 | – | – | 0.0 | 0.0 | 0.0 |
| spanish | non-English · human | 827 | 0.0 | 0.0 | 0.0 | 0.2 | – | – | 0.0 | 0.0 | 0.0 |

**By attack.** Fire rate % at the 1% cut.

| Attack | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai_backtranslation | English · ai_adversarial | 487 | 87.3 | 90.3 | 97.3 | 65.7 | 66.3 | 80.5 | 66.3 | 18.9 | 99.8 |
| ai_character_deletion | English · ai_adversarial | 496 | 86.9 | 98.0 | 99.8 | 66.3 | 79.4 | 96.4 | 89.1 | 18.8 | 99.8 |
| ai_character_insertion | English · ai_adversarial | 493 | 86.0 | 98.0 | 99.8 | 65.9 | 78.1 | 96.8 | 89.0 | 19.1 | 100.0 |
| ai_character_substitution | English · ai_adversarial | 482 | 86.3 | 98.5 | 100.0 | 66.6 | 73.2 | 97.9 | 91.1 | 18.7 | 99.8 |
| ai_condensing | English · ai_adversarial | 497 | 83.7 | 96.8 | 99.0 | 63.6 | 77.1 | 91.8 | 90.5 | 18.9 | 99.8 |
| ai_decoder_paraphrasing | English · ai_adversarial | 486 | 59.7 | 64.2 | 74.5 | 44.0 | 55.8 | 68.7 | 62.8 | 20.6 | 80.2 |
| ai_encoder_paraphrasing | English · ai_adversarial | 491 | 85.7 | 96.3 | 99.4 | 66.6 | 71.1 | 91.0 | 75.4 | 18.9 | 100.0 |
| ai_expanding | English · ai_adversarial | 499 | 92.4 | 99.2 | 100.0 | 76.8 | 91.2 | 98.4 | 96.6 | 24.8 | 100.0 |
| ai_polishing | English · ai_adversarial | 497 | 88.3 | 98.2 | 100.0 | 65.4 | 83.3 | 96.8 | 91.5 | 18.9 | 99.8 |
| ai_seq2seq_paraphrasing | English · ai_adversarial | 372 | 76.9 | 82.5 | 97.8 | 59.7 | 72.0 | 82.0 | 80.1 | 24.2 | 98.1 |
| ai_zero_width_insertion | English · ai_adversarial | 496 | 86.1 | 98.6 | 100.0 | 66.1 | 79.8 | 97.2 | 91.3 | 19.4 | 99.6 |

**By plan.** Fire rate % at the 1% cut.

| Plan | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | English · ai_none | 992 | 87.0 | 99.1 | 100.0 | 68.9 | 85.3 | 97.9 | 92.0 | 27.3 | 99.9 |
| B | English · ai_none | 5,962 | 87.4 | 98.5 | 100.0 | 67.3 | 85.4 | 97.6 | 93.0 | 25.9 | 99.7 |
| C | English · ai_none | 497 | 86.9 | 98.4 | 100.0 | 65.0 | 84.1 | 97.2 | 93.6 | 26.2 | 99.8 |
| C | English · ai_adversarial | 5,296 | 83.8 | 93.1 | 97.1 | 64.4 | 75.4 | 90.9 | 84.1 | 20.0 | 97.9 |
| A | English · human | 950 | 4.6 | 4.3 | 11.7 | 2.0 | 1.2 | 6.2 | 1.1 | 11.4 | 3.5 |
| B | English · human | 5,745 | 4.9 | 4.1 | 11.2 | 2.4 | 1.1 | 6.2 | 1.0 | 11.4 | 3.2 |
| C | English · human | 474 | 3.8 | 4.0 | 10.5 | 2.1 | 1.3 | 4.9 | 0.6 | 10.5 | 3.0 |
| A | non-English · ai_none | 6,865 | 86.8 | 95.6 | 99.9 | 73.2 | – | – | 73.8 | 4.0 | 98.5 |
| A | non-English · human | 6,594 | 0.3 | 0.1 | 0.2 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |

**By domain.** Fire rate % at the 1% cut.

| Domain | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Academic | English · ai_none | 1,246 | 89.7 | 95.3 | 100.0 | 69.4 | 75.4 | 99.2 | 99.5 | 26.9 | 100.0 |
| News | English · ai_none | 1,252 | 96.1 | 98.8 | 100.0 | 96.6 | 98.0 | 100.0 | 99.4 | 29.1 | 100.0 |
| Novel | English · ai_none | 1,237 | 96.1 | 99.9 | 100.0 | 89.1 | 98.2 | 100.0 | 79.9 | 38.3 | 100.0 |
| SEO | English · ai_none | 1,262 | 71.1 | 99.0 | 99.9 | 17.8 | 60.9 | 88.5 | 86.5 | 14.7 | 99.8 |
| Webtext | English · ai_none | 1,232 | 84.6 | 99.2 | 100.0 | 65.7 | 87.7 | 99.7 | 95.9 | 23.5 | 99.9 |
| Wiki | English · ai_none | 1,222 | 86.5 | 99.2 | 100.0 | 66.1 | 91.8 | 98.4 | 96.5 | 24.2 | 98.6 |
| Academic | English · ai_adversarial | 830 | 83.6 | 88.4 | 96.4 | 66.4 | 63.4 | 92.3 | 92.3 | 20.5 | 98.7 |
| News | English · ai_adversarial | 900 | 92.2 | 94.8 | 98.4 | 93.4 | 88.4 | 96.3 | 92.3 | 23.0 | 99.1 |
| Novel | English · ai_adversarial | 901 | 93.1 | 93.8 | 98.0 | 88.3 | 86.1 | 93.0 | 76.2 | 32.3 | 97.7 |
| SEO | English · ai_adversarial | 1,035 | 65.2 | 92.9 | 95.2 | 14.3 | 57.5 | 80.4 | 74.2 | 12.4 | 97.3 |
| Webtext | English · ai_adversarial | 805 | 86.3 | 94.3 | 99.1 | 62.0 | 74.7 | 95.2 | 86.5 | 15.7 | 98.6 |
| Wiki | English · ai_adversarial | 825 | 85.2 | 94.1 | 95.6 | 69.7 | 84.5 | 90.4 | 85.8 | 16.7 | 96.2 |
| Academic | English · human | 1,240 | 0.4 | 0.2 | 0.5 | 0.3 | 0.1 | 0.1 | 0.1 | 0.0 | 0.5 |
| News | English · human | 1,240 | 1.0 | 0.0 | 0.0 | 2.9 | 0.0 | 0.2 | 0.0 | 3.4 | 0.0 |
| Novel | English · human | 1,200 | 0.4 | 0.0 | 0.0 | 1.1 | 0.1 | 0.1 | 0.1 | 0.0 | 0.0 |
| SEO | English · human | 1,268 | 7.6 | 8.7 | 9.0 | 1.9 | 4.1 | 7.3 | 3.5 | 4.5 | 5.4 |
| Webtext | English · human | 1,008 | 22.3 | 18.3 | 68.2 | 9.1 | 2.5 | 33.6 | 2.6 | 70.8 | 15.8 |
| Wiki | English · human | 1,213 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 |
| Academic | non-English · ai_none | 1,173 | 88.6 | 98.0 | 100.0 | 75.6 | – | – | 72.5 | 5.0 | 99.5 |
| News | non-English · ai_none | 1,211 | 85.5 | 88.4 | 99.7 | 81.4 | – | – | 85.0 | 3.1 | 99.3 |
| Novel | non-English · ai_none | 1,136 | 93.7 | 99.0 | 100.0 | 87.4 | – | – | 46.7 | 8.1 | 99.9 |
| SEO | non-English · ai_none | 984 | 87.8 | 99.3 | 100.0 | 55.5 | – | – | 78.3 | 1.3 | 99.0 |
| Webtext | non-English · ai_none | 1,193 | 79.9 | 95.4 | 100.0 | 68.2 | – | – | 81.4 | 2.3 | 97.2 |
| Wiki | non-English · ai_none | 1,168 | 85.8 | 94.6 | 99.5 | 68.5 | – | – | 78.3 | 3.6 | 95.9 |
| Academic | non-English · human | 1,174 | 0.3 | 0.2 | 0.7 | 0.3 | – | – | 0.1 | 0.0 | 0.1 |
| News | non-English · human | 1,153 | 0.3 | 0.0 | 0.0 | 0.3 | – | – | 0.0 | 0.0 | 0.0 |
| Novel | non-English · human | 1,097 | 0.3 | 0.1 | 0.1 | 0.6 | – | – | 0.0 | 0.0 | 0.0 |
| SEO | non-English · human | 901 | 0.2 | 0.1 | 0.3 | 0.1 | – | – | 0.0 | 0.0 | 0.0 |
| Webtext | non-English · human | 1,102 | 0.5 | 0.0 | 0.0 | 0.5 | – | – | 0.0 | 0.0 | 0.0 |
| Wiki | non-English · human | 1,167 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 | 0.0 | 0.0 |

**By generator.** Fire rate % at the 1% cut.

| Generator | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek-v3 | English · ai_none | 1,839 | 92.4 | 99.6 | 100.0 | 72.1 | 88.5 | 99.0 | 95.2 | 6.8 | 99.9 |
| gemini-2.5-flash | English · ai_none | 1,852 | 76.8 | 95.8 | 100.0 | 55.1 | 78.9 | 97.1 | 92.1 | 7.1 | 99.8 |
| gpt-4o | English · ai_none | 1,850 | 90.6 | 99.7 | 100.0 | 71.6 | 89.2 | 98.1 | 88.8 | 4.9 | 99.6 |
| qwen-max | English · ai_none | 1,910 | 89.4 | 99.1 | 99.9 | 70.6 | 84.5 | 96.3 | 95.7 | 83.6 | 99.6 |
| deepseek-v3 | English · ai_adversarial | 1,167 | 89.8 | 93.9 | 97.3 | 66.3 | 78.3 | 92.4 | 88.5 | 4.5 | 97.9 |
| gemini-2.5-flash | English · ai_adversarial | 1,464 | 75.6 | 90.6 | 97.1 | 57.7 | 68.7 | 91.9 | 78.8 | 7.1 | 97.8 |
| gpt-4o | English · ai_adversarial | 1,218 | 88.1 | 94.8 | 97.5 | 69.0 | 81.7 | 91.1 | 83.6 | 4.8 | 98.3 |
| qwen-max | English · ai_adversarial | 1,447 | 83.5 | 93.4 | 96.5 | 65.7 | 74.4 | 88.6 | 86.5 | 58.4 | 97.7 |
| deepseek-v3 | English · human | 1,779 | 4.6 | 3.9 | 11.5 | 2.4 | 1.0 | 6.2 | 1.0 | 11.6 | 2.8 |
| gemini-2.5-flash | English · human | 1,778 | 5.8 | 4.6 | 11.4 | 3.0 | 1.5 | 6.9 | 1.1 | 12.8 | 3.3 |
| gpt-4o | English · human | 1,773 | 3.9 | 3.5 | 11.2 | 2.0 | 0.8 | 5.8 | 0.7 | 10.3 | 3.3 |
| qwen-max | English · human | 1,839 | 4.9 | 4.5 | 11.0 | 2.1 | 1.2 | 5.5 | 1.1 | 10.8 | 3.6 |
| deepseek-v3 | non-English · ai_none | 1,731 | 85.9 | 95.0 | 99.8 | 69.6 | – | – | 75.8 | 0.1 | 100.0 |
| gemini-2.5-flash | non-English · ai_none | 1,685 | 82.4 | 95.3 | 99.9 | 65.8 | – | – | 64.5 | 0.0 | 99.6 |
| gpt-4o | non-English · ai_none | 1,752 | 88.4 | 96.3 | 99.8 | 78.8 | – | – | 70.9 | 0.1 | 98.5 |
| qwen-max | non-English · ai_none | 1,697 | 90.3 | 96.1 | 99.9 | 78.6 | – | – | 83.9 | 15.8 | 95.8 |
| deepseek-v3 | non-English · human | 1,660 | 0.1 | 0.0 | 0.1 | 0.1 | – | – | 0.0 | 0.0 | 0.0 |
| gemini-2.5-flash | non-English · human | 1,620 | 0.4 | 0.1 | 0.2 | 0.3 | – | – | 0.1 | 0.0 | 0.0 |
| gpt-4o | non-English · human | 1,674 | 0.3 | 0.1 | 0.2 | 0.4 | – | – | 0.0 | 0.0 | 0.0 |
| qwen-max | non-English · human | 1,640 | 0.2 | 0.1 | 0.2 | 0.4 | – | – | 0.0 | 0.0 | 0.1 |

**Other model x input columns.** Fire rate % at the 1% cut.

| Arm | n | ProseLens · raw outline |
|---|---|---|
| English · ai_none | 7,451 | 99.2 |
| English · ai_adversarial | 5,296 | 98.6 |
| English · human | 7,169 | 68.7 |
| non-English · ai_none | 6,865 | 99.7 |
| non-English · human | 6,594 | 72.3 |
