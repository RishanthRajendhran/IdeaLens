# Translation into English

50 sources per language in each of 24 languages, for the human pages and IdeaShift-X levels 0 and 5; 3,594 of 3,600
documents translated. Flagged of n on the original -> the English translation, global 1% cut (ours); Pangram 4 at its own
threshold. Spearman correlation of original and translated scores over all pairs: IdeaLens 0.946, ProseLens 0.878.

| Arm | Rate | IdeaLens | ProseLens | Pangram 4 |
|---|---|---|---|---|
| Human pages | FPR | 3/1200 -> 3/1197 | 0/1200 -> 3/1197 | 0/1198 -> 26/1197 |
| Level 0 (model ideas) | TPR | 1141/1200 -> 1130/1200 | 896/1200 -> 1178/1200 | 942/1200 -> 1200/1200 |
| Level 5 (human ideas, model prose) | FPR | 13/1200 -> 9/1197 | 419/1200 -> 571/1197 | 616/1200 -> 1161/1197 |
