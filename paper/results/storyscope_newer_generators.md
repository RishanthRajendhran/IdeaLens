### StoryScope, unseen generators: main table

Fire rate % at the 1% cut (global / per-format). TPR on model-idea rows, FPR on human-idea rows.

- Every document is Creative Writing; the per-format cut is the Creative Writing cut.
- Same 250 StoryScope prompts (seeded 18% sample) for every generator, prompt sent as-is with no length control, as for the five StoryScope generators. Claude Fable 5.1 and Opus 5 were generated with no system prompt and no tools. Outputs that are not stories are dropped: Fable 6 of 250 (3 refusals, 2 safety-classifier cuts, 1 tool-call leak on both tries), Opus 5 of 250 (1 refusal, 4 classifier cuts), gpt-5.6-sol 4 of 250 (refusals).
- The matched human stories are StoryScope's human row (storyscope.md) and are not repeated here.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5.6-sol (unseen) | model ideas (TPR) | 246 | 78.5 / 90.7 | 98.8 / 100.0 | 98.8 / 99.6 | 48.8 / 59.8 | 43.9 / 77.2 | 100.0 / 100.0 | 1.2 / 81.7 | 0.0 / – | 100.0 |
| gpt-6-astra (unseen) | model ideas (TPR) | 250 | 62.8 / 74.8 | 91.6 / 99.2 | 83.2 / 96.4 | 30.4 / 44.0 | 27.2 / 69.2 | 97.6 / 100.0 | 0.0 / 67.6 | 0.0 / – | 100.0 |
| claude-fable-5-1 (unseen) | model ideas (TPR) | 244 | 51.2 / 65.6 | 27.9 / 79.1 | 17.2 / 35.2 | 22.1 / 32.4 | 16.4 / 49.2 | 46.3 / 77.5 | 0.0 / 7.4 | 0.0 / – | 99.2 |
| claude-opus-5 (unseen) | model ideas (TPR) | 245 | 51.0 / 65.7 | 49.4 / 84.9 | 41.2 / 64.1 | 20.4 / 33.9 | 22.9 / 55.1 | 76.7 / 90.6 | 0.0 / 24.9 | 0.0 / – | 99.2 |

**Length.** Share under 500 words: gpt-5.6-sol (unseen) 0.0%, gpt-6-astra (unseen) 0.0%, claude-fable-5-1 (unseen) 0.0%, claude-opus-5 (unseen) 0.0%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5.6-sol (unseen) · >= 500 | model ideas (TPR) | 246 | 78.5 / 90.7 | 98.8 / 100.0 | 98.8 / 99.6 | 48.8 / 59.8 | 43.9 / 77.2 | 100.0 / 100.0 | 1.2 / 81.7 | 0.0 / – | 100.0 |
| gpt-6-astra (unseen) · >= 500 | model ideas (TPR) | 250 | 62.8 / 74.8 | 91.6 / 99.2 | 83.2 / 96.4 | 30.4 / 44.0 | 27.2 / 69.2 | 97.6 / 100.0 | 0.0 / 67.6 | 0.0 / – | 100.0 |
| claude-fable-5-1 (unseen) · >= 500 | model ideas (TPR) | 244 | 51.2 / 65.6 | 27.9 / 79.1 | 17.2 / 35.2 | 22.1 / 32.4 | 16.4 / 49.2 | 46.3 / 77.5 | 0.0 / 7.4 | 0.0 / – | 99.2 |
| claude-opus-5 (unseen) · >= 500 | model ideas (TPR) | 245 | 51.0 / 65.7 | 49.4 / 84.9 | 41.2 / 64.1 | 20.4 / 33.9 | 22.9 / 55.1 | 76.7 / 90.6 | 0.0 / 24.9 | 0.0 / – | 99.2 |

### StoryScope, unseen generators: appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global / per-format).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| gpt-5.6-sol (unseen) | IdeaLens · outline | 65.9 / – | 75.6 / 83.3 | 87.8 / 93.5 | 94.3 / 96.3 |
| gpt-5.6-sol (unseen) | IdeaLens · document | 93.1 / – | 97.2 / 100.0 | 99.6 / 100.0 | 100.0 / 100.0 |
| gpt-5.6-sol (unseen) | ProseLens | 95.5 / – | 97.2 / 99.6 | 99.6 / 99.6 | 99.6 / 99.6 |
| gpt-5.6-sol (unseen) | IdeaLens-ModernBERT-L · outline | 28.9 / – | 39.4 / 50.8 | 59.8 / 69.9 | 76.0 / 79.3 |
| gpt-5.6-sol (unseen) | IdeaLens-ModernBERT-L · document | 32.9 / – | 37.0 / 74.0 | 58.5 / 82.9 | 78.9 / 88.6 |
| gpt-5.6-sol (unseen) | ProseLens-ModernBERT-L | 96.3 / – | 98.8 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 |
| gpt-5.6-sol (unseen) | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 28.5 | 32.9 / 99.2 | 99.6 / 100.0 |
| gpt-5.6-sol (unseen) | Binoculars (cal.) | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 |
| gpt-6-astra (unseen) | IdeaLens · outline | 42.8 / – | 57.2 / 68.4 | 71.6 / 80.0 | 83.6 / 86.4 |
| gpt-6-astra (unseen) | IdeaLens · document | 81.2 / – | 88.0 / 98.8 | 97.2 / 100.0 | 100.0 / 100.0 |
| gpt-6-astra (unseen) | ProseLens | 66.8 / – | 78.4 / 95.2 | 92.4 / 96.8 | 96.8 / 97.6 |
| gpt-6-astra (unseen) | IdeaLens-ModernBERT-L · outline | 12.0 / – | 24.0 / 32.0 | 44.0 / 52.0 | 60.4 / 65.2 |
| gpt-6-astra (unseen) | IdeaLens-ModernBERT-L · document | 19.6 / – | 24.0 / 60.8 | 40.4 / 72.4 | 70.4 / 79.6 |
| gpt-6-astra (unseen) | ProseLens-ModernBERT-L | 89.6 / – | 95.6 / 99.6 | 99.6 / 100.0 | 100.0 / 100.0 |
| gpt-6-astra (unseen) | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 18.8 | 24.0 / 97.6 | 98.4 / 100.0 |
| gpt-6-astra (unseen) | Binoculars (cal.) | 0.0 / – | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 |
| claude-fable-5-1 (unseen) | IdeaLens · outline | 30.3 / – | 41.8 / 59.0 | 62.7 / 70.9 | 74.2 / 76.6 |
| claude-fable-5-1 (unseen) | IdeaLens · document | 17.2 / – | 20.1 / 71.7 | 54.9 / 86.1 | 87.3 / 92.6 |
| claude-fable-5-1 (unseen) | ProseLens | 8.2 / – | 11.5 / 29.9 | 23.8 / 40.2 | 40.2 / 46.3 |
| claude-fable-5-1 (unseen) | IdeaLens-ModernBERT-L · outline | 10.7 / – | 19.3 / 23.8 | 32.0 / 41.4 | 51.2 / 57.0 |
| claude-fable-5-1 (unseen) | IdeaLens-ModernBERT-L · document | 12.3 / – | 14.8 / 43.4 | 26.2 / 58.6 | 53.7 / 68.4 |
| claude-fable-5-1 (unseen) | ProseLens-ModernBERT-L | 20.9 / – | 38.1 / 68.0 | 61.1 / 80.7 | 79.9 / 84.4 |
| claude-fable-5-1 (unseen) | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 2.0 | 2.9 / 31.1 | 58.2 / 86.9 |
| claude-fable-5-1 (unseen) | Binoculars (cal.) | 0.0 / – | 0.0 / 0.0 | 8.2 / 10.7 | 23.8 / 27.0 |
| claude-opus-5 (unseen) | IdeaLens · outline | 28.2 / – | 43.7 / 58.8 | 63.3 / 71.8 | 75.5 / 79.6 |
| claude-opus-5 (unseen) | IdeaLens · document | 29.0 / – | 39.6 / 82.0 | 72.2 / 90.6 | 90.6 / 93.5 |
| claude-opus-5 (unseen) | ProseLens | 23.3 / – | 31.8 / 61.2 | 52.7 / 71.0 | 71.0 / 75.1 |
| claude-opus-5 (unseen) | IdeaLens-ModernBERT-L · outline | 9.0 / – | 14.3 / 22.0 | 33.1 / 39.6 | 50.2 / 54.3 |
| claude-opus-5 (unseen) | IdeaLens-ModernBERT-L · document | 13.1 / – | 15.9 / 48.2 | 33.5 / 62.4 | 59.2 / 68.2 |
| claude-opus-5 (unseen) | ProseLens-ModernBERT-L | 58.0 / – | 71.8 / 89.0 | 86.5 / 92.7 | 91.0 / 95.5 |
| claude-opus-5 (unseen) | EditLens-Llama-3B (cal.) | 0.0 / – | 0.0 / 5.3 | 6.1 / 66.1 | 84.5 / 95.9 |
| claude-opus-5 (unseen) | Binoculars (cal.) | 0.0 / – | 0.0 / 0.4 | 7.8 / 13.1 | 46.5 / 51.8 |
