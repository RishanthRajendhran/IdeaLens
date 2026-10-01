### AI research ideas: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Every proposal, expert and model alike, was copy-edited by an LLM into the study's template (wording and formatting only, content preserved; Si et al., Appendix D), so the expert proposals are a person's ideas in model-polished prose and only the ideas separate the arms. Every paper was written by a researcher; only the seed idea's origin differs. Every review is an expert's.
- Papers are shown as a P(AI) gradation: papers from a model idea are mixed, human-leaning. Pangram 4 covers all three parts.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| proposals from model ideas (model_idea, model_idea_reranked) | model ideas (TPR) | 97 | 95.9 | 100.0 | 100.0 | 79.4 | 99.0 | 100.0 | 93.8 | 96.9 | 100.0 |
| proposals from expert ideas | human ideas, AI prose (FPR) | 48 | 10.4 | 12.5 | 14.6 | 14.6 | 16.7 | 18.8 | 25.0 | 8.3 | 12.5 |
| reviews (all) | human ideas (FPR) | 504 | 2.6 | 2.2 | 2.2 | 4.0 | 2.4 | 3.6 | 3.2 | 3.4 | 2.4 |
| AUC, proposals, model vs expert ideas | | | 0.990 | 0.998 | 0.984 | 0.912 | 0.985 | 0.959 | 0.890 | 0.976 | 0.967 |
| AUC, papers, model-seed vs expert-seed | | | 0.704 | 0.605 | 0.561 | 0.684 | 0.583 | 0.516 | 0.568 | 0.594 | 0.599 |

**Length.** Share under 500 words: proposals from model ideas (model_idea, model_idea_reranked) 0.0%, proposals from expert ideas 2.1%, reviews (all) 94.4%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| proposals from model ideas (model_idea, model_idea_reranked) · >= 500 | model ideas (TPR) | 97 | 95.9 | 100.0 | 100.0 | 79.4 | 99.0 | 100.0 | 93.8 | 96.9 | 100.0 |
| proposals from expert ideas · < 500 | human ideas, AI prose (FPR) | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 | 0.0 | 0.0 |
| proposals from expert ideas · >= 500 | human ideas, AI prose (FPR) | 47 | 10.6 | 12.8 | 14.9 | 14.9 | 17.0 | 19.1 | 23.4 | 8.5 | 12.8 |
| reviews (all) · < 500 | human ideas (FPR) | 476 | 2.7 | 2.3 | 2.3 | 4.2 | 2.3 | 3.6 | 3.4 | 3.6 | 2.3 |
| reviews (all) · >= 500 | human ideas (FPR) | 28 | 0.0 | 0.0 | 0.0 | 0.0 | 3.6 | 3.6 | 0.0 | 0.0 | 3.6 |

**Shared P(AI) table, AI research ideas rows.** P(AI) % (1 - P(human); Pangram: its derived P(AI)); the statistic is named per row where a level shows more than the mean.

| Level | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| proposals from model ideas · mean | model ideas, AI prose | 97 | 97.4 | 99.7 | 99.9 | 93.6 | 99.7 | 99.9 | – | – | 99.7 |
| proposals from model ideas · median | model ideas, AI prose | 97 | 98.8 | 99.7 | 99.9 | 98.1 | 99.8 | 100.0 | – | – | 100.0 |
| papers from a model idea · mean | mixed, human-leaning | 24 | 48.7 | 59.1 | 16.4 | 49.3 | 54.1 | 40.0 | – | – | 30.4 |
| papers from a model idea · median | mixed, human-leaning | 24 | 49.7 | 75.3 | 0.2 | 43.7 | 57.3 | 1.8 | – | – | 26.3 |
| papers from a model idea · min | mixed, human-leaning | 24 | 0.0 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | – | – | 0.0 |
| papers from a model idea · max | mixed, human-leaning | 24 | 99.7 | 98.9 | 84.6 | 99.8 | 99.7 | 99.8 | – | – | 87.0 |
| proposals from expert ideas · mean | human ideas, AI prose | 48 | 29.6 | 30.7 | 15.7 | 37.0 | 33.8 | 26.1 | – | – | 18.4 |
| proposals from expert ideas · median | human ideas, AI prose | 48 | 15.0 | 14.8 | 0.3 | 17.9 | 16.9 | 3.6 | – | – | 6.9 |
| papers from an expert idea · mean | human ideas, human prose | 19 | 22.7 | 53.2 | 10.6 | 26.6 | 43.2 | 32.2 | – | – | 23.7 |
| papers from an expert idea · median | human ideas, human prose | 19 | 8.9 | 55.7 | 0.0 | 2.8 | 22.6 | 1.8 | – | – | 24.5 |
| reviews · mean | human ideas | 504 | 28.5 | 19.6 | 4.3 | 40.3 | 19.9 | 7.5 | – | – | 2.7 |
| reviews · median | human ideas | 504 | 20.8 | 13.7 | 0.5 | 34.3 | 10.2 | 0.2 | – | – | 0.0 |

### AI research ideas: appendix

**Rows reported in the appendix only.** Fire rate % at the 1% cut.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| papers from an expert idea | human ideas (FPR) | 19 | 5.3 | 10.5 | 10.5 | 10.5 | 15.8 | 31.6 | 0.0 | 0.0 | 5.3 |
| papers from a model idea | mixed, human-leaning (fire rate) | 24 | 29.2 | 25.0 | 20.8 | 33.3 | 29.2 | 37.5 | 0.0 | 0.0 | 8.3 |

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| proposals from model ideas (model_idea, model_idea_reranked) | IdeaLens · outline | 68.0 | 93.8 | 100.0 | 100.0 |
| proposals from model ideas (model_idea, model_idea_reranked) | IdeaLens · document | 100.0 | 100.0 | 100.0 | 100.0 |
| proposals from model ideas (model_idea, model_idea_reranked) | ProseLens | 100.0 | 100.0 | 100.0 | 100.0 |
| proposals from model ideas (model_idea, model_idea_reranked) | IdeaLens-ModernBERT-L · outline | 12.4 | 54.6 | 92.8 | 96.9 |
| proposals from model ideas (model_idea, model_idea_reranked) | IdeaLens-ModernBERT-L · document | 94.8 | 95.9 | 100.0 | 100.0 |
| proposals from model ideas (model_idea, model_idea_reranked) | ProseLens-ModernBERT-L | 97.9 | 100.0 | 100.0 | 100.0 |
| proposals from model ideas (model_idea, model_idea_reranked) | EditLens-Llama-3B (cal.) | 0.0 | 33.0 | 100.0 | 100.0 |
| proposals from model ideas (model_idea, model_idea_reranked) | Binoculars (cal.) | 20.6 | 96.9 | 100.0 | 100.0 |
| proposals from expert ideas | IdeaLens · outline | 0.0 | 8.3 | 18.8 | 37.5 |
| proposals from expert ideas | IdeaLens · document | 4.2 | 6.2 | 27.1 | 62.5 |
| proposals from expert ideas | ProseLens | 10.4 | 14.6 | 25.0 | 66.7 |
| proposals from expert ideas | IdeaLens-ModernBERT-L · outline | 2.1 | 6.2 | 16.7 | 39.6 |
| proposals from expert ideas | IdeaLens-ModernBERT-L · document | 6.2 | 12.5 | 25.0 | 79.2 |
| proposals from expert ideas | ProseLens-ModernBERT-L | 6.2 | 12.5 | 33.3 | 64.6 |
| proposals from expert ideas | EditLens-Llama-3B (cal.) | 0.0 | 6.2 | 58.3 | 100.0 |
| proposals from expert ideas | Binoculars (cal.) | 2.1 | 10.4 | 20.8 | 33.3 |
| reviews (all) | IdeaLens · outline | 0.0 | 2.2 | 8.7 | 38.7 |
| reviews (all) | IdeaLens · document | 0.4 | 2.0 | 5.8 | 77.6 |
| reviews (all) | ProseLens | 2.2 | 2.2 | 10.1 | 71.6 |
| reviews (all) | IdeaLens-ModernBERT-L · outline | 0.2 | 2.4 | 11.7 | 49.2 |
| reviews (all) | IdeaLens-ModernBERT-L · document | 0.6 | 2.4 | 7.3 | 82.9 |
| reviews (all) | ProseLens-ModernBERT-L | 2.0 | 2.2 | 12.5 | 50.4 |
| reviews (all) | EditLens-Llama-3B (cal.) | 0.0 | 2.2 | 12.3 | 35.1 |
| reviews (all) | Binoculars (cal.) | 1.8 | 3.4 | 14.9 | 25.2 |
| papers from an expert idea | IdeaLens · outline | 5.3 | 5.3 | 10.5 | 26.3 |
| papers from an expert idea | IdeaLens · document | 0.0 | 5.3 | 52.6 | 78.9 |
| papers from an expert idea | ProseLens | 0.0 | 10.5 | 21.1 | 36.8 |
| papers from an expert idea | IdeaLens-ModernBERT-L · outline | 5.3 | 10.5 | 15.8 | 26.3 |
| papers from an expert idea | IdeaLens-ModernBERT-L · document | 5.3 | 10.5 | 42.1 | 73.7 |
| papers from an expert idea | ProseLens-ModernBERT-L | 15.8 | 26.3 | 31.6 | 57.9 |
| papers from an expert idea | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 15.8 | 47.4 |
| papers from an expert idea | Binoculars (cal.) | 0.0 | 0.0 | 5.3 | 5.3 |
| papers from a model idea | IdeaLens · outline | 8.3 | 20.8 | 41.7 | 58.3 |
| papers from a model idea | IdeaLens · document | 0.0 | 16.7 | 58.3 | 91.7 |
| papers from a model idea | ProseLens | 0.0 | 12.5 | 33.3 | 50.0 |
| papers from a model idea | IdeaLens-ModernBERT-L · outline | 4.2 | 20.8 | 37.5 | 50.0 |
| papers from a model idea | IdeaLens-ModernBERT-L · document | 8.3 | 20.8 | 50.0 | 75.0 |
| papers from a model idea | ProseLens-ModernBERT-L | 12.5 | 29.2 | 41.7 | 54.2 |
| papers from a model idea | EditLens-Llama-3B (cal.) | 0.0 | 0.0 | 12.5 | 54.2 |
| papers from a model idea | Binoculars (cal.) | 0.0 | 0.0 | 4.2 | 12.5 |

**By arm.** Fire rate % at the 1% cut.

| Arm | Description | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| model_idea | proposals from model ideas (model_idea, model_idea_reranked) | 49 | 98.0 | 100.0 | 100.0 | 77.6 | 98.0 | 100.0 | 95.9 | 98.0 | 100.0 |
| model_idea_reranked | proposals from model ideas (model_idea, model_idea_reranked) | 48 | 93.8 | 100.0 | 100.0 | 81.2 | 100.0 | 100.0 | 91.7 | 95.8 | 100.0 |
| expert_idea | proposals from expert ideas | 48 | 10.4 | 12.5 | 14.6 | 14.6 | 16.7 | 18.8 | 25.0 | 8.3 | 12.5 |
| execution_review_of_ai | reviews (all) | 93 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| execution_review_of_human | reviews (all) | 84 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.2 | 0.0 | 1.2 | 0.0 |
| ideation_review_of_ai | reviews (all) | 102 | 3.9 | 3.9 | 3.9 | 7.8 | 4.9 | 5.9 | 4.9 | 3.9 | 5.9 |
| ideation_review_of_ai_rerank | reviews (all) | 108 | 3.7 | 3.7 | 3.7 | 7.4 | 3.7 | 5.6 | 6.5 | 4.6 | 3.7 |
| ideation_review_of_human | reviews (all) | 117 | 4.3 | 2.6 | 2.6 | 3.4 | 2.6 | 4.3 | 3.4 | 6.0 | 1.7 |
| paper_from_expert_idea | papers from an expert idea | 19 | 5.3 | 10.5 | 10.5 | 10.5 | 15.8 | 31.6 | 0.0 | 0.0 | 5.3 |
| paper_from_model_idea | papers from a model idea | 24 | 29.2 | 25.0 | 20.8 | 33.3 | 29.2 | 37.5 | 0.0 | 0.0 | 8.3 |
