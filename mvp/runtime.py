"""Everything the spine needs from the outside world: keys, the model client, tracing.

Kept apart from `spine.py` so the decision logic can be exercised with no network and no
credentials — see `mvp/test_spine.py`, which runs the full guard ladder against a stub.

Secrets live in ONE shared file for all Ironhack work, `~/.config/ironhack/.env.local`,
never in this repo. `.env.example` documents the names; the values never appear here, in a
commit, or in a trace.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

ENV_FILE = Path.home() / ".config/ironhack/.env.local"
LOCAL_ENV = Path(__file__).resolve().parents[1] / ".env.local"   # optional per-repo override
TRACING_PROJECT = "capstone-mvp"

_SALT = os.environ.get("PSEUDONYM_SALT", "capstone-round1")
PSEUDONYM_PREFIX = "cx_"


def env(key: str) -> str | None:
    """One key at a time, by name. Never returns or logs the whole map."""
    if os.environ.get(key):
        return os.environ[key]
    for f in (LOCAL_ENV, ENV_FILE):
        if f.exists():
            m = re.search(rf"^{re.escape(key)}=(.*)$", f.read_text(), re.M)
            if m:
                v = m.group(1).strip().strip('"').strip("'")
                if v:
                    return v
    return None


def key_fingerprint(key_name: str) -> str:
    """Presence check that never reveals a value — length plus a short digest."""
    v = env(key_name)
    if not v:
        return "absent"
    return f"present (len {len(v)}, sha256:{hashlib.sha256(v.encode()).hexdigest()[:8]})"


def pseudonymise(identifier) -> str:
    """Salted alias for a subject reference. IDEMPOTENT ON PURPOSE.

    Pseudonymisation happens once, at the boundary. Hashing an already-hashed reference
    produces a second, different alias that still looks valid — right prefix, right length
    — while silently joining to nothing. That defect was real in Round 1 and cost a broken
    join across the whole monitoring export, so re-aliasing is a no-op here.
    """
    s = str(identifier)
    if s.startswith(PSEUDONYM_PREFIX):
        return s
    return PSEUDONYM_PREFIX + hashlib.sha256(f"{_SALT}:{s}".encode()).hexdigest()[:16]


# --------------------------------------------------------------------------- model client

class ModelUnavailable(RuntimeError):
    """Raised when no key is configured. The spine turns this into ERROR_MODEL_CALL."""


_client = None


def _openai():
    global _client
    if _client is None:
        key = env("OPENAI_API_KEY")
        if not key:
            raise ModelUnavailable(
                "OPENAI_API_KEY is not set. Add it to ~/.config/ironhack/.env.local")
        from openai import OpenAI
        _client = OpenAI(api_key=key, timeout=45.0, max_retries=2)
    return _client


def call_model(messages: list[dict], model: str) -> str:
    """The single path to the model. Temperature 0 so a demo is reproducible."""
    r = _openai().chat.completions.create(
        model=model, messages=messages, temperature=0,
        response_format={"type": "json_object"})
    return r.choices[0].message.content or ""


# ------------------------------------------------------------------------------- tracing

def configure_langsmith(project: str = TRACING_PROJECT) -> bool:
    """Point the SDK at the EU workspace. Returns whether tracing is configured.

    The workspace is EU-hosted: a key from it authenticates against the default US
    endpoint and then 403s on every call, which reads as a bad key rather than a wrong
    region. The endpoint is therefore always set explicitly.
    """
    key = env("LANGSMITH_API_KEY")
    if not key:
        return False
    os.environ["LANGSMITH_API_KEY"] = key
    os.environ["LANGSMITH_ENDPOINT"] = env("LANGSMITH_ENDPOINT") or "https://eu.api.smith.langchain.com"
    os.environ["LANGSMITH_PROJECT"] = project
    os.environ["LANGSMITH_TRACING"] = "true"
    return True


def trace(decision, request_meta: dict) -> bool:
    """Record one decision in monitoring. Best effort, and never able to change it.

    Round 1 taught this the hard way: a tracing step wired *inline* into the n8n workflow
    replaced the payload and broke the routing that followed it. Observing must not affect
    the observed, so this is a leaf — it is called after the Decision exists, it returns a
    bool, and nothing downstream reads its result.

    Only the pseudonymous ref is sent. No complaint id, no account number, no name.
    """
    if not configure_langsmith():
        return False
    try:
        from langsmith import Client
        Client().create_run(
            name=f"mvp_{decision.capability}",
            run_type="chain",
            project_name=TRACING_PROJECT,
            inputs={"capability": decision.capability, "ref": decision.ref, **request_meta},
            outputs=decision.as_dict(),
            extra={"metadata": {
                "reason_code": decision.reason_code,
                "decision": decision.decision,
                "failed_stage": decision.failed_stage or "none",
                "capability": decision.capability,
                "model": decision.model,
            }},
        )
        return True
    except Exception:
        return False        # monitoring being down must never stop the system deciding
