### excerpt vs full: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Source documents cut to random 500-word excerpts on sentence boundaries; each excerpt's format was re-classified from the excerpt alone, as in use. Two builds: the original (1,486 rows) and the 2026-09-08 rebuild (4,967 rows, full documents added 2026-09-10). 2,349 full documents, 4,104 excerpts.
- Our outline-trained models on the raw outline, global calibrated cut. The original build carries no window or source-length fields, so those splits cover the rebuild only.
- Format gate: 'forced format' excerpts were rejected by the format gate and forced into a format; 'gated' passed it (rebuild only).

| Arm | Label | n | IdeaLens · outline (raw) | IdeaLens-ModernBERT-L · outline (raw) |
|---|---|---|---|---|
| full document · AI | AI (TPR) | 1,196 | 96.5 | 88.6 |
| 500-word excerpt · AI | AI (TPR) | 2,059 | 91.4 | 71.6 |
| full document · human | human (FPR) | 1,153 | 3.1 | 2.8 |
| 500-word excerpt · human | human (FPR) | 2,045 | 2.8 | 2.0 |
| AUC, full documents | | | 0.995 | 0.989 |
| AUC, excerpts | | | 0.992 | 0.980 |

**Length.** Share under 500 words: full document · AI 0.0%, 500-word excerpt · AI 10.0%, full document · human 0.0%, 500-word excerpt · human 8.4%.

| Arm · length | Label | n | IdeaLens · outline (raw) | IdeaLens-ModernBERT-L · outline (raw) |
|---|---|---|---|---|
| full document · AI · >= 500 | AI (TPR) | 1,196 | 96.5 | 88.6 |
| 500-word excerpt · AI · < 500 | AI (TPR) | 206 | 95.1 | 73.8 |
| 500-word excerpt · AI · >= 500 | AI (TPR) | 1,853 | 90.9 | 71.3 |
| full document · human · >= 500 | human (FPR) | 1,153 | 3.1 | 2.8 |
| 500-word excerpt · human · < 500 | human (FPR) | 172 | 5.2 | 2.9 |
| 500-word excerpt · human · >= 500 | human (FPR) | 1,873 | 2.6 | 1.9 |

### excerpt vs full: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| full document · AI | IdeaLens · outline (raw) | 80.0 | 93.3 | 98.8 | 99.6 |
| full document · AI | IdeaLens-ModernBERT-L · outline (raw) | 57.9 | 80.4 | 96.2 | 98.7 |
| 500-word excerpt · AI | IdeaLens · outline (raw) | 63.1 | 85.1 | 96.2 | 98.3 |
| 500-word excerpt · AI | IdeaLens-ModernBERT-L · outline (raw) | 32.6 | 58.6 | 86.1 | 94.9 |
| full document · human | IdeaLens · outline (raw) | 0.6 | 2.3 | 4.6 | 6.9 |
| full document · human | IdeaLens-ModernBERT-L · outline (raw) | 0.2 | 1.6 | 4.9 | 9.1 |
| 500-word excerpt · human | IdeaLens · outline (raw) | 0.3 | 1.5 | 4.4 | 6.4 |
| 500-word excerpt · human | IdeaLens-ModernBERT-L · outline (raw) | 0.0 | 0.9 | 3.6 | 8.0 |

**By build.** Fire rate % at the 1% cut.

| Build | Arm | n | IdeaLens · outline (raw) | IdeaLens-ModernBERT-L · outline (raw) |
|---|---|---|---|---|
| 2026-09-08 rebuild | full document · AI | 900 | 97.1 | 88.6 |
| original build | full document · AI | 296 | 94.6 | 88.9 |
| 2026-09-08 rebuild | 500-word excerpt · AI | 1,637 | 93.1 | 72.6 |
| original build | 500-word excerpt · AI | 422 | 84.6 | 67.5 |
| 2026-09-08 rebuild | full document · human | 857 | 3.5 | 2.3 |
| original build | full document · human | 296 | 2.0 | 4.1 |
| 2026-09-08 rebuild | 500-word excerpt · human | 1,573 | 3.1 | 1.9 |
| original build | 500-word excerpt · human | 472 | 1.9 | 2.1 |

**By source length.** Fire rate % at the 1% cut.

| Source length | Arm | n | IdeaLens · outline (raw) | IdeaLens-ModernBERT-L · outline (raw) |
|---|---|---|---|---|
| 1.2-2k | full document · AI | 221 | 97.3 | 90.5 |
| 2k+ | full document · AI | 244 | 98.0 | 88.1 |
| 500-800 | full document · AI | 226 | 96.0 | 88.5 |
| 800-1.2k | full document · AI | 209 | 97.1 | 87.1 |
| 1.2-2k | 500-word excerpt · AI | 442 | 93.9 | 72.6 |
| 2k+ | 500-word excerpt · AI | 488 | 94.3 | 76.2 |
| 500-800 | 500-word excerpt · AI | 289 | 92.7 | 71.3 |
| 800-1.2k | 500-word excerpt · AI | 418 | 91.1 | 69.4 |
| 1.2-2k | full document · human | 224 | 3.1 | 2.7 |
| 2k+ | full document · human | 254 | 2.4 | 1.2 |
| 500-800 | full document · human | 203 | 3.4 | 2.5 |
| 800-1.2k | full document · human | 176 | 5.7 | 3.4 |
| 1.2-2k | 500-word excerpt · human | 448 | 2.7 | 1.8 |
| 2k+ | 500-word excerpt · human | 508 | 3.0 | 2.0 |
| 500-800 | 500-word excerpt · human | 265 | 2.6 | 1.5 |
| 800-1.2k | 500-word excerpt · human | 352 | 4.0 | 2.3 |

**By window.** Fire rate % at the 1% cut.

| Window | Arm | n | IdeaLens · outline (raw) | IdeaLens-ModernBERT-L · outline (raw) |
|---|---|---|---|---|
| full | full document · AI | 900 | 97.1 | 88.6 |
| w0 | 500-word excerpt · AI | 900 | 90.9 | 68.3 |
| w1 | 500-word excerpt · AI | 737 | 95.8 | 77.9 |
| full | full document · human | 857 | 3.5 | 2.3 |
| w0 | 500-word excerpt · human | 857 | 3.0 | 1.9 |
| w1 | 500-word excerpt · human | 716 | 3.1 | 2.0 |

**By format gate.** Fire rate % at the 1% cut.

| Format gate | Arm | n | IdeaLens · outline (raw) | IdeaLens-ModernBERT-L · outline (raw) |
|---|---|---|---|---|
| forced format | 500-word excerpt · AI | 191 | 91.6 | 64.4 |
| gated | 500-word excerpt · AI | 1,446 | 93.3 | 73.7 |
| forced format | 500-word excerpt · human | 160 | 4.4 | 1.9 |
| gated | 500-word excerpt · human | 1,413 | 2.9 | 1.9 |
