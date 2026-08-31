"""The standing work queues, and the record of what a person did with each item.

Two requirements drive this file, and both come from how Chleo would actually use the
product rather than from how a demo is easiest to build:

  * **Work is already there when she opens the page.** Nobody types a complaint into a box
    that already arrived in the case system. The AI has been through the batch before she
    arrives, so a queue renders instantly and shows the same thing every time.
  * **Her decisions survive her closing the tab.** A disposition held only in session state
    is a demo record, not an audit record — and the audit record is the thing that answers
    the ombudsman in March.

So the AI output is precomputed to `mvp/queues/` and committed, while human decisions are appended to
`mvp/queues/decision_events.json`, which is NOT committed — it is this operator's
own working state, and a fresh clone should start with an empty queue rather than someone
else's decisions.

Precomputing is also the honest choice for a live demo. Sixty model calls on stage is sixty
chances for a network to fail in front of a panel, and the guard behaviour being
demonstrated is identical either way.
"""
from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUEUES = HERE / "queues"
TRIAGE_FILE = QUEUES / "triage_queue.json"
ANOMALY_FILE = QUEUES / "anomaly_queue.json"
EVENTS_FILE = QUEUES / "decision_events.json"

_lock = threading.Lock()

# What a person can do with an item. `PENDING` is the absence of a decision, not a decision
# — the distinction matters, because "nobody has looked at this yet" and "somebody looked
# and let it through" are different facts and must never collapse into one another.
PENDING = "pending"
TRIAGE_ACTIONS = {
    "accepted": "Accepted — routed as proposed",
    "rerouted": "Rerouted — handler chose a different team",
    "escalated": "Sent to a person for full review",
}
ANOMALY_ACTIONS = {
    "escalated": "Escalated to an analyst",
    "dismissed": "Dismissed — ordinary for this account",
    "more_info": "Needs more information",
}


def _read(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def load_triage() -> list[dict]:
    return _read(TRIAGE_FILE, [])


def load_anomaly() -> list[dict]:
    return _read(ANOMALY_FILE, [])


def events() -> list[dict]:
    """Every human action ever taken, oldest first. Append-only.

    This list IS the decision log, and the queues are a projection of it — each item's
    status is simply its latest event. One store, two views: the queue answers "what is
    the state of this item", the log answers "what happened, in order". An item revisited
    appears once in the queue and twice in the log, which is the correct answer to both
    questions.

    Append-only for the reason the GDPR pack already commits to: a past decision is a
    record of what was decided at the time, and overwriting it destroys the audit value
    that justifies keeping it at all.
    """
    return _read(EVENTS_FILE, [])


def record(item_id: str, action: str, *, capability: str, by: str,
           proposed: str = "", reason_code: str = "", note: str = "") -> None:
    """Append one human action. Read-modify-write under a lock.

    Streamlit serves every browser session from one process, so two tabs on the same queue
    is not hypothetical — it is what happens demoing on a laptop with the projector
    mirroring. Without the lock the second write silently drops the first.
    """
    with _lock:
        log = events()
        log.append({
            "at": datetime.now().isoformat(timespec="seconds"),
            "item_id": item_id, "capability": capability, "action": action,
            "proposed": proposed, "reason_code": reason_code, "by": by, "note": note,
        })
        EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        EVENTS_FILE.write_text(json.dumps(log, indent=2))


def latest_by_item() -> dict[str, dict]:
    """The projection the queues read: item_id -> its most recent event."""
    out: dict[str, dict] = {}
    for e in events():          # already oldest first, so the last write wins
        out[e["item_id"]] = e
    return out


def status_of(item_id: str, item: dict, latest: dict | None = None) -> str:
    """This row's status: the latest human action if there is one, else the system's own.

    The system's own outcome is `proposed` or `held` — the guard ladder decided it. A human
    action changes the STATUS; it never edits what the system proposed, which stays on the
    item where an auditor can still see it.
    """
    e = (latest if latest is not None else latest_by_item()).get(item_id)
    if e:
        return e["action"]
    return "proposed" if item.get("decision") == "PROPOSE_TO_HANDLER" else "held"


PENDING_STATUSES = {"proposed", "held"}
DISAGREEMENTS = {"rerouted", "dismissed"}


def summary(items: list[dict], id_key: str = "item_id") -> dict:
    """Counts for the Overview page. One pass over the queue, one read of the events."""
    latest = latest_by_item()
    out = {"total": len(items), "proposed": 0, "held": 0, "handled": 0, "pending": 0,
           "agreed": 0, "disagreed": 0, "by_reason": {}, "by_status": {}}
    for it in items:
        if it.get("decision") == "PROPOSE_TO_HANDLER":
            out["proposed"] += 1
        else:
            out["held"] += 1
            rc = it.get("reason_code", "UNKNOWN")
            out["by_reason"][rc] = out["by_reason"].get(rc, 0) + 1
        s = status_of(it[id_key], it, latest)
        out["by_status"][s] = out["by_status"].get(s, 0) + 1
        if s in PENDING_STATUSES:
            out["pending"] += 1
        else:
            out["handled"] += 1
            if s in DISAGREEMENTS:
                out["disagreed"] += 1
            elif s in ("accepted", "escalated"):
                out["agreed"] += 1
    # Agreement rate is measured over items a person actually decided on. Counting
    # untouched rows as agreement would make an unattended queue look like a triumph.
    out["agreement_rate"] = (100 * out["agreed"] / (out["agreed"] + out["disagreed"])
                             if (out["agreed"] + out["disagreed"]) else None)
    return out
