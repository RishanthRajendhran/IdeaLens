# Configs

Every script in this repository is driven by a config file. Nothing that varies
between runs lives in Python source, so a result can be reproduced from its
`run.json` alone and a new eval or model arm is a new YAML file rather than a new
script.

## What is where

| file / directory | what it configures |
|---|---|
| `paths.yaml` | the only machine-specific paths. Edit this once after cloning. |
| `models.yaml` | every trained detector arm: backend, checkpoint, input setting |
| `pricing.yaml` | provider rates, with an `as_of` date that is checked at run time |
| `evals/` | one file per evaluation set: what it asks, where its data is, how to report it |
| `training/` | one file per training run |
| `pipeline/` | the extraction, de-leak and format-classification stages |
| `calibration/` | which split each model's thresholds are fitted on |
| `features/` | the four feature-discovery configurations |
| `pangram/` | the surface-detector baseline |

## How they compose

`extends:` names one or more parents, merged depth-first with the child winning.
Shared defaults live in `_base.yaml` files, which are never loaded directly.

```yaml
extends: _base.yaml
name: My new eval
number: 12
```

Lists **replace** rather than concatenate. An eval that overrides `fpr_targets`
means "use exactly these"; a merge that kept the defaults alongside them would be
silently wrong.

## Overriding at the command line

```bash
python scripts/eval/score.py --config test5_peer_review --model nemotron_1m_full \
    --set limit=50 --set report.n_boot=0
```

`--set` takes `key.path=value`, is repeatable, and parses values as YAML, so
`true`, `3`, `0.01` and `[a, b]` arrive with the type they look like. Overrides
are recorded in `run.json`, so an overridden run is never mistaken for a default one.

## Secrets

`${VAR}` and `${VAR:-default}` interpolate from the environment. **No key, token,
service-account file or `.env` belongs in this directory or anywhere else in the
repository.** Run `python -m ideadet.llm.keys` to see which providers are usable.
