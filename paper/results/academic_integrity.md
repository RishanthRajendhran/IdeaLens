### AcademicIntegrity: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Pre-ChatGPT abstracts (2013 to 2015). Every row carries the author's own ideas, so every flag is a false positive; the model conditions include a fresh abstract written from the author's article.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| human (original abstract) | human ideas (FPR) | 289 | 0.3 | 0.0 | 0.0 | 5.2 | 0.3 | 4.8 | 0.0 | 0.0 | 0.3 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) | human ideas, AI prose (FPR) | 867 | 8.2 | 3.7 | 83.9 | 8.5 | 4.3 | 54.7 | 69.4 | 2.5 | 96.4 |
| humanized (the four humanized versions) | human ideas, humanized prose (FPR) | 1,156 | 0.9 | 0.1 | 0.7 | 3.8 | 0.2 | 3.1 | 0.4 | 1.7 | 9.0 |

**Length.** Share under 500 words: human (original abstract) 99.3%, human ideas + AI prose (refined, refined with the article, fresh from the article) 100.0%, humanized (the four humanized versions) 99.0%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| human (original abstract) · < 500 | human ideas (FPR) | 287 | 0.3 | 0.0 | 0.0 | 5.2 | 0.3 | 4.9 | 0.0 | 0.0 | 0.3 |
| human (original abstract) · >= 500 | human ideas (FPR) | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) · < 500 | human ideas, AI prose (FPR) | 867 | 8.2 | 3.7 | 83.9 | 8.5 | 4.3 | 54.7 | 69.4 | 2.5 | 96.4 |
| humanized (the four humanized versions) · < 500 | human ideas, humanized prose (FPR) | 1,145 | 0.9 | 0.1 | 0.7 | 3.8 | 0.2 | 3.1 | 0.4 | 1.7 | 9.0 |
| humanized (the four humanized versions) · >= 500 | human ideas, humanized prose (FPR) | 11 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 9.1 |

### AcademicIntegrity: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| human (original abstract) | IdeaLens · outline | 0.0 | 0.0 | 1.0 | 3.5 |
| human (original abstract) | IdeaLens · document | 0.0 | 0.0 | 0.0 | 3.1 |
| human (original abstract) | ProseLens | 0.0 | 0.0 | 1.4 | 10.0 |
| human (original abstract) | IdeaLens-ModernBERT-L · outline | 0.3 | 1.7 | 9.0 | 23.9 |
| human (original abstract) | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 2.4 | 42.6 |
| human (original abstract) | ProseLens-ModernBERT-L | 1.4 | 4.2 | 8.7 | 46.0 |
| human (original abstract) | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.0 | 4.5 |
| human (original abstract) | Binoculars (cal.) | 0.0 | 0.0 | 9.0 | 13.8 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) | IdeaLens · outline | 1.6 | 5.2 | 13.8 | 24.1 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) | IdeaLens · document | 0.2 | 1.7 | 17.1 | 43.7 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) | ProseLens | 52.5 | 72.3 | 94.9 | 99.3 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) | IdeaLens-ModernBERT-L · outline | 0.7 | 5.0 | 19.3 | 43.4 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) | IdeaLens-ModernBERT-L · document | 0.1 | 1.2 | 28.4 | 82.9 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) | ProseLens-ModernBERT-L | 7.2 | 31.5 | 91.5 | 99.8 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) | EditLens-Llama-3B (cal.) | 0.0 | 33.3 | 90.3 | 99.1 |
| human ideas + AI prose (refined, refined with the article, fresh from the article) | Binoculars (cal.) | 0.2 | 2.5 | 20.8 | 37.0 |
| humanized (the four humanized versions) | IdeaLens · outline | 0.1 | 0.6 | 2.0 | 5.2 |
| humanized (the four humanized versions) | IdeaLens · document | 0.0 | 0.0 | 0.2 | 3.0 |
| humanized (the four humanized versions) | ProseLens | 0.1 | 0.3 | 1.6 | 9.4 |
| humanized (the four humanized versions) | IdeaLens-ModernBERT-L · outline | 0.3 | 1.7 | 9.0 | 25.5 |
| humanized (the four humanized versions) | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 2.5 | 36.5 |
| humanized (the four humanized versions) | ProseLens-ModernBERT-L | 0.7 | 1.5 | 6.7 | 32.3 |
| humanized (the four humanized versions) | EditLens-Llama-3B (cal.) | 0.0 | 0.1 | 1.9 | 7.5 |
| humanized (the four humanized versions) | Binoculars (cal.) | 0.3 | 1.8 | 12.3 | 21.5 |

**By arm.** Fire rate % at the 1% cut.

| Arm | Description | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| original__raw | human (original abstract) | 289 | 0.3 | 0.0 | 0.0 | 5.2 | 0.3 | 4.8 | 0.0 | 0.0 | 0.3 |
| new_article_only__raw | human ideas + AI prose (refined, refined with the article, fresh from the article) | 289 | 12.1 | 6.6 | 94.1 | 11.4 | 5.9 | 69.2 | 91.0 | 1.4 | 98.6 |
| refine_abstract_article__raw | human ideas + AI prose (refined, refined with the article, fresh from the article) | 289 | 6.9 | 2.1 | 81.3 | 7.3 | 3.1 | 50.2 | 63.7 | 2.1 | 95.2 |
| refine_abstract_only__raw | human ideas + AI prose (refined, refined with the article, fresh from the article) | 289 | 5.5 | 2.4 | 76.1 | 6.9 | 3.8 | 44.6 | 53.6 | 4.2 | 95.5 |
| new_article_only__humanized | humanized (the four humanized versions) | 289 | 1.0 | 0.0 | 0.3 | 3.5 | 0.0 | 0.3 | 0.0 | 0.7 | 16.6 |
| original__humanized | humanized (the four humanized versions) | 289 | 0.0 | 0.0 | 0.0 | 5.2 | 0.3 | 3.1 | 0.0 | 3.5 | 1.7 |
| refine_abstract_article__humanized | humanized (the four humanized versions) | 289 | 1.4 | 0.0 | 0.7 | 2.8 | 0.3 | 3.8 | 0.7 | 0.7 | 8.7 |
| refine_abstract_only__humanized | humanized (the four humanized versions) | 289 | 1.0 | 0.3 | 1.7 | 3.8 | 0.0 | 5.2 | 1.0 | 2.1 | 9.0 |

**By domain.** Fire rate % at the 1% cut.

| Domain | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chemistry | human (original abstract) | 84 | 0.0 | 0.0 | 0.0 | 2.4 | 0.0 | 0.0 | 0.0 | 0.0 | 1.2 |
| computer_science | human (original abstract) | 68 | 0.0 | 0.0 | 0.0 | 2.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| political_science | human (original abstract) | 63 | 1.6 | 0.0 | 0.0 | 4.8 | 1.6 | 3.2 | 0.0 | 0.0 | 0.0 |
| theology | human (original abstract) | 74 | 0.0 | 0.0 | 0.0 | 10.8 | 0.0 | 16.2 | 0.0 | 0.0 | 0.0 |
| chemistry | human ideas + AI prose (refined, refined with the article, fresh from the article) | 252 | 6.0 | 1.6 | 69.0 | 7.1 | 3.2 | 35.3 | 59.1 | 2.4 | 91.7 |
| computer_science | human ideas + AI prose (refined, refined with the article, fresh from the article) | 204 | 3.4 | 1.0 | 83.8 | 12.3 | 4.9 | 56.9 | 59.3 | 1.0 | 98.5 |
| political_science | human ideas + AI prose (refined, refined with the article, fresh from the article) | 189 | 12.7 | 7.4 | 95.8 | 9.5 | 5.8 | 62.4 | 83.6 | 4.8 | 100.0 |
| theology | human ideas + AI prose (refined, refined with the article, fresh from the article) | 222 | 11.3 | 5.4 | 90.5 | 5.9 | 3.6 | 68.0 | 78.4 | 2.3 | 96.8 |
| chemistry | humanized (the four humanized versions) | 336 | 0.9 | 0.0 | 0.0 | 2.4 | 0.3 | 0.0 | 0.0 | 0.9 | 3.6 |
| computer_science | humanized (the four humanized versions) | 272 | 0.4 | 0.0 | 0.0 | 5.1 | 0.0 | 0.0 | 0.0 | 1.8 | 9.9 |
| political_science | humanized (the four humanized versions) | 252 | 2.0 | 0.4 | 0.8 | 5.2 | 0.4 | 3.2 | 0.8 | 2.8 | 8.3 |
| theology | humanized (the four humanized versions) | 296 | 0.3 | 0.0 | 2.0 | 3.0 | 0.0 | 9.5 | 1.0 | 1.7 | 14.9 |

**By year.** Fire rate % at the 1% cut.

| Year | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2013 | human (original abstract) | 76 | 0.0 | 0.0 | 0.0 | 6.6 | 0.0 | 2.6 | 0.0 | 0.0 | 0.0 |
| 2014 | human (original abstract) | 106 | 0.0 | 0.0 | 0.0 | 3.8 | 0.0 | 2.8 | 0.0 | 0.0 | 0.0 |
| 2015 | human (original abstract) | 107 | 0.9 | 0.0 | 0.0 | 5.6 | 0.9 | 8.4 | 0.0 | 0.0 | 0.9 |
| 2013 | human ideas + AI prose (refined, refined with the article, fresh from the article) | 228 | 4.4 | 1.3 | 77.6 | 8.3 | 4.4 | 47.4 | 64.9 | 1.8 | 95.6 |
| 2014 | human ideas + AI prose (refined, refined with the article, fresh from the article) | 318 | 10.4 | 4.1 | 85.8 | 9.7 | 5.7 | 56.9 | 66.7 | 2.8 | 97.2 |
| 2015 | human ideas + AI prose (refined, refined with the article, fresh from the article) | 321 | 8.7 | 5.0 | 86.3 | 7.5 | 2.8 | 57.6 | 75.4 | 2.8 | 96.3 |
| 2013 | humanized (the four humanized versions) | 304 | 0.7 | 0.0 | 0.0 | 5.3 | 0.0 | 1.6 | 0.0 | 1.6 | 9.9 |
| 2014 | humanized (the four humanized versions) | 424 | 1.2 | 0.2 | 0.5 | 3.8 | 0.2 | 2.8 | 0.5 | 1.2 | 8.5 |
| 2015 | humanized (the four humanized versions) | 428 | 0.7 | 0.0 | 1.4 | 2.8 | 0.2 | 4.4 | 0.7 | 2.3 | 8.9 |

**Commercial verdicts shipped with the corpus** (identical documents; share flagged).

| Arm | n | Pangram 3.2 (shipped) | GPTZero (shipped) |
|---|---|---|---|
| original__raw | 289 | 0.0 | 0.0 |
| refine_abstract_only__raw | 289 | 63.3 | 36.7 |
| refine_abstract_article__raw | 289 | 79.2 | 44.3 |
| new_article_only__raw | 289 | 97.2 | 83.4 |
| original__humanized | 289 | 0.3 | 1.4 |
| refine_abstract_only__humanized | 289 | 3.5 | 3.1 |
| refine_abstract_article__humanized | 289 | 0.7 | 5.2 |
| new_article_only__humanized | 289 | 0.0 | 3.5 |

**P(AI) gradation** (mean / median %; not in the main table).

| Arm | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | Pangram 4 |
|---|---|---|---|---|---|---|---|
| original__raw | 3.6 / 0.2 | 0.7 / 0.1 | 0.2 / 0.0 | 23.1 / 10.0 | 7.1 / 1.1 | 7.3 / 0.1 | 0.2 / 0.0 |
| refine_abstract_only__raw | 13.4 / 1.2 | 12.6 / 0.9 | 68.9 / 85.1 | 32.6 / 17.6 | 30.6 / 13.6 | 66.4 / 76.8 | 63.4 / 50.0 |
| refine_abstract_article__raw | 14.6 / 1.5 | 13.6 / 1.1 | 74.5 / 92.1 | 34.2 / 19.7 | 30.7 / 13.8 | 68.6 / 82.6 | 69.1 / 58.5 |
| new_article_only__raw | 31.2 / 12.2 | 32.4 / 16.4 | 89.2 / 98.9 | 48.6 / 48.4 | 46.2 / 45.2 | 81.8 / 93.5 | 94.8 / 100.0 |
| original__humanized | 2.7 / 0.3 | 0.7 / 0.1 | 0.2 / 0.0 | 23.2 / 8.4 | 6.1 / 0.9 | 5.5 / 0.1 | 2.8 / 0.0 |
| refine_abstract_only__humanized | 5.6 / 0.3 | 1.6 / 0.1 | 1.8 / 0.0 | 24.7 / 8.3 | 9.4 / 1.7 | 8.9 / 0.1 | 8.1 / 0.0 |
| refine_abstract_article__humanized | 4.8 / 0.3 | 0.3 / 0.0 | 0.7 / 0.0 | 21.5 / 7.9 | 5.4 / 0.7 | 4.5 / 0.0 | 8.4 / 0.0 |
| new_article_only__humanized | 6.2 / 0.4 | 0.2 / 0.0 | 0.3 / 0.0 | 24.8 / 9.5 | 5.4 / 0.9 | 1.2 / 0.0 | 16.7 / 0.0 |
