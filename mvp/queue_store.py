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
SETTINGS_FILE = QUEUES / "settings.json"

_lock = threading.Lock()

# What a person can do with an item. `PENDING` is the absence of a decision, not a decision
# — the distinction matters, because "nobody has looked at this yet" and "somebody looked
# and let it through" are different facts and must never collapse into one another.
PENDING = "pending"
TRIAGE_ACTIONS = {
    "accepted": "Accepted — routed as proposed",
    "rerouted": "Rerouted — send to a different team",
    "escalated": "Sent to a person for full review",
}

# A reroute that does not say WHERE is the most expensive omission in this system. The
# correction is the only signal that says how the model is wrong rather than merely that it
# was wrong: it is what improves the prompt, and it is what lets the ops lead see which
# teams the model confuses. `destination` carries it.
NEEDS_DESTINATION = {"rerouted"}
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
           proposed: str = "", reason_code: str = "", note: str = "",
           destination: str = "") -> None:
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
            "destination": destination,
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


# --------------------------------------------------------------------------- the clock
# A complaints operation is measured against a deadline, and the Round 1 dashboard already
# reported that 335 of this corpus missed one. A queue that cannot sort by age is a queue a
# regulated firm cannot use, so age and time-remaining are computed here, once, for both the
# queue page and the Overview.
#
# SLA_DAYS is an ASSUMPTION standing in for a first-response target, not a regulatory
# citation. Complaint deadlines differ by product, member state and the firm's own policy —
# a final-response deadline is commonly far longer — and the number the firm actually works
# to is established in Phase 0. One constant, so changing it changes everything.
#
# Note when reading the demo: this batch is a HISTORICAL sample spanning 53 days of intake,
# so a large share of it reads as breached. That is a property of the sample, not of any
# firm's performance, and the page says so rather than letting the number alarm anyone.
SLA_DAYS = 15
DUE_SOON_DAYS = 5

BREACHED, DUE_SOON, ON_TRACK = "breached", "due soon", "on track"


def as_at(items: list[dict], date_key: str) -> str:
    """The queue's reference date: the most recent item in it.

    Deliberately NOT today's date. The corpus is a fixed historical batch, so measuring
    against today would show every complaint as months overdue and make the whole column
    meaningless. Measuring against the batch's own newest item gives the ages a live queue
    would have, and the page says which date it is working from rather than implying it is
    now.
    """
    dates = [i.get(date_key) for i in items if i.get(date_key)]
    return max(dates) if dates else ""


def _days(a: str, b: str) -> int:
    from datetime import date
    ya, ma, da = (int(x) for x in a.split("-"))
    yb, mb, db = (int(x) for x in b.split("-"))
    return (date(ya, ma, da) - date(yb, mb, db)).days


def clock(item_date: str, reference: str) -> dict:
    """Age, days remaining and SLA state for one item."""
    if not item_date or not reference:
        return {"age_days": None, "days_left": None, "sla": ""}
    age = _days(reference, item_date)
    left = SLA_DAYS - age
    state = BREACHED if left < 0 else (DUE_SOON if left <= DUE_SOON_DAYS else ON_TRACK)
    return {"age_days": age, "days_left": left, "sla": state}


def with_clock(items: list[dict], date_key: str) -> tuple[list[dict], str]:
    """Attach the clock to every item. Returns the items and the reference date used."""
    ref = as_at(items, date_key)
    return [{**i, **clock(i.get(date_key, ""), ref)} for i in items], ref


# ------------------------------------------------------------------------------- weeks
# Chleo opens this weekly, so "is this a normal week" is the question her whole cadence
# rests on — and it needs a last week to compare against. The batch carries nine distinct
# ISO weeks of real receipt dates, so this is measured, not synthesised. What a fixed batch
# genuinely cannot show is NEW work arriving; comparing the weeks it already contains is
# honest.
def iso_week(date_str: str) -> str:
    from datetime import date
    y, m, d = (int(x) for x in date_str.split("-"))
    iy, iw, _ = date(y, m, d).isocalendar()
    return f"{iy}-W{iw:02d}"


def by_week(items: list[dict], date_key: str) -> list[dict]:
    """Per-week counts, oldest first: volume, held, and how many a person has decided."""
    latest = latest_by_item()
    buckets: dict[str, dict] = {}
    for it in items:
        if not it.get(date_key):
            continue
        w = buckets.setdefault(iso_week(it[date_key]),
                               {"week": iso_week(it[date_key]), "items": 0, "held": 0,
                                "agreed": 0, "disagreed": 0, "decided": 0})
        w["items"] += 1
        if it.get("decision") != "PROPOSE_TO_HANDLER":
            w["held"] += 1
        s = status_of(it["item_id"], it, latest)
        if s not in PENDING_STATUSES:
            w["decided"] += 1
            if s in DISAGREEMENTS:
                w["disagreed"] += 1
            elif s in ("accepted", "escalated"):
                w["agreed"] += 1
    rows = sorted(buckets.values(), key=lambda r: r["week"])
    for r in rows:
        r["held_pct"] = 100 * r["held"] / r["items"] if r["items"] else 0.0
        r["agreement_pct"] = (100 * r["agreed"] / (r["agreed"] + r["disagreed"])
                              if (r["agreed"] + r["disagreed"]) else None)
    return rows


def week_on_week(rows: list[dict]) -> dict:
    """The last complete week against the one before it. None when there is no comparison."""
    if len(rows) < 2:
        return {}
    cur, prev = rows[-1], rows[-2]
    return {"current": cur, "previous": prev,
            "items_delta": cur["items"] - prev["items"],
            "held_pct_delta": cur["held_pct"] - prev["held_pct"]}


# ------------------------------------------------------------------------ on/off switches
# Chleo asked for this directly: she wants to disable a capability on a Monday morning
# without phoning a consultant. It lives in a file rather than in code precisely so that
# turning something off is an operational act, not a deployment.
CAPABILITIES = {
    "triage": "Complaint triage",
    "anomaly": "Anomaly review",
    "reporting": "Reporting assistance",
}


def settings() -> dict:
    s = _read(SETTINGS_FILE, {})
    return {k: bool(s.get(k, True)) for k in CAPABILITIES}     # on unless switched off


def is_on(capability: str) -> bool:
    return settings().get(capability, True)


def set_capability(capability: str, on: bool, *, by: str) -> None:
    """Switch one capability on or off, and record it — turning a capability off is a
    decision about the system and belongs in the same log as decisions about cases."""
    with _lock:
        s = _read(SETTINGS_FILE, {})
        s[capability] = bool(on)
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(s, indent=2, sort_keys=True))
    record(f"capability:{capability}", "switched_on" if on else "switched_off",
           capability=capability, by=by,
           proposed=f"{CAPABILITIES.get(capability, capability)} "
                    f"{'enabled' if on else 'disabled'}")


# ------------------------------------------------------------- supervision breakdowns
def by_proposed_team(items: list[dict]) -> list[dict]:
    """Where the model is overridden, grouped by the team it proposed (O2).

    The ops lead's question is not "how often is it wrong" but "wrong about what". A team
    with a high override rate is either a team the model confuses or a taxonomy that needs
    fixing — and those need different responses.
    """
    latest = latest_by_item()
    rows: dict[str, dict] = {}
    for it in items:
        team = it.get("proposed_team") or "—"
        r = rows.setdefault(team, {"team": team, "items": 0, "decided": 0,
                                   "agreed": 0, "overridden": 0, "sent_instead": {}})
        r["items"] += 1
        e = latest.get(it["item_id"])
        if not e:
            continue
        r["decided"] += 1
        if e["action"] in DISAGREEMENTS:
            r["overridden"] += 1
            d = e.get("destination")
            if d:
                r["sent_instead"][d] = r["sent_instead"].get(d, 0) + 1
        elif e["action"] in ("accepted", "escalated"):
            r["agreed"] += 1
    out = []
    for r in rows.values():
        r["override_pct"] = (100 * r["overridden"] / r["decided"]) if r["decided"] else None
        r["sent_instead"] = ", ".join(f"{k} ×{v}" for k, v in
                                      sorted(r["sent_instead"].items(), key=lambda kv: -kv[1]))
        out.append(r)
    return sorted(out, key=lambda r: -r["items"])


def by_handler() -> list[dict]:
    """Acceptance per person (O3).

    Risk R2 is automation bias, rated 4 x 4, and its stated mitigation is "measured per
    handler". Until this existed the register promised a control that did not exist, which
    is worse than not claiming it. A rate near 100% is a warning, not a success.
    """
    rows: dict[str, dict] = {}
    for e in events():
        if e["action"] in ("switched_on", "switched_off"):
            continue
        r = rows.setdefault(e["by"], {"handler": e["by"], "decisions": 0,
                                      "agreed": 0, "overridden": 0})
        r["decisions"] += 1
        if e["action"] in DISAGREEMENTS:
            r["overridden"] += 1
        elif e["action"] in ("accepted", "escalated"):
            r["agreed"] += 1
    out = []
    for r in rows.values():
        d = r["agreed"] + r["overridden"]
        r["acceptance_pct"] = (100 * r["agreed"] / d) if d else None
        r["flag"] = ("rubber-stamping?" if r["acceptance_pct"] is not None
                     and d >= 10 and r["acceptance_pct"] > 97 else "")
        out.append(r)
    return sorted(out, key=lambda r: -r["decisions"])


def outstanding_by_team(items: list[dict]) -> list[dict]:
    """What is still waiting, per proposed team (O4) — so the day can be balanced."""
    latest = latest_by_item()
    rows: dict[str, dict] = {}
    for it in items:
        s = status_of(it["item_id"], it, latest)
        if s not in PENDING_STATUSES:
            continue
        team = it.get("proposed_team") or "—"
        r = rows.setdefault(team, {"team": team, "waiting": 0, "past_target": 0})
        r["waiting"] += 1
        if it.get("sla") == BREACHED:
            r["past_target"] += 1
    return sorted(rows.values(), key=lambda r: (-r["past_target"], -r["waiting"]))
