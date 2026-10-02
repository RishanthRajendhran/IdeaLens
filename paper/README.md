# IdeaLens: the paper's results, prompts and code

This folder holds what the paper's appendix points to: every evaluation's full result tables, the prompts and role
vocabularies, and the code that produced the numbers. The trained models are on Hugging Face (starting from
[IdeaLens](https://huggingface.co/rishanthrajendhran/IdeaLens) and [ProseLens](https://huggingface.co/rishanthrajendhran/ProseLens)), as are the training corpus
[WildOutlines](https://huggingface.co/datasets/rishanthrajendhran/WildOutlines) and the evaluation sets we constructed ([IdeaShift](https://huggingface.co/datasets/rishanthrajendhran/IdeaShift),
[IdeaShift-X](https://huggingface.co/datasets/rishanthrajendhran/IdeaShift-X), [TwiceTold](https://huggingface.co/datasets/rishanthrajendhran/TwiceTold)); the
[IdeaLens collection](https://huggingface.co/collections/rishanthrajendhran/idealens-6abee785ce6196fc0be9200f) gathers them all, and the
demo (link: TBD) runs IdeaLens and ProseLens in the browser. To run the detectors on new documents, use the
`idealens` package at the root of this repository.

## Layout

| Folder | Contents | Appendix |
|---|---|---|
| `results/<evaluation>.md` | One file per evaluation: every arm for our detectors (IdeaLens, ProseLens and their ModernBERT variants), EditLens-3B, Binoculars and Pangram 4; other operating points (0.1, 0.5, 2 and 5% false-positive targets), the < 500 / ≥ 500 word splits, per-arm breakdowns and the mean P(AI) of mixed-provenance arms | G, H, I |
| `results/in_domain_test.md` | The held-out test split of the training corpus | E, G |
| `results/paraphrase_probe_similarity.md` | How much of the raw outline and the source document the paraphrased outline keeps | D.4 |
| `results/input_representation.md` | What the outline carries: content only, shuffled items, roles only, items scored alone | I.4 |
| `results/feature_bank.csv` | The 79 consolidated item-level features: name, gloss, proposed and observed direction, fire rate, score and 95% interval | J |
| `results/feature_analysis/` | The feature analysis behind it: the 79-feature bank with each feature's definition and operationalization (`feature_bank.json`), the nine discovery groups' raw proposals, the Gemini 3.8 Flash and GPT-5.6 Luna ratings of the 13,616 held-out items with the items' ids, formats, roles and P(human) (their text is withheld), and the agreement and firing analyses | J |
| `results/all_detectors_global_1pct.csv` | Every arm of every evaluation against every detector at the global 1% cut: IdeaLens on the outline and on the document, ProseLens, the ModernBERT, Qwen and logistic-regression variants, Pangram 4 and the open baselines | G |
| `results/per_format_1pct.csv` | The global and per-format 1% cut for IdeaLens, ProseLens and EditLens-3B on every arm of the quadrant tables (the values after the slash in Appendix G) | E.2, G |
| `results/twicetold.md` | TwiceTold: the rewrites and the model originals, and the length and overlap correlations | H.2 |
| `results/ideashift_*.md`, `results/ideashift_x.md`, `results/translation.md` | IdeaShift (human and AI sources, source overlap), IdeaShift-X, translation into English | H.1, H.3, H.4 |
| `results/c4_2019.md`, `results/robustness_*.md`, `results/attack_content_preservation_*.md`, `results/extraction_variance_*.md`, `results/storyscope_newer_generators.md` | Pre-ChatGPT web text, content-preserving transformations, attacks, repeated extraction, newer generators | I |
| `results/excluded_*.md` | PeerPrism and the personal-style post-editing set, left out of the paper for data-quality problems | C |
| `results/csv/` | Every markdown table as CSV, named `<file>__table<k>.csv` | |
| `prompts/format_classification/` | The format taxonomy the format gate chooses from (from WebOrganizer; the gate prompt itself is in `code/src/ideadet/pipeline/format_classify.py`) | D, K |
| `prompts/role_discovery/` | Base role proposal, outline extraction, role assignment and consolidation, with their output schemas | D.1, K |
| `prompts/role_vocabularies/` | The final role vocabulary of each format: definitions, assignment tests, the roles each is distinguished from | D.1 |
| `prompts/extraction/` | The labelled outline extraction prompt (`labeled_outline_extraction_en.txt`; `labeled_outline_extraction.txt` is the same prompt without its English-output section), its output schema, and the six exemplars per format with their reference outlines (`fewshot/n6_exemplars.json`) | D.2, K |
| `prompts/deleak/` | The outline paraphrase prompt (`canonical_paraphrasing_v1.txt`) | D.4, K |
| `prompts/training/` | Classifier chat template, the system prompts of IdeaLens (`system_full.txt`) and ProseLens (`system_docs.txt`), label tokens and maximum lengths (`contract.json`) | E.1, K |
| `prompts/eval_generation/` | IdeaShift briefs (`test3_ladder.*`), generation (`test3_ladder_generate.txt`, the system prompt; the user message is the brief) and level 5 (`test2_generate.*`); IdeaShift-X briefs and level 5 (`multiling_ladder_brief.*`, `multiling_rung5_generate.*`); translation (`multiling_translate.*`); source paraphrase (`test1_paraphrase.*`); TwiceTold's model stories and writer instructions (`twicetold_*.txt`) | H, I.4, K |
| `prompts/feature_discovery/` | Item-level feature discovery and consolidation prompts and schemas | J |
| `code/` | The `ideadet` package, configs and scripts: pipeline, training, scoring, calibration, evaluation construction, feature analysis. See `code/README.md` and `code/docs/` | D, E |

## Evaluation configs and the paper's names

The code keeps its original evaluation ids (`code/configs/evals/`):

| Config | Paper |
|---|---|
| `indomain` | In-domain test split |
| `test0_deleak_invariance`, `test1_source_paraphrase`, `test4_extractor_sensitivity`, `test14_partial_documents` | Content-preserving transformations: raw vs paraphrased outline, source paraphrased before extraction, a different extractor, 500-word excerpts |
| `test3_collaboration_ladder` | IdeaShift |
| `test9_multilingual` | The nine-language predecessor of IdeaShift-X (the reported 24-language set was built with the earlier codebase) |
| `test33_ai_ideated_prose` | TwiceTold |
| `test34_storyscope_new_generators` | StoryScope, newer generators |
| `test5_peer_review`, `test6_ai_peer_review` | AI Peer Review Detection; AI in Peer Review (Saha et al.) |
| `test7_detectrl`, `test24_detectrl_attacks` | DetectRL-X and its attack sweep |
| `test8_storyscope` | StoryScope |
| `test10_detectionai` ... `test25_ellipse` | DetectionAI, OpAI-Bench, Sem-Detect, MELD, personal-style post-edit, LAMP, ARB, GEDE, Perkins et al., HART, Epoch author imitation, CoCoNUTS, PeerPrism, ELLIPSE |
| `test26_research_ideas_ideation`, `test27_research_ideas_execution`, `test28_research_ideas_reviews` | AI-Researcher: proposals, papers, expert reviews |

## Conventions

- Detectors: IdeaLens is trained on paraphrased outlines and reads either the outline or the raw document; ProseLens is the same model trained on and reading raw documents. `-ModernBERT`, `-Qwen3.5-9B` and `-LogisticClassifier` are the other backbones trained on the same corpus (WildOutlines, about 1M documents).
- Rates are percentages. On model-ideas arms the rate is the true-positive rate; on human-ideas arms it is the false-positive rate.
- `n` is the number of documents in an arm. Where a detector scored fewer (for example a document the extractor failed on), the paper's quadrant tables give that detector's count.
- In `all_detectors_global_1pct.csv`, the newer-generators rows carry our detectors and Pangram 4 only (EditLens-3B and Binoculars for them are in `storyscope_newer_generators.md`), and the TwiceTold rows leave blank the outline readers other than IdeaLens, whose outlines differ between runs.
- Our detectors use the cut fitted for a 1% false-positive rate on 80,000 human calibration documents (global cut); a per-format cut, where shown, follows a slash. Baselines use their published thresholds unless marked "cal." (cut calibrated on the same human documents). Pangram 4 counts a text as AI when its AI fraction plus half its AI-assisted fraction is at least 0.5.
- Mixed-provenance arms have no correct binary answer and are reported as P(AI) distributions.
- Outlines are "paraphrased" (as in training) or "raw" (as extracted, as at inference).
- Study participants who wrote rewrites are identified only by codes W01, W02, ...
- The six extraction exemplars per format and the example excerpts in the role vocabularies quote training-corpus documents (WildOutlines). No text from any evaluation benchmark or from the evaluation sets we constructed is included here; the constructed sets are on Hugging Face.
- Absolute paths in `code/` are written as `${REPO_DIR}` (this code), `${WORK_DIR}` (data and outputs), `${AUX_DIR}` (an earlier codebase some evaluation builders import helpers from, not included), `${PROJECT_ROOT}` and `${HF_HOME}`. They are not read from environment variables: replace them with your own paths. Provider keys are read from the environment (`code/docs/RUNNING.md`).
- IdeaShift-X, Academic Integrity and GEN were built with that earlier codebase; their results are in `results/` and the IdeaShift-X construction prompts in `prompts/evaluation_construction/`.
