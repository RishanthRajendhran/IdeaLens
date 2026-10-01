### OpAI-Bench: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Every version keeps the seed author's ideas, so every flag is a false positive; there is no TPR or AUC.
- The v0-to-v8 trajectory is a separate figure. Formats for 37,119 documents come from the re-gated extract input (the label file carries none).

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v0: the human seed | human ideas (FPR) | 4,145 | 0.3 | 0.0 | 0.0 | 1.6 | 0.0 | 0.1 | 0.0 | 0.2 | 0.0 |
| v1 to v8: AI-edited versions · mean over 8 versions | human ideas, AI prose (FPR) | 33,163 | 0.4 | 0.0 | 12.1 | 1.6 | 0.0 | 4.0 | 0.9 | 0.0 | 16.2 |
| v1 to v8: AI-edited versions · median over 8 versions | human ideas, AI prose (FPR) |  | 0.4 | 0.0 | 10.1 | 1.6 | 0.0 | 3.0 | 0.3 | 0.0 | 4.7 |
| v1 to v8: AI-edited versions · min over 8 versions | human ideas, AI prose (FPR) |  | 0.2 (v1) | 0.0 (v1) | 0.0 (v1) | 1.2 (v2) | 0.0 (v1) | 0.0 (v2) | 0.0 (v2) | 0.0 (v4) | 0.0 (v1) |
| v1 to v8: AI-edited versions · max over 8 versions | human ideas, AI prose (FPR) |  | 0.6 (v5) | 0.0 (v5) | 26.3 (v6) | 2.0 (v6) | 0.1 (v8) | 11.3 (v6) | 3.7 (v6) | 0.2 (v1) | 48.5 (v8) |

**Length.** Share under 500 words: v0: the human seed 69.6%, v1 to v8: AI-edited versions 67.3%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v0: the human seed · < 500 | human ideas (FPR) | 2,883 | 0.4 | 0.0 | 0.0 | 1.8 | 0.0 | 0.1 | 0.0 | 0.3 | 0.0 |
| v0: the human seed · >= 500 | human ideas (FPR) | 1,262 | 0.2 | 0.0 | 0.0 | 1.1 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 |
| v1 to v8: AI-edited versions · < 500 | human ideas, AI prose (FPR) | 22,303 | 0.5 | 0.0 | 12.3 | 1.9 | 0.0 | 4.2 | 1.1 | 0.1 | 19.6 |
| v1 to v8: AI-edited versions · >= 500 | human ideas, AI prose (FPR) | 10,860 | 0.3 | 0.0 | 11.8 | 1.0 | 0.0 | 3.7 | 0.5 | 0.0 | 9.2 |

### OpAI-Bench: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| v0: the human seed | IdeaLens · outline | 0.0 | 0.1 | 0.8 | 3.5 |
| v0: the human seed | IdeaLens · document | 0.0 | 0.0 | 0.0 | 2.2 |
| v0: the human seed | ProseLens | 0.0 | 0.0 | 0.0 | 6.7 |
| v0: the human seed | IdeaLens-ModernBERT-L · outline | 0.1 | 0.7 | 3.7 | 14.7 |
| v0: the human seed | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 0.7 | 22.1 |
| v0: the human seed | ProseLens-ModernBERT-L | 0.0 | 0.0 | 0.7 | 12.4 |
| v0: the human seed | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 0.3 | 6.0 |
| v0: the human seed | Binoculars (cal.) | 0.0 | 0.3 | 2.9 | 9.6 |
| v1 to v8: AI-edited versions | IdeaLens · outline | 0.0 | 0.2 | 1.4 | 5.7 |
| v1 to v8: AI-edited versions | IdeaLens · document | 0.0 | 0.0 | 0.7 | 11.2 |
| v1 to v8: AI-edited versions | ProseLens | 1.7 | 6.5 | 25.7 | 58.0 |
| v1 to v8: AI-edited versions | IdeaLens-ModernBERT-L · outline | 0.1 | 0.8 | 4.4 | 16.1 |
| v1 to v8: AI-edited versions | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 1.2 | 27.0 |
| v1 to v8: AI-edited versions | ProseLens-ModernBERT-L | 0.1 | 1.3 | 13.2 | 43.4 |
| v1 to v8: AI-edited versions | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 8.7 | 34.1 |
| v1 to v8: AI-edited versions | Binoculars (cal.) | 0.0 | 0.0 | 1.2 | 4.4 |

**By version.** Fire rate % at the 1% cut.

| Version | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v1 | v1 to v8: AI-edited versions | 4,146 | 0.2 | 0.0 | 0.0 | 1.4 | 0.0 | 0.1 | 0.0 | 0.2 | 0.0 |
| v2 | v1 to v8: AI-edited versions | 4,145 | 0.3 | 0.0 | 0.0 | 1.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1 |
| v3 | v1 to v8: AI-edited versions | 4,146 | 0.2 | 0.0 | 3.1 | 1.4 | 0.0 | 0.7 | 0.0 | 0.1 | 1.3 |
| v4 | v1 to v8: AI-edited versions | 4,146 | 0.3 | 0.0 | 0.3 | 1.4 | 0.0 | 0.1 | 0.0 | 0.0 | 0.3 |
| v5 | v1 to v8: AI-edited versions | 4,144 | 0.6 | 0.0 | 17.0 | 1.7 | 0.0 | 5.3 | 0.5 | 0.0 | 8.2 |
| v6 | v1 to v8: AI-edited versions | 4,144 | 0.6 | 0.0 | 26.3 | 2.0 | 0.0 | 11.3 | 3.7 | 0.0 | 25.4 |
| v7 | v1 to v8: AI-edited versions | 4,146 | 0.6 | 0.0 | 24.2 | 1.9 | 0.0 | 6.9 | 0.8 | 0.0 | 45.8 |
| v8 | v1 to v8: AI-edited versions | 4,146 | 0.6 | 0.0 | 26.1 | 1.8 | 0.1 | 7.8 | 1.9 | 0.0 | 48.5 |

**By rewriting model.** Fire rate % at the 1% cut.

| Rewriting model | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gemini-2.5-flash | v1 to v8: AI-edited versions | 18,598 | 0.5 | 0.0 | 19.1 | 1.8 | 0.0 | 6.7 | 1.4 | 0.0 | 21.1 |
| gpt-5.4 | v1 to v8: AI-edited versions | 4,438 | 0.1 | 0.0 | 0.0 | 0.8 | 0.1 | 0.1 | 0.1 | 0.0 | 3.5 |
| gpt-5.4-nano | v1 to v8: AI-edited versions | 8,903 | 0.4 | 0.0 | 3.9 | 1.4 | 0.0 | 0.2 | 0.0 | 0.0 | 12.8 |
| qwen3-8b | v1 to v8: AI-edited versions | 1,224 | 1.6 | 0.3 | 10.7 | 3.7 | 0.4 | 5.0 | 1.2 | 0.5 | 11.5 |

**By genre.** Fire rate % at the 1% cut.

| Genre | Arm | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abstracts | v0: the human seed | 1,120 | 0.3 | 0.0 | 0.0 | 1.9 | 0.0 | 0.4 | 0.0 | 0.4 | 0.0 |
| essays | v0: the human seed | 942 | 1.1 | 0.0 | 0.0 | 4.4 | 0.0 | 0.2 | 0.0 | 0.4 | 0.0 |
| news | v0: the human seed | 864 | 0.0 | 0.0 | 0.0 | 0.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| reports | v0: the human seed | 1,219 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| abstracts | v1 to v8: AI-edited versions | 8,965 | 0.3 | 0.0 | 2.6 | 1.6 | 0.0 | 1.8 | 0.3 | 0.1 | 23.0 |
| essays | v1 to v8: AI-edited versions | 7,535 | 1.5 | 0.1 | 37.8 | 4.8 | 0.0 | 15.0 | 3.5 | 0.1 | 28.1 |
| news | v1 to v8: AI-edited versions | 6,911 | 0.0 | 0.0 | 13.0 | 0.2 | 0.0 | 0.3 | 0.0 | 0.0 | 7.7 |
| reports | v1 to v8: AI-edited versions | 9,752 | 0.0 | 0.0 | 0.4 | 0.1 | 0.1 | 0.3 | 0.0 | 0.0 | 6.7 |
