"""Provider clients. Every bulk call in this project goes through one of these.

Rules this package exists to enforce:

* **Batch, never online, for anything over a handful of documents.** The batch
  APIs are half price and this project's spend is dominated by two bulk stages.
  A config field named `mode: batch` is only a label; the transport is chosen
  by which function you call, so call the batch one.
* **Prices are polled, never hard-coded.** Provider discounts have moved twice
  during this project. `pricing.py` fetches or reads a dated table and every
  cost estimate goes through it.
* **Usage is recorded per row.** Reasoning tokens bill at the output rate and
  are reported separately from completion tokens, so a cost model that reads
  only completions undercounts by several times at high thinking levels.
"""
from .keys import require_key, preflight  # noqa: F401
