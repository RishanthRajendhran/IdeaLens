### Perkins et al.: main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Six evasion techniques applied to model-written samples (12 to 15 documents each). The clean AI (15) and human (10) rows are too small to read and are reported in the appendix only.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| adversarial (6 techniques) | model ideas (TPR) | 86 | 93.0 | 98.8 | 100.0 | 83.7 | 70.9 | 94.2 | 94.2 | 27.9 | 96.5 |

**Length.** Share under 500 words: adversarial (6 techniques) 61.6%.

| Arm · length | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| adversarial (6 techniques) · < 500 | model ideas (TPR) | 53 | 94.3 | 98.1 | 100.0 | 81.1 | 66.0 | 90.6 | 96.2 | 15.1 | 96.2 |
| adversarial (6 techniques) · >= 500 | model ideas (TPR) | 33 | 90.9 | 100.0 | 100.0 | 87.9 | 78.8 | 100.0 | 90.9 | 48.5 | 97.0 |

### Perkins et al.: appendix

**Rows reported in the appendix only.** Fire rate % at the 1% cut.

| Arm | Label | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ai (Bard, Claude, GPT-4) | model ideas (TPR) | 15 | 93.3 | 100.0 | 100.0 | 86.7 | 100.0 | 100.0 | 100.0 | 66.7 | 100.0 |
| human (faculty, students) | human ideas (FPR) | 10 | 40.0 | 20.0 | 30.0 | 50.0 | 20.0 | 20.0 | 10.0 | 0.0 | 20.0 |

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| adversarial (6 techniques) | IdeaLens · outline | 46.5 | 79.1 | 100.0 | 100.0 |
| adversarial (6 techniques) | IdeaLens · document | 29.1 | 82.6 | 100.0 | 100.0 |
| adversarial (6 techniques) | ProseLens | 90.7 | 100.0 | 100.0 | 100.0 |
| adversarial (6 techniques) | IdeaLens-ModernBERT-L · outline | 22.1 | 59.3 | 97.7 | 100.0 |
| adversarial (6 techniques) | IdeaLens-ModernBERT-L · document | 2.3 | 31.4 | 93.0 | 100.0 |
| adversarial (6 techniques) | ProseLens-ModernBERT-L | 46.5 | 89.5 | 95.3 | 96.5 |
| adversarial (6 techniques) | EditLens-Llama-3B (cal.) | 0.0 | 60.5 | 98.8 | 100.0 |
| adversarial (6 techniques) | Binoculars (cal.) | 16.3 | 30.2 | 52.3 | 66.3 |
| ai (Bard, Claude, GPT-4) | IdeaLens · outline | 46.7 | 80.0 | 100.0 | 100.0 |
| ai (Bard, Claude, GPT-4) | IdeaLens · document | 40.0 | 93.3 | 100.0 | 100.0 |
| ai (Bard, Claude, GPT-4) | ProseLens | 93.3 | 100.0 | 100.0 | 100.0 |
| ai (Bard, Claude, GPT-4) | IdeaLens-ModernBERT-L · outline | 33.3 | 73.3 | 100.0 | 100.0 |
| ai (Bard, Claude, GPT-4) | IdeaLens-ModernBERT-L · document | 0.0 | 60.0 | 100.0 | 100.0 |
| ai (Bard, Claude, GPT-4) | ProseLens-ModernBERT-L | 66.7 | 100.0 | 100.0 | 100.0 |
| ai (Bard, Claude, GPT-4) | EditLens-Llama-3B (cal.) | 0.0 | 93.3 | 100.0 | 100.0 |
| ai (Bard, Claude, GPT-4) | Binoculars (cal.) | 53.3 | 66.7 | 80.0 | 80.0 |
| human (faculty, students) | IdeaLens · outline | 10.0 | 30.0 | 50.0 | 80.0 |
| human (faculty, students) | IdeaLens · document | 0.0 | 0.0 | 30.0 | 80.0 |
| human (faculty, students) | ProseLens | 0.0 | 10.0 | 60.0 | 80.0 |
| human (faculty, students) | IdeaLens-ModernBERT-L · outline | 10.0 | 30.0 | 60.0 | 80.0 |
| human (faculty, students) | IdeaLens-ModernBERT-L · document | 0.0 | 0.0 | 30.0 | 90.0 |
| human (faculty, students) | ProseLens-ModernBERT-L | 0.0 | 20.0 | 40.0 | 90.0 |
| human (faculty, students) | EditLens-Llama-3B (cal.) | 0.0 | 10.0 | 20.0 | 40.0 |
| human (faculty, students) | Binoculars (cal.) | 0.0 | 0.0 | 10.0 | 40.0 |

**By arm.** Fire rate % at the 1% cut.

| Arm | Description | n | IdeaLens · outline | IdeaLens · document | ProseLens | IdeaLens-ModernBERT-L · outline | IdeaLens-ModernBERT-L · document | ProseLens-ModernBERT-L | EditLens-Llama-3B (cal.) | Binoculars (own) | Pangram 4 (own) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| adv_decrease_complexity | adversarial (6 techniques) | 15 | 93.3 | 100.0 | 100.0 | 73.3 | 73.3 | 93.3 | 100.0 | 40.0 | 100.0 |
| adv_increase_burstiness | adversarial (6 techniques) | 15 | 86.7 | 100.0 | 100.0 | 86.7 | 100.0 | 100.0 | 100.0 | 40.0 | 100.0 |
| adv_increase_complexity | adversarial (6 techniques) | 14 | 92.9 | 92.9 | 100.0 | 85.7 | 100.0 | 100.0 | 100.0 | 28.6 | 100.0 |
| adv_non_native_style | adversarial (6 techniques) | 15 | 93.3 | 100.0 | 100.0 | 93.3 | 40.0 | 80.0 | 93.3 | 6.7 | 100.0 |
| adv_paraphrase | adversarial (6 techniques) | 15 | 93.3 | 100.0 | 100.0 | 73.3 | 33.3 | 93.3 | 80.0 | 13.3 | 80.0 |
| adv_spelling_errors | adversarial (6 techniques) | 12 | 100.0 | 100.0 | 100.0 | 91.7 | 83.3 | 100.0 | 91.7 | 41.7 | 100.0 |
| ai_bard | ai (Bard, Claude, GPT-4) | 5 | 80.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| ai_claude | ai (Bard, Claude, GPT-4) | 5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0 | 100.0 |
| ai_gpt4 | ai (Bard, Claude, GPT-4) | 5 | 100.0 | 100.0 | 100.0 | 60.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| human_faculty | human (faculty, students) | 5 | 40.0 | 20.0 | 40.0 | 40.0 | 20.0 | 20.0 | 20.0 | 0.0 | 40.0 |
| human_student | human (faculty, students) | 5 | 40.0 | 20.0 | 20.0 | 60.0 | 20.0 | 20.0 | 0.0 | 0.0 | 0.0 |
