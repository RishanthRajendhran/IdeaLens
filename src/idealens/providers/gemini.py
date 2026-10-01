"""Google Gemini: the Gemini API (API key) and Vertex AI (Google Cloud credentials), online and, on Vertex, batch.

Requests are the training corpus's (idealens.prompts.gemini_body). The default model is gemini-3.7-flash, the
extractor the published thresholds assume.

Credentials
  Gemini API  GEMINI_API_KEY or GOOGLE_API_KEY (or api_key=...)
  Vertex      project=... or GOOGLE_CLOUD_PROJECT; auth from VERTEX_API_KEY, else Application Default Credentials
              (pip install google-auth), else `gcloud auth print-access-token`
Vertex batch needs a Cloud Storage bucket you can write to (gcs_bucket=... or IDEALENS_GCS_BUCKET) and
pip install google-cloud-storage google-auth.
"""
from __future__ import annotations

import json
import os
import random
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
import uuid

from . import Provider, Reply
from ..prompts import gemini_body

DEFAULT_MODEL = "gemini-3.7-flash"
RETRY_CODES = (429, 500, 502, 503, 504)


def parse_response(out: dict) -> Reply:
    cand = (out.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []) if not p.get("thought"))
    u = out.get("usageMetadata") or {}
    usage = {"input": u.get("promptTokenCount", 0), "cached_input": u.get("cachedContentTokenCount", 0),
             "output": u.get("candidatesTokenCount", 0), "reasoning": u.get("thoughtsTokenCount", 0)}
    block = (out.get("promptFeedback") or {}).get("blockReason")
    err = f"blocked: {block}" if block else (None if text else "empty reply")
    return Reply(text or None, usage, err, cand.get("finishReason"))


class _Online(Provider):
    supports_batch = False
    schema_key = "responseSchema"

    def __init__(self, model=None, timeout=900, max_attempts=8):
        self.model = model or DEFAULT_MODEL
        self.timeout, self.max_attempts = timeout, max_attempts

    def _url(self) -> str: ...

    def _headers(self) -> dict: ...

    def generate(self, prompt) -> Reply:
        data = json.dumps(gemini_body(prompt, self.schema_key)).encode()
        last = None
        for attempt in range(self.max_attempts):
            req = urllib.request.Request(self._url(), data=data, headers=self._headers(), method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return parse_response(json.loads(resp.read()))
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}: {e.read().decode(errors='replace')[:500]}"
                if e.code not in RETRY_CODES:
                    break
            except (urllib.error.URLError, TimeoutError) as e:
                last = f"request failed: {e}"
            time.sleep(min(120, 2 ** attempt * 5) * (1 + random.random()))
        return Reply(None, error=last)


class GeminiAPI(_Online):
    name = "gemini"
    schema_key = "responseJsonSchema"

    def __init__(self, model=None, api_key=None, **kw):
        super().__init__(model, **kw)
        self.key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.key:
            raise RuntimeError("no Gemini API key: pass api_key or set GEMINI_API_KEY (or use provider='vertex')")

    def _url(self):
        return f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def _headers(self):
        return {"Content-Type": "application/json", "x-goog-api-key": self.key}


class Vertex(_Online):
    name = "vertex"
    supports_batch = True

    def __init__(self, model=None, project=None, location="global", api_key=None, gcs_bucket=None,
                 gcs_prefix="idealens_batch", poll_interval=60, labels=None, **kw):
        super().__init__(model, **kw)
        self.project = project or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.key = api_key or os.environ.get("VERTEX_API_KEY")
        self.host = "aiplatform.googleapis.com" if location == "global" else f"{location}-aiplatform.googleapis.com"
        if not self.project and not self.key:
            raise RuntimeError("Vertex needs project=... (or GOOGLE_CLOUD_PROJECT) or an api_key")
        self.bucket = gcs_bucket or os.environ.get("IDEALENS_GCS_BUCKET")
        self.gcs_prefix, self.poll_interval, self.labels = gcs_prefix, poll_interval, labels or {}
        self._token, self._token_at, self._lock = None, 0.0, threading.Lock()
        if not self.key:
            self._access_token()   # fail here, before any request, when no credentials can be found

    def _model_path(self):
        m = self.model if "/" in self.model else f"publishers/google/models/{self.model}"
        return m if (self.key and not self.project) else f"projects/{self.project}/locations/{self.location}/{m}"

    def _url(self):
        return f"https://{self.host}/v1/{self._model_path()}:generateContent"

    def _access_token(self) -> str:
        with self._lock:
            if self._token and time.time() - self._token_at < 1800:
                return self._token
            try:
                import google.auth
                import google.auth.transport.requests
                creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
                creds.refresh(google.auth.transport.requests.Request())
                self._token = creds.token
            except Exception as e:
                why = f"google-auth: {type(e).__name__}: {e}"
                try:
                    self._token = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True,
                                                 text=True, check=True).stdout.strip()
                except Exception as e2:
                    raise RuntimeError(
                        "no Vertex credentials: set VERTEX_API_KEY, or pip install 'idealens[vertex]' and run "
                        "`gcloud auth application-default login`, or put gcloud on PATH "
                        f"({why}; gcloud: {type(e2).__name__}: {e2})") from None
            self._token_at = time.time()
            return self._token

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.key:
            h["x-goog-api-key"] = self.key
        else:
            h["Authorization"] = f"Bearer {self._access_token()}"
        return h

    # ------------------------------------------------------------------ batch (Vertex Batch Prediction via GCS)
    def run_batch(self, prompts: dict, log=print, description: str = "idealens") -> dict:
        """prompts: {id: Prompt}. Returns {id: Reply}. Uploads one JSONL to gs://<bucket>/<prefix>/..., runs one
        batchPredictionJob, downloads the predictions. Keep prompts of the same format together (the caller sorts):
        identical system prefixes in consecutive rows earn the cached-input rate."""
        if not self.bucket:
            raise RuntimeError("Vertex batch needs a Cloud Storage bucket: gcs_bucket=... or IDEALENS_GCS_BUCKET")
        from google.cloud import storage
        client = storage.Client(project=self.project)
        bucket = client.bucket(self.bucket)
        run = f"{self.gcs_prefix}/{description}_{len(prompts)}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
            for pid, p in prompts.items():
                fh.write(json.dumps({"custom_id": str(pid), "request": gemini_body(p, "responseSchema")},
                                    ensure_ascii=False) + "\n")
        bucket.blob(f"{run}/input/requests.jsonl").upload_from_filename(fh.name)
        os.unlink(fh.name)
        body = {"displayName": description[:120], "model": f"publishers/google/models/{self.model}",
                "inputConfig": {"instancesFormat": "jsonl",
                                "gcsSource": {"uris": [f"gs://{self.bucket}/{run}/input/requests.jsonl"]}},
                "outputConfig": {"predictionsFormat": "jsonl",
                                 "gcsDestination": {"outputUriPrefix": f"gs://{self.bucket}/{run}/output"}}}
        if self.labels:
            body["labels"] = self.labels
        base = f"https://{self.host}/v1beta1/projects/{self.project}/locations/{self.location}"
        job = self._rest("POST", f"{base}/batchPredictionJobs", body)
        log(f"Vertex batch job {job['name']}: {len(prompts)} requests, input gs://{self.bucket}/{run}")
        t0 = time.time()
        while True:
            job = self._rest("GET", f"https://{self.host}/v1beta1/{job['name']}")
            st, cs = job.get("state", ""), job.get("completionStats") or {}
            log(f"  [{(time.time() - t0) / 60:.1f} min] {st} ok={cs.get('successfulCount', 0)} "
                f"failed={cs.get('failedCount', 0)}")
            if "SUCCEEDED" in st:
                break
            if any(s in st for s in ("FAILED", "CANCELLED", "EXPIRED")):
                raise RuntimeError(f"Vertex batch job {job['name']} ended {st}: {job.get('error')}")
            time.sleep(self.poll_interval)
        out_dir = (job.get("outputInfo") or {}).get("gcsOutputDirectory") or f"gs://{self.bucket}/{run}/output"
        prefix = out_dir.split(f"gs://{self.bucket}/", 1)[1]
        results = {}
        for blob in client.list_blobs(bucket, prefix=prefix):
            if not blob.name.endswith(".jsonl"):
                continue
            for line in blob.download_as_text().splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                r = parse_response(rec.get("response") or {})
                if r.text is None and not rec.get("response"):
                    r.error = str(rec.get("status") or "empty response")
                results[rec.get("custom_id")] = r
        for pid in prompts:  # rows Vertex dropped entirely
            results.setdefault(str(pid), Reply(None, error="missing from batch output"))
        return results

    def _rest(self, method, url, body=None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(6):
            req = urllib.request.Request(url, data=data, headers=self._headers(), method=method)
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    return json.loads(resp.read())
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="replace")[:1500]
                if e.code not in RETRY_CODES or attempt == 5:
                    raise RuntimeError(f"Vertex {method} {url} failed [{e.code}]: {msg}") from None
            except (urllib.error.URLError, TimeoutError):
                if attempt == 5:
                    raise
            time.sleep(10 * (attempt + 1))
