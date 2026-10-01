# PeerPrism: similarity of each transformed review to its original human review


- Pairs: 4,800 transformed reviews matched to their original in our slice (paper id + review id); unmatched: 0. Synthetic reviews have no original.
- Document similarity: OpenAI text-embedding-3-large (3,072 dimensions, L2-normalised, up to 8,191 tokens; 0 documents truncated), direct API calls, 6,896,280 tokens billed.
- Lexical: token-set Jaccard and ROUGE-L F1 over lowercased word tokens (exact LCS).
- Ideas: our raw outlines, items embedded with text-embedding-3-large. An original item is **kept** when its best match among the transformed outline's items reaches tau = 0.682, the 95th percentile of best-match cosines against a human review of a different paper (7,493 items). "New items traceable" is the same test from the transformed outline's side (1 minus it = items with no counterpart in the original).
- Reference rows: a second human review of the same paper (different reviewer) and a human review of a different paper, one per original, fixed seed.
- Cells are mean / median.

## By arm

| Arm | n | doc cosine | token Jaccard | ROUGE-L F1 | length ratio | orig items kept | new items traceable | mean best item cos |
|---|---|---|---|---|---|---|---|---|
| rewritten | 1,500 | 0.928 / 0.931 | 0.394 / 0.377 | 0.436 / 0.425 | 1.034 / 1.000 | 0.808 / 0.846 | 0.818 / 0.846 | 0.763 / 0.765 |
| extract_regenerate | 1,500 | 0.868 / 0.866 | 0.352 / 0.287 | 0.301 / 0.227 | 1.450 / 1.324 | 0.562 / 0.556 | 0.507 / 0.500 | 0.690 / 0.685 |
| expanded | 900 | 0.888 / 0.888 | 0.491 / 0.330 | 0.483 / 0.354 | 2.336 / 2.004 | 0.607 / 0.600 | 0.551 / 0.533 | 0.709 / 0.700 |
| hybrid | 900 | 0.872 / 0.868 | 0.401 / 0.268 | 0.371 / 0.222 | 2.273 / 1.777 | 0.500 / 0.455 | 0.415 / 0.333 | 0.679 / 0.663 |
| ref: other reviewer, same paper | 673 | 0.815 / 0.819 | 0.207 / 0.207 | 0.176 / 0.175 | 1.272 / 1.017 | 0.171 / 0.167 | 0.174 / 0.154 | 0.570 / 0.570 |
| ref: human review, different paper | 673 | 0.511 / 0.508 | 0.146 / 0.145 | 0.146 / 0.147 | 1.268 / 1.026 | 0.057 / 0.054 | 0.054 / 0.050 | 0.476 / 0.475 |

## By arm and generator

| Arm | Generator | n | doc cosine | token Jaccard | ROUGE-L F1 | length ratio | orig items kept | new items traceable | mean best item cos |
|---|---|---|---|---|---|---|---|---|---|
| rewritten | claude-haiku-4.5 | 250 | 0.913 / 0.917 | 0.318 / 0.314 | 0.361 / 0.359 | 1.114 / 1.098 | 0.788 / 0.800 | 0.801 / 0.800 | 0.753 / 0.751 |
| rewritten | deepseek-r1 | 250 | 0.919 / 0.926 | 0.373 / 0.378 | 0.399 / 0.405 | 0.985 / 0.965 | 0.784 / 0.818 | 0.798 / 0.833 | 0.753 / 0.754 |
| rewritten | gemini-2.5-flash | 250 | 0.938 / 0.942 | 0.370 / 0.368 | 0.441 / 0.442 | 1.257 / 1.231 | 0.841 / 0.857 | 0.850 / 0.875 | 0.770 / 0.771 |
| rewritten | gpt-5 | 250 | 0.951 / 0.950 | 0.471 / 0.426 | 0.535 / 0.493 | 0.898 / 0.889 | 0.879 / 0.900 | 0.887 / 0.900 | 0.789 / 0.791 |
| rewritten | llama-4-scout | 251 | 0.919 / 0.924 | 0.452 / 0.443 | 0.481 / 0.487 | 1.009 / 1.000 | 0.756 / 0.800 | 0.768 / 0.800 | 0.751 / 0.760 |
| rewritten | o4-mini | 249 | 0.926 / 0.929 | 0.378 / 0.362 | 0.400 / 0.387 | 0.940 / 0.943 | 0.800 / 0.818 | 0.803 / 0.833 | 0.759 / 0.756 |
| extract_regenerate | claude-haiku-4.5 | 250 | 0.843 / 0.845 | 0.275 / 0.265 | 0.207 / 0.196 | 1.963 / 1.863 | 0.496 / 0.500 | 0.380 / 0.375 | 0.673 / 0.671 |
| extract_regenerate | deepseek-r1 | 250 | 0.846 / 0.848 | 0.268 / 0.250 | 0.215 / 0.196 | 1.363 / 1.248 | 0.497 / 0.500 | 0.463 / 0.444 | 0.669 / 0.665 |
| extract_regenerate | gemini-2.5-flash | 250 | 0.869 / 0.871 | 0.343 / 0.328 | 0.288 / 0.264 | 1.693 / 1.593 | 0.625 / 0.625 | 0.577 / 0.571 | 0.706 / 0.706 |
| extract_regenerate | gpt-5 | 250 | 0.909 / 0.896 | 0.480 / 0.318 | 0.437 / 0.259 | 1.281 / 1.166 | 0.710 / 0.714 | 0.609 / 0.571 | 0.735 / 0.724 |
| extract_regenerate | llama-4-scout | 250 | 0.864 / 0.873 | 0.397 / 0.327 | 0.355 / 0.271 | 1.031 / 1.000 | 0.470 / 0.429 | 0.538 / 0.500 | 0.665 / 0.661 |
| extract_regenerate | o4-mini | 250 | 0.877 / 0.867 | 0.352 / 0.266 | 0.304 / 0.210 | 1.372 / 1.316 | 0.573 / 0.556 | 0.476 / 0.429 | 0.693 / 0.682 |
| expanded | claude-haiku-4.5 | 150 | 0.802 / 0.800 | 0.236 / 0.227 | 0.206 / 0.184 | 3.787 / 3.338 | 0.350 / 0.333 | 0.284 / 0.273 | 0.616 / 0.621 |
| expanded | deepseek-r1 | 150 | 0.863 / 0.869 | 0.215 / 0.212 | 0.180 / 0.178 | 2.128 / 1.986 | 0.385 / 0.357 | 0.313 / 0.294 | 0.649 / 0.645 |
| expanded | gemini-2.5-flash | 150 | 0.896 / 0.897 | 0.366 / 0.358 | 0.420 / 0.408 | 3.305 / 3.157 | 0.646 / 0.640 | 0.577 / 0.586 | 0.711 / 0.710 |
| expanded | gpt-5 | 150 | 1.000 / 1.000 | 0.999 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 | 0.922 / 1.000 | 0.930 / 1.000 | 0.822 / 0.825 |
| expanded | llama-4-scout | 150 | 0.827 / 0.880 | 0.450 / 0.485 | 0.430 / 0.437 | 2.118 / 1.728 | 0.620 / 0.692 | 0.518 / 0.556 | 0.701 / 0.718 |
| expanded | o4-mini | 150 | 0.940 / 1.000 | 0.677 / 1.000 | 0.662 / 1.000 | 1.677 / 1.000 | 0.688 / 0.769 | 0.645 / 0.800 | 0.744 / 0.764 |
| hybrid | claude-haiku-4.5 | 150 | 0.796 / 0.800 | 0.215 / 0.221 | 0.166 / 0.156 | 3.498 / 3.181 | 0.294 / 0.286 | 0.187 / 0.162 | 0.607 / 0.606 |
| hybrid | deepseek-r1 | 150 | 0.860 / 0.860 | 0.252 / 0.247 | 0.214 / 0.210 | 1.652 / 1.468 | 0.410 / 0.375 | 0.309 / 0.300 | 0.656 / 0.656 |
| hybrid | gemini-2.5-flash | 150 | 0.860 / 0.862 | 0.290 / 0.272 | 0.282 / 0.263 | 3.844 / 3.355 | 0.520 / 0.542 | 0.312 / 0.289 | 0.684 / 0.688 |
| hybrid | gpt-5 | 150 | 0.996 / 1.000 | 0.983 / 1.000 | 0.983 / 1.000 | 1.053 / 1.000 | 0.912 / 1.000 | 0.916 / 1.000 | 0.813 / 0.822 |
| hybrid | llama-4-scout | 150 | 0.867 / 0.883 | 0.396 / 0.398 | 0.354 / 0.342 | 1.606 / 1.480 | 0.453 / 0.455 | 0.456 / 0.455 | 0.657 / 0.656 |
| hybrid | o4-mini | 150 | 0.855 / 0.859 | 0.271 / 0.226 | 0.229 / 0.178 | 1.987 / 1.814 | 0.390 / 0.375 | 0.286 / 0.250 | 0.651 / 0.645 |

## Detectors against similarity

Spearman correlation, within each arm, between a similarity measure and the detector's P(AI) of the transformed review (negative = the closer the review stays to the original, the less it is flagged). Detector notes:

- IdeaLens outline: fires at p_human <= 0.1371 (global 1%)
- IdeaLens document: fires at p_human <= 0.08744 (global 1%)
- ProseLens: fires at p_human <= 0.6054 (global 1%)
- IdeaLens-ModernBERT-L outline: fires at p_human <= 0.05541 (global 1%)
- ProseLens-ModernBERT-L: fires at p_human <= 0.1879 (global 1%)
- EditLens-Llama-3B: p_ai, calibrated global 1% cut 0.8281 (fires when ai_score > cut)
- Binoculars: p_ai, calibrated global 1% cut -0.8873 (fires when ai_score > cut)
- Pangram 4: P(AI) = fraction_ai + 0.5 fraction_ai_assisted; fires on AI / AI-assisted

### doc cosine

| Detector | rewritten | extract_regenerate | expanded | hybrid | all four |
|---|---|---|---|---|---|
| IdeaLens outline | -0.32 (n=1,500) | -0.37 (n=1,499) | -0.58 (n=846) | -0.51 (n=866) | -0.66 (n=4,711) |
| IdeaLens document | -0.42 (n=1,500) | -0.46 (n=1,499) | -0.68 (n=846) | -0.62 (n=866) | -0.76 (n=4,711) |
| ProseLens | -0.50 (n=1,500) | -0.52 (n=1,499) | -0.73 (n=846) | -0.65 (n=866) | -0.75 (n=4,711) |
| IdeaLens-ModernBERT-L outline | -0.27 (n=1,500) | -0.31 (n=1,499) | -0.43 (n=846) | -0.38 (n=866) | -0.58 (n=4,711) |
| ProseLens-ModernBERT-L | -0.46 (n=1,500) | -0.45 (n=1,499) | -0.70 (n=846) | -0.60 (n=866) | -0.71 (n=4,711) |
| EditLens-Llama-3B | -0.45 (n=1,500) | -0.39 (n=1,500) | -0.54 (n=900) | -0.40 (n=900) | -0.46 (n=4,800) |
| Binoculars | -0.15 (n=1,500) | -0.25 (n=1,500) | -0.38 (n=900) | -0.11 (n=900) | -0.35 (n=4,800) |
| Pangram 4 | -0.45 (n=1,500) | -0.45 (n=1,500) | -0.75 (n=900) | -0.61 (n=900) | -0.70 (n=4,800) |

### ROUGE-L F1

| Detector | rewritten | extract_regenerate | expanded | hybrid | all four |
|---|---|---|---|---|---|
| IdeaLens outline | -0.37 (n=1,500) | -0.44 (n=1,499) | -0.69 (n=846) | -0.66 (n=866) | -0.72 (n=4,711) |
| IdeaLens document | -0.42 (n=1,500) | -0.55 (n=1,499) | -0.83 (n=846) | -0.80 (n=866) | -0.83 (n=4,711) |
| ProseLens | -0.64 (n=1,500) | -0.68 (n=1,499) | -0.89 (n=846) | -0.84 (n=866) | -0.88 (n=4,711) |
| IdeaLens-ModernBERT-L outline | -0.32 (n=1,500) | -0.42 (n=1,499) | -0.55 (n=846) | -0.54 (n=866) | -0.65 (n=4,711) |
| ProseLens-ModernBERT-L | -0.57 (n=1,500) | -0.54 (n=1,499) | -0.85 (n=846) | -0.79 (n=866) | -0.82 (n=4,711) |
| EditLens-Llama-3B | -0.39 (n=1,500) | -0.41 (n=1,500) | -0.65 (n=900) | -0.50 (n=900) | -0.51 (n=4,800) |
| Binoculars | 0.08 (n=1,500) | -0.02 (n=1,500) | -0.24 (n=900) | 0.04 (n=900) | -0.22 (n=4,800) |
| Pangram 4 | -0.65 (n=1,500) | -0.58 (n=1,500) | -0.90 (n=900) | -0.78 (n=900) | -0.82 (n=4,800) |

### orig items kept

| Detector | rewritten | extract_regenerate | expanded | hybrid | all four |
|---|---|---|---|---|---|
| IdeaLens outline | -0.20 (n=1,491) | -0.24 (n=1,492) | -0.55 (n=842) | -0.55 (n=860) | -0.57 (n=4,685) |
| IdeaLens document | -0.23 (n=1,491) | -0.33 (n=1,492) | -0.66 (n=842) | -0.61 (n=860) | -0.65 (n=4,685) |
| ProseLens | -0.25 (n=1,491) | -0.36 (n=1,492) | -0.73 (n=842) | -0.64 (n=860) | -0.64 (n=4,685) |
| IdeaLens-ModernBERT-L outline | -0.17 (n=1,491) | -0.21 (n=1,492) | -0.41 (n=842) | -0.45 (n=860) | -0.49 (n=4,685) |
| ProseLens-ModernBERT-L | -0.24 (n=1,491) | -0.32 (n=1,492) | -0.70 (n=842) | -0.62 (n=860) | -0.59 (n=4,685) |
| EditLens-Llama-3B | -0.21 (n=1,491) | -0.28 (n=1,492) | -0.55 (n=858) | -0.47 (n=874) | -0.34 (n=4,715) |
| Binoculars | -0.07 (n=1,491) | -0.29 (n=1,492) | -0.19 (n=858) | -0.12 (n=874) | -0.26 (n=4,715) |
| Pangram 4 | -0.24 (n=1,491) | -0.33 (n=1,492) | -0.76 (n=858) | -0.63 (n=874) | -0.58 (n=4,715) |

## Fire rate by how many of the original's ideas were kept

Transformed reviews binned by `orig items kept` (quartiles over all four arms pooled); each cell is the detector's fire rate (global 1% cut; Pangram 4 at its own verdict) and mean P(AI).

**rewritten**

| Detector | <= 0.43 | 0.43 to 0.67 | 0.67 to 0.88 | > 0.88 |
|---|---|---|---|---|
| n | 60 | 252 | 577 | 602 |
| IdeaLens outline | 25.0% / 0.53 | 10.7% / 0.26 | 7.6% / 0.19 | 4.7% / 0.14 |
| IdeaLens document | 41.7% / 0.60 | 13.9% / 0.32 | 7.6% / 0.21 | 4.7% / 0.16 |
| ProseLens | 91.7% / 0.89 | 83.7% / 0.79 | 78.0% / 0.72 | 70.1% / 0.63 |
| IdeaLens-ModernBERT-L outline | 38.3% / 0.72 | 15.1% / 0.47 | 12.7% / 0.42 | 6.3% / 0.35 |
| ProseLens-ModernBERT-L | 86.7% / 0.92 | 80.6% / 0.86 | 71.2% / 0.78 | 62.3% / 0.71 |
| EditLens-Llama-3B | 85.0% / 0.92 | 70.6% / 0.87 | 58.9% / 0.83 | 51.8% / 0.80 |
| Binoculars | 36.7% / -0.90 | 10.7% / -0.96 | 6.9% / -0.97 | 5.3% / -0.97 |
| Pangram 4 | 40.0% / 0.78 | 17.9% / 0.69 | 11.1% / 0.63 | 5.5% / 0.57 |

**extract_regenerate**

| Detector | <= 0.43 | 0.43 to 0.67 | 0.67 to 0.88 | > 0.88 |
|---|---|---|---|---|
| n | 444 | 601 | 300 | 147 |
| IdeaLens outline | 67.1% / 0.82 | 66.1% / 0.81 | 58.3% / 0.73 | 27.9% / 0.33 |
| IdeaLens document | 92.6% / 0.97 | 89.2% / 0.94 | 75.7% / 0.83 | 31.3% / 0.35 |
| ProseLens | 99.8% / 0.99 | 99.0% / 0.98 | 87.0% / 0.86 | 35.4% / 0.35 |
| IdeaLens-ModernBERT-L outline | 83.6% / 0.95 | 79.4% / 0.93 | 72.0% / 0.84 | 32.7% / 0.42 |
| ProseLens-ModernBERT-L | 99.8% / 1.00 | 99.0% / 0.99 | 87.0% / 0.87 | 36.1% / 0.36 |
| EditLens-Llama-3B | 96.4% / 0.97 | 94.7% / 0.96 | 84.3% / 0.88 | 30.6% / 0.52 |
| Binoculars | 37.4% / -0.88 | 26.0% / -0.91 | 17.7% / -0.93 | 9.5% / -0.96 |
| Pangram 4 | 84.2% / 0.94 | 77.5% / 0.91 | 69.0% / 0.80 | 25.9% / 0.32 |

**expanded**

| Detector | <= 0.43 | 0.43 to 0.67 | 0.67 to 0.88 | > 0.88 |
|---|---|---|---|---|
| n | 282 | 204 | 147 | 225 |
| IdeaLens outline | 40.4% / 0.63 | 25.5% / 0.44 | 23.8% / 0.35 | 6.2% / 0.11 |
| IdeaLens document | 82.6% / 0.90 | 56.5% / 0.72 | 34.7% / 0.47 | 6.7% / 0.13 |
| ProseLens | 95.9% / 0.95 | 77.5% / 0.74 | 48.3% / 0.46 | 12.0% / 0.12 |
| IdeaLens-ModernBERT-L outline | 32.2% / 0.67 | 23.0% / 0.53 | 21.8% / 0.46 | 7.6% / 0.26 |
| ProseLens-ModernBERT-L | 93.7% / 0.95 | 74.5% / 0.77 | 43.5% / 0.49 | 11.1% / 0.14 |
| EditLens-Llama-3B | 40.1% / 0.78 | 24.5% / 0.69 | 27.2% / 0.63 | 8.9% / 0.40 |
| Binoculars | 9.2% / -0.94 | 12.3% / -0.95 | 22.4% / -0.94 | 8.9% / -0.97 |
| Pangram 4 | 81.9% / 0.89 | 50.0% / 0.70 | 14.3% / 0.40 | 1.3% / 0.09 |

**hybrid**

| Detector | <= 0.43 | 0.43 to 0.67 | 0.67 to 0.88 | > 0.88 |
|---|---|---|---|---|
| n | 412 | 236 | 104 | 122 |
| IdeaLens outline | 65.8% / 0.82 | 46.4% / 0.68 | 25.0% / 0.42 | 4.1% / 0.07 |
| IdeaLens document | 89.5% / 0.95 | 73.0% / 0.85 | 40.4% / 0.54 | 4.1% / 0.06 |
| ProseLens | 98.5% / 0.97 | 91.8% / 0.89 | 59.6% / 0.57 | 6.6% / 0.06 |
| IdeaLens-ModernBERT-L outline | 61.6% / 0.85 | 51.1% / 0.77 | 32.7% / 0.54 | 5.7% / 0.23 |
| ProseLens-ModernBERT-L | 96.0% / 0.97 | 85.0% / 0.89 | 57.7% / 0.59 | 4.9% / 0.06 |
| EditLens-Llama-3B | 54.1% / 0.83 | 45.3% / 0.80 | 21.2% / 0.61 | 5.7% / 0.34 |
| Binoculars | 17.0% / -0.94 | 19.5% / -0.94 | 11.5% / -0.96 | 1.6% / -0.99 |
| Pangram 4 | 76.9% / 0.85 | 43.2% / 0.65 | 23.1% / 0.39 | 1.6% / 0.04 |

**all four**

| Detector | <= 0.43 | 0.43 to 0.67 | 0.67 to 0.88 | > 0.88 |
|---|---|---|---|---|
| n | 1,198 | 1,293 | 1,128 | 1,096 |
| IdeaLens outline | 58.4% / 0.76 | 45.3% / 0.62 | 24.8% / 0.38 | 8.0% / 0.15 |
| IdeaLens document | 86.6% / 0.93 | 66.4% / 0.77 | 32.3% / 0.44 | 8.6% / 0.17 |
| ProseLens | 98.0% / 0.97 | 91.4% / 0.89 | 74.8% / 0.71 | 46.4% / 0.43 |
| IdeaLens-ModernBERT-L outline | 62.0% / 0.84 | 52.9% / 0.75 | 31.5% / 0.54 | 10.0% / 0.33 |
| ProseLens-ModernBERT-L | 96.4% / 0.97 | 89.0% / 0.91 | 70.6% / 0.75 | 41.9% / 0.47 |
| EditLens-Llama-3B | 68.0% / 0.88 | 69.9% / 0.87 | 58.1% / 0.80 | 35.0% / 0.63 |
| Binoculars | 23.7% / -0.92 | 19.6% / -0.93 | 12.2% / -0.95 | 6.2% / -0.97 |
| Pangram 4 | 79.0% / 0.89 | 55.3% / 0.78 | 28.0% / 0.62 | 6.9% / 0.38 |
