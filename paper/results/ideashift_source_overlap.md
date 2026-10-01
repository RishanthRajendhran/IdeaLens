# IdeaShift source overlap: how much of the source each level carries


- Embeddings: OpenAI text-embedding-3-large via the Batch API (10,712,687 tokens, about $0.70; 11 documents truncated to 8,191 tokens).
- Items: raw outlines, `content` only. A source item is **kept** when its best match among the level's items reaches tau = 0.471, the 95th percentile of best-match cosines against another source, same format and topic (9,027 items). **Traceable** is the same test from the level's side (1 minus it = items the model added).
- Reference rows: a different source of the same format and side, and a different source of the same format and topic (either side), one each per source.
- Cells are mean / median where marked, else mean. Missing pairs: none.

## AI sources (AI sources)

| Level | Given to the writer | n | doc cosine | source items kept | level items traceable | ROUGE-L F1 | length ratio | items (level / source) |
|---|---|---|---|---|---|---|---|---|
| level 0 | type + broad subject | 263 | 0.537 / 0.544 | 0.348 / 0.286 | 0.310 / 0.227 | 0.123 | 1.187 | 27.3 / 20.0 |
| level 1 | very high-level topic | 263 | 0.589 / 0.594 | 0.471 / 0.462 | 0.398 / 0.379 | 0.126 | 1.222 | 27.5 / 20.0 |
| level 2 | global themes | 263 | 0.788 / 0.806 | 0.874 / 0.933 | 0.822 / 0.889 | 0.144 | 1.227 | 26.9 / 20.0 |
| level 3 | themes + role sequence | 263 | 0.792 / 0.809 | 0.885 / 0.950 | 0.832 / 0.889 | 0.143 | 1.190 | 26.1 / 20.0 |
| level 4 | themes + full outline | 263 | 0.865 / 0.874 | 0.997 / 1.000 | 0.984 / 1.000 | 0.208 | 1.166 | 26.9 / 20.0 |
| level 5 | full outline, realise exactly | 263 | 0.889 / 0.896 | 0.999 / 1.000 | 0.998 / 1.000 | 0.250 | 0.994 | 21.9 / 20.0 |
| ref: another source, same format and topic |  | 241 | 0.348 / 0.339 | 0.064 / 0.000 | 0.062 / 0.000 | 0.116 | 1.394 | 19.7 / 19.8 |
| ref: another source, same format |  | 263 | 0.290 / 0.283 | 0.018 / 0.000 | 0.017 / 0.000 | 0.113 | 1.387 | 18.5 / 20.0 |

## Human sources (human sources)

| Level | Given to the writer | n | doc cosine | source items kept | level items traceable | ROUGE-L F1 | length ratio | items (level / source) |
|---|---|---|---|---|---|---|---|---|
| level 0 | type + broad subject | 237 | 0.518 / 0.527 | 0.301 / 0.222 | 0.269 / 0.176 | 0.122 | 1.190 | 26.5 / 19.5 |
| level 1 | very high-level topic | 237 | 0.572 / 0.578 | 0.450 / 0.440 | 0.405 / 0.364 | 0.125 | 1.222 | 27.6 / 19.5 |
| level 2 | global themes | 237 | 0.746 / 0.767 | 0.831 / 0.900 | 0.801 / 0.857 | 0.140 | 1.189 | 25.4 / 19.5 |
| level 3 | themes + role sequence | 237 | 0.754 / 0.781 | 0.835 / 0.900 | 0.824 / 0.900 | 0.138 | 1.156 | 24.1 / 19.5 |
| level 4 | themes + full outline | 237 | 0.842 / 0.866 | 0.982 / 1.000 | 0.969 / 1.000 | 0.204 | 1.104 | 24.1 / 19.5 |
| level 5 | full outline, realise exactly | 237 | 0.868 / 0.884 | 0.990 / 1.000 | 0.988 / 1.000 | 0.237 | 0.958 | 21.8 / 19.5 |
| ref: another source, same format and topic |  | 214 | 0.330 / 0.318 | 0.047 / 0.000 | 0.042 / 0.000 | 0.116 | 1.370 | 19.8 / 19.9 |
| ref: another source, same format |  | 237 | 0.235 / 0.232 | 0.008 / 0.000 | 0.008 / 0.000 | 0.113 | 1.495 | 19.6 / 19.5 |

## Step-to-step, per source

Share of sources whose source-items-kept rises (strictly / ties count half) from one level to the next.

| Side | level 0 -> level 1 | level 1 -> level 2 | level 2 -> level 3 | level 3 -> level 4 | level 4 -> level 5 |
|---|---|---|---|---|---|
| AI sources | 67% (n=263) | 93% (n=263) | 54% (n=263) | 78% (n=263) | 51% (n=263) |
| human sources | 72% (n=237) | 94% (n=237) | 51% (n=237) | 85% (n=237) | 51% (n=237) |
