### Held-out test split (1M corpus): main table

Fire rate % at the 1% cut (global). TPR on model-idea rows, FPR on human-idea rows.

- Silver labels: the corpus labels agree with Pangram on 100.00% of rows, so Pangram (and the baselines) are not reported here. Our outline-trained models on the paraphrased outline.
- The global cut is fitted for 1% FPR on the 80,000 calibration humans; on this split's humans it realises 2.6% for IdeaLens and 2.0% for IdeaLens-ModernBERT-L, almost all from Knowledge Article and Nonfiction Writing (2026-crawled pages; see the crawl-year note). The FPR column is the realised rate; the per-format rows show which formats do well at the same cut.
- Every document is 501 words or more (median 1,372).
| Arm | Label | n | IdeaLens · outline (paraphrased) | IdeaLens-ModernBERT-L · outline (paraphrased) |
|---|---|---|---|---|
| AI | AI (TPR) | 24,295 | 95.8 | 86.9 |
| human | human (FPR, realised) | 24,574 | 2.6 | 2.0 |
| Personal Blog · AI | AI (TPR) | 3,181 | 97.5 | 91.9 |
| Personal Blog · human | human (FPR, realised) | 3,155 | 1.4 | 1.1 |
| Creative Writing · AI | AI (TPR) | 3,192 | 95.5 | 86.4 |
| Creative Writing · human | human (FPR, realised) | 3,132 | 0.3 | 0.4 |
| User Reviews · AI | AI (TPR) | 3,148 | 98.0 | 94.3 |
| User Reviews · human | human (FPR, realised) | 3,151 | 0.6 | 0.6 |
| Nonfiction Writing · AI | AI (TPR) | 3,132 | 94.5 | 83.7 |
| Nonfiction Writing · human | human (FPR, realised) | 3,132 | 6.8 | 5.7 |
| Academic Writing · AI | AI (TPR) | 3,132 | 98.2 | 93.9 |
| Academic Writing · human | human (FPR, realised) | 3,132 | 0.7 | 0.8 |
| Knowledge Article · AI | AI (TPR) | 3,132 | 93.7 | 73.9 |
| Knowledge Article · human | human (FPR, realised) | 3,132 | 7.7 | 5.3 |
| Personal About Page · AI | AI (TPR) | 2,863 | 93.7 | 82.3 |
| Personal About Page · human | human (FPR, realised) | 3,103 | 1.0 | 0.7 |
| News Article · AI | AI (TPR) | 2,515 | 95.2 | 88.7 |
| News Article · human | human (FPR, realised) | 2,637 | 1.7 | 1.3 |
| AUC, AI vs human | | | 0.995 | 0.990 |

**Length.** Share under 500 words: AI 0.0%, human 0.0%.

| Arm · length | Label | n | IdeaLens · outline (paraphrased) | IdeaLens-ModernBERT-L · outline (paraphrased) |
|---|---|---|---|---|
| AI · >= 500 | AI (TPR) | 24,295 | 95.8 | 86.9 |
| human · >= 500 | human (FPR, realised) | 24,574 | 2.6 | 2.0 |

### Held-out test split (1M corpus): appendix

**Other cuts.** Fire rate % at 0.1%, 0.5%, 2%, 5% (global).

| Arm | Model | 0.1% | 0.5% | 2% | 5% |
|---|---|---|---|---|---|
| AI | IdeaLens · outline (paraphrased) | 79.7 | 93.3 | 97.8 | 99.1 |
| AI | IdeaLens-ModernBERT-L · outline (paraphrased) | 52.9 | 77.7 | 93.8 | 97.7 |
| human | IdeaLens · outline (paraphrased) | 0.6 | 2.0 | 3.7 | 5.5 |
| human | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.2 | 1.1 | 3.6 | 7.2 |
| Personal Blog · AI | IdeaLens · outline (paraphrased) | 91.2 | 96.5 | 98.6 | 99.4 |
| Personal Blog · AI | IdeaLens-ModernBERT-L · outline (paraphrased) | 75.3 | 88.6 | 95.5 | 98.3 |
| Personal Blog · human | IdeaLens · outline (paraphrased) | 0.7 | 1.0 | 2.3 | 3.6 |
| Personal Blog · human | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.6 | 0.8 | 1.9 | 4.8 |
| Creative Writing · AI | IdeaLens · outline (paraphrased) | 88.8 | 94.0 | 96.9 | 98.3 |
| Creative Writing · AI | IdeaLens-ModernBERT-L · outline (paraphrased) | 72.0 | 82.7 | 91.3 | 95.8 |
| Creative Writing · human | IdeaLens · outline (paraphrased) | 0.0 | 0.2 | 0.8 | 1.6 |
| Creative Writing · human | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.1 | 0.3 | 1.0 | 3.9 |
| User Reviews · AI | IdeaLens · outline (paraphrased) | 94.2 | 97.4 | 98.7 | 99.3 |
| User Reviews · AI | IdeaLens-ModernBERT-L · outline (paraphrased) | 81.8 | 91.4 | 96.8 | 98.6 |
| User Reviews · human | IdeaLens · outline (paraphrased) | 0.3 | 0.5 | 1.0 | 1.9 |
| User Reviews · human | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.3 | 0.6 | 1.1 | 3.1 |
| Nonfiction Writing · AI | IdeaLens · outline (paraphrased) | 63.2 | 90.1 | 97.7 | 99.3 |
| Nonfiction Writing · AI | IdeaLens-ModernBERT-L · outline (paraphrased) | 17.0 | 64.6 | 93.8 | 98.4 |
| Nonfiction Writing · human | IdeaLens · outline (paraphrased) | 1.5 | 5.6 | 9.1 | 12.2 |
| Nonfiction Writing · human | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.1 | 3.4 | 8.8 | 13.6 |
| Academic Writing · AI | IdeaLens · outline (paraphrased) | 92.8 | 97.4 | 98.8 | 99.4 |
| Academic Writing · AI | IdeaLens-ModernBERT-L · outline (paraphrased) | 76.0 | 90.3 | 96.9 | 98.8 |
| Academic Writing · human | IdeaLens · outline (paraphrased) | 0.3 | 0.6 | 1.1 | 2.2 |
| Academic Writing · human | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.2 | 0.5 | 1.4 | 3.9 |
| Knowledge Article · AI | IdeaLens · outline (paraphrased) | 51.7 | 86.7 | 97.8 | 99.3 |
| Knowledge Article · AI | IdeaLens-ModernBERT-L · outline (paraphrased) | 7.3 | 49.2 | 91.5 | 97.9 |
| Knowledge Article · human | IdeaLens · outline (paraphrased) | 1.4 | 5.8 | 10.6 | 13.7 |
| Knowledge Article · human | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.0 | 2.3 | 10.0 | 16.4 |
| Personal About Page · AI | IdeaLens · outline (paraphrased) | 73.2 | 90.6 | 96.8 | 98.9 |
| Personal About Page · AI | IdeaLens-ModernBERT-L · outline (paraphrased) | 34.1 | 72.0 | 90.4 | 96.3 |
| Personal About Page · human | IdeaLens · outline (paraphrased) | 0.3 | 0.8 | 1.6 | 3.5 |
| Personal About Page · human | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.1 | 0.4 | 1.5 | 5.2 |
| News Article · AI | IdeaLens · outline (paraphrased) | 81.7 | 93.2 | 97.3 | 98.8 |
| News Article · AI | IdeaLens-ModernBERT-L · outline (paraphrased) | 58.2 | 82.8 | 94.3 | 97.8 |
| News Article · human | IdeaLens · outline (paraphrased) | 0.6 | 1.4 | 2.6 | 5.4 |
| News Article · human | IdeaLens-ModernBERT-L · outline (paraphrased) | 0.3 | 0.9 | 2.4 | 6.2 |

**By topic.** Fire rate % at the 1% cut.

| Topic | Arm | n | IdeaLens · outline (paraphrased) | IdeaLens-ModernBERT-L · outline (paraphrased) |
|---|---|---|---|---|
| Art & Design | AI | 872 | 96.8 | 92.0 |
| Crime & Law | AI | 855 | 95.3 | 86.5 |
| Education & Jobs | AI | 1,062 | 94.1 | 81.3 |
| Entertainment | AI | 1,447 | 95.7 | 89.3 |
| Fashion & Beauty | AI | 1,044 | 97.7 | 90.5 |
| Finance & Business | AI | 1,645 | 94.7 | 81.9 |
| Food & Dining | AI | 879 | 97.3 | 90.1 |
| Games | AI | 1,216 | 94.9 | 82.4 |
| Hardware | AI | 761 | 97.2 | 90.3 |
| Health | AI | 1,368 | 93.9 | 80.3 |
| History | AI | 650 | 97.8 | 94.3 |
| Home & Hobbies | AI | 1,105 | 95.6 | 85.7 |
| Industrial | AI | 691 | 95.4 | 84.5 |
| Literature | AI | 1,994 | 97.2 | 91.3 |
| Politics | AI | 864 | 95.7 | 87.5 |
| Religion | AI | 1,085 | 95.6 | 85.3 |
| Science & Tech. | AI | 1,110 | 95.5 | 85.9 |
| Social Life | AI | 1,340 | 95.5 | 85.4 |
| Software | AI | 739 | 96.1 | 84.2 |
| Software Dev. | AI | 666 | 94.1 | 80.5 |
| Sports & Fitness | AI | 1,201 | 96.7 | 92.1 |
| Transportation | AI | 771 | 97.0 | 89.6 |
| Travel | AI | 930 | 95.9 | 91.4 |
| Art & Design | human | 966 | 2.1 | 2.1 |
| Crime & Law | human | 1,092 | 2.5 | 1.9 |
| Education & Jobs | human | 1,082 | 3.0 | 1.6 |
| Entertainment | human | 1,249 | 2.5 | 2.1 |
| Fashion & Beauty | human | 822 | 2.4 | 2.8 |
| Finance & Business | human | 1,403 | 3.1 | 1.9 |
| Food & Dining | human | 812 | 2.5 | 1.7 |
| Games | human | 1,227 | 3.7 | 1.7 |
| Hardware | human | 705 | 2.8 | 1.7 |
| Health | human | 1,494 | 2.8 | 2.1 |
| History | human | 1,068 | 0.4 | 0.5 |
| Home & Hobbies | human | 1,058 | 3.9 | 2.9 |
| Industrial | human | 681 | 3.2 | 2.1 |
| Literature | human | 1,135 | 0.6 | 0.9 |
| Politics | human | 1,304 | 0.7 | 0.6 |
| Religion | human | 1,409 | 2.4 | 1.6 |
| Science & Tech. | human | 1,161 | 3.9 | 3.1 |
| Social Life | human | 1,027 | 2.6 | 2.7 |
| Software | human | 768 | 5.3 | 3.9 |
| Software Dev. | human | 883 | 1.6 | 1.6 |
| Sports & Fitness | human | 1,206 | 2.3 | 2.6 |
| Transportation | human | 923 | 2.8 | 2.8 |
| Travel | human | 1,099 | 2.7 | 2.6 |
