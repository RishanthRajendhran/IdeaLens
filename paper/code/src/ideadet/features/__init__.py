"""Feature discovery and interpretable probes: what the detector is keying on.

Two questions, two tools, and they are not interchangeable:

* **Discovery** (`discovery.py`) asks a frontier model to read contrast sets and
  propose named, operationalisable features. It produces hypotheses.
* **Probes** (`probes.py`) computes candidate features programmatically and fits
  a transparent classifier on them. It produces measurements.

Run discovery to generate the feature bank, probes to test it. A feature that
sounds compelling and does not compute is a failed hypothesis, not a finding.
"""
