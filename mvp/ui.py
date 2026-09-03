"""Shared presentation of a Decision — one renderer for all three capabilities.

Every capability page calls the same three functions, so a proposal cannot look one way in
triage and another in anomaly flagging. The architecture claim the Round 2 deck makes —
one decision spine — is only credible if the interface reflects it.

Streamlit reruns the whole script on every click, so a Decision that exists only inside an
`if st.button(...)` branch is gone by the time the user acts on it, and the human
confirmation click lands on a widget that no longer exists and is silently discarded. The
Decision is therefore held in session state and rendered unconditionally. The human step is
the point of this application; it cannot be the fragile part.
"""
from __future__ import annotations

import copy

from datetime import datetime

import streamlit as st

from . import runtime as R
from .spine import run, STAGES, PROPOSE

BLUE, AMBER, RED, GREY = "#2a78d6", "#d99000", "#c0392b", "#8a8f98"

STATE_DEFAULTS = {"log": [], "last": {}, "traced": {}, "recorded": set()}


def init_state() -> None:
    # copy, or every session shares the one module-level list/dict/set by reference
    for k, v in STATE_DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = copy.deepcopy(v)


def _ladder(d) -> str:
    """The guard ladder — every check it passed, and the one it did not, by name.

    This is the transparency claim made literal. Chleo's objection was that she cannot see
    what the AI does; this shows the checks, not a confidence score.
    """
    out, stop = [], d.failed_stage
    for s in STAGES:
        if stop is not None and s == stop:
            out.append(f"<span style='color:{RED}'>&#10007;</span> <b>{s}</b> — {d.reason_code}")
            break
        out.append(f"<span style='color:{BLUE}'>&#10003;</span> {s}")
    return ("<div style='font-family:ui-monospace,Menlo,monospace;font-size:.82rem;"
            "line-height:1.7'>" + "<br>".join(out) + "</div>")


def _record(d, key: str, action: str) -> None:
    st.session_state.recorded.add(key)
    st.session_state.log.insert(0, {
        "at": datetime.now().strftime("%H:%M:%S"),
        "capability": d.capability, "proposed": d.summary,
        "reason_code": d.reason_code, "human": action,
        "confidence": d.confidence, "ref": d.ref,
    })
    st.toast(f"Recorded: {action}")
    st.rerun()


def render(d, key: str, *, accept_label: str, review_label: str) -> None:
    proposed = d.decision == PROPOSE
    colour = BLUE if proposed else AMBER
    label = "Proposed" if proposed else "Held for a person"

    left, right = st.columns([3, 2])
    with left:
        st.markdown(f":{'blue' if proposed else 'orange'}-badge[{label}] "
                    f"{reason_chip(d.reason_code)}")
        st.subheader(d.summary)
        st.caption(d.reason)

        if d.capability == "triage" and d.payload.get("evidence"):
            st.markdown("**Because the customer wrote:**")
            st.info(f"“{d.payload['evidence']}”")
        elif d.capability == "reporting" and d.payload.get("narrative"):
            st.markdown("**Draft:**")
            st.success(d.payload["narrative"])
        elif d.capability == "anomaly" and d.payload.get("explanation"):
            st.markdown("**Case note:**")
            st.info(d.payload["explanation"])
            if d.payload.get("next_check"):
                st.markdown(f"**Fastest check:** {d.payload['next_check']}")
        if d.grounding_detail:
            st.caption(f"Grounding check — {d.grounding_detail}")

    with right:
        with st.container(border=True):
            st.markdown("**Checks**")
            st.html(_ladder(d))
            c = conf_txt(d.confidence)
            st.caption(f"confidence {c} · {d.latency_ms} ms · {d.model} · ref {d.ref}")

    if key in st.session_state.recorded:
        st.success("Recorded in the decision log. Nothing else happens automatically.")
        return

    st.markdown("**A person decides. Nothing has happened yet.**")
    with st.container(horizontal=True):
        if st.button(accept_label, key=f"acc_{key}", type="primary", disabled=not proposed,
                     icon=":material/check:"):
            _record(d, key, "accepted by handler")
        if st.button(review_label, key=f"rev_{key}", icon=":material/person_raised_hand:"):
            _record(d, key, "overridden — sent to review")


def fire(cap, request: dict, slot: str) -> None:
    """Run one capability and keep the result. Any failure is a Decision, never a crash."""
    with st.spinner("Working…"):
        d = run(cap, request, call=R.call_model)
        st.session_state.traced[slot] = R.trace(d, {"capability": cap.name})
    st.session_state.last[slot] = d
    st.session_state.recorded.discard(slot)      # a new proposal needs a new human action


def show(slot: str, **kw) -> None:
    d = st.session_state.last.get(slot)
    if d is None:
        return
    render(d, slot, **kw)
    if not st.session_state.traced.get(slot, False):
        st.caption("Not traced to monitoring — LANGSMITH_API_KEY is not configured.")


def model_ready() -> bool:
    return R.env("OPENAI_API_KEY") is not None


# ---------------------------------------------------------------- queue presentation
# The two queues are the same page shape — a ranked list with a pre-written justification
# and a disposition — so they share these helpers rather than each growing its own.

import pandas as pd                                                    # noqa: E402

from . import queue_store as Q                                         # noqa: E402
from .spine import STAGE_OF                                            # noqa: E402

STATUS_COLOUR = {
    "held": "orange", "proposed": "blue",
    "accepted": "green", "escalated": "green",
    "rerouted": "red", "dismissed": "red", "more_info": "violet",
}
STATUS_LABEL = {
    "held": "Held for a person", "proposed": "Proposed",
    "accepted": "Accepted", "rerouted": "Rerouted", "escalated": "Escalated",
    "dismissed": "Dismissed", "more_info": "Needs more",
}


# The raw code belongs in the Checks panel beside the ladder, not in a badge on a queue row.
# A handler needs to know what was wrong, not what the constant is called.
REASON_LABEL = {
    "OK_PROPOSED": "",
    "REJECT_INVALID_INPUT": "Input rejected",
    "ERROR_MODEL_CALL": "Model call failed",
    "REJECT_MALFORMED_OUTPUT": "Unreadable reply",
    "REJECT_QUEUE_NOT_IN_PRODUCT": "Queue not on this product",
    "REJECT_OUT_OF_TAXONOMY": "No queue fits",
    "REJECT_METRIC_NOT_PUBLISHED": "Metric not published",
    "REJECT_ACCOUNT_NOT_IN_LEDGER": "Not in this batch",
    "REJECT_LOW_CONFIDENCE": "Below the confidence threshold",
    "REJECT_EVIDENCE_NOT_VERBATIM": "Quote not found in the complaint",
    "REJECT_FIGURE_NOT_COMPUTED": "Figure not computed from the data",
    "REJECT_VALUE_MISMATCH": "Value does not match the record",
}


def reason_chip(code: str) -> str:
    """A plain-English badge, or nothing when the proposal passed."""
    label = REASON_LABEL.get(code, code)
    return f" :gray-badge[{label}]" if label else ""


MAX_OPERATOR_CHARS = 40
MAX_NOTE_CHARS = 200


def current_operator() -> str:
    """Who is acting, normalised. Never blank: an audit row that cannot say who decided is
    not an audit row, and the field is a free-text box that can be emptied."""
    name = " ".join(str(st.session_state.get("operator", "")).split())[:MAX_OPERATOR_CHARS]
    return name or "unknown"


def conf_txt(v) -> str:
    """Render a confidence, or an em dash when there isn't one.

    `confidence` is None whenever the model returned malformed JSON — which is exactly the
    case the Checks panel exists to display. Formatting None with :.2f raises TypeError, so
    the page would crash precisely when it had something important to say.
    """
    return f"{v:.0%}" if isinstance(v, (int, float)) and v == v else "—"


@st.cache_data(show_spinner=False)
def team_names() -> list[str]:
    """The teams a handler can reroute to — the same seven the classifier maps onto, read
    from `classifier/teams.py` rather than retyped, so a correction cannot name a team the
    system does not have."""
    from .capabilities import _shared  # noqa: F401  (path setup)
    import teams as T
    return [t for t in T.TEAMS]


def status_chip(status: str) -> str:
    return (f":{STATUS_COLOUR.get(status, 'gray')}-badge"
            f"[{STATUS_LABEL.get(status, status)}]")


def ladder_html(reason_code: str) -> str:
    """The guard ladder for a stored reason code — the same display a live run gets."""
    stop = STAGE_OF.get(reason_code)
    out = []
    for s in STAGES:
        if stop is not None and s == stop:
            out.append(f"<span style='color:{RED}'>&#10007;</span> <b>{s}</b> — {reason_code}")
            break
        out.append(f"<span style='color:{BLUE}'>&#10003;</span> {s}")
    return ("<div style='font-family:ui-monospace,Menlo,monospace;font-size:.82rem;"
            "line-height:1.7'>" + "<br>".join(out) + "</div>")


SLA_LABEL = {"breached": "Past target", "due soon": "Due soon", "on track": "On track"}

CAPABILITY_LABEL = {"triage": "Complaint triage", "anomaly": "Anomaly review",
                    "reporting": "Reporting assistance"}


def action_label(a: str) -> str:
    """What a person did, in their words. Falls back to the constant made readable."""
    return STATUS_LABEL.get(a, str(a).replace("_", " ").capitalize())

# Facets filter on the stored value but must not show it. "breached" is the system's word;
# the queue above it says "Past target" and so does the badge on the case.
FACET_LABEL = {"sla": SLA_LABEL}


def queue_filters(df: pd.DataFrame, *, extra_facets=(), date_col: str = "received"):
    """Status, facets and free text. Returns the filtered frame.

    Defaults to what needs a person. Handled items are one click away, never hidden —
    an inbox that empties tells you nothing about what was decided this morning.
    """
    present = [s for s in ["held", "proposed", "accepted", "rerouted", "escalated",
                           "dismissed", "more_info"] if s in set(df["status"])]
    with st.container(border=True):
        c = st.columns([2, 1] + [1] * len(extra_facets) + [1.4])
        show = c[0].segmented_control(
            "Show", ["Needs you", "Handled", "Disagreements", "All"],
            default="Needs you", key=f"show_{date_col}")
        statuses = c[1].multiselect("Status", present, default=[],
                                    key=f"st_{date_col}",
                                    format_func=lambda v: STATUS_LABEL.get(v, v),
                                    help="Leave empty to use the Show setting")
        picked = {}
        for i, (col, label) in enumerate(extra_facets):
            opts = sorted(x for x in df[col].dropna().unique() if str(x).strip())
            fmt = FACET_LABEL.get(col, {})
            picked[col] = c[2 + i].multiselect(label, opts, default=[],
                                               key=f"f_{col}_{date_col}",
                                               format_func=lambda v: fmt.get(v, v))
        term = c[-1].text_input("Search", "", key=f"q_{date_col}",
                                placeholder="text in this row")

    out = df
    if statuses:
        out = out[out["status"].isin(statuses)]
    elif show == "Needs you":
        out = out[out["status"].isin(Q.PENDING_STATUSES)]
    elif show == "Handled":
        out = out[~out["status"].isin(Q.PENDING_STATUSES)]
    elif show == "Disagreements":
        out = out[out["status"].isin(Q.DISAGREEMENTS)]

    for col, vals in picked.items():
        if vals:
            out = out[out[col].isin(vals)]
    if term:
        hay = out.astype(str).agg(" ".join, axis=1).str.lower()
        out = out[hay.str.contains(term.lower(), regex=False)]

    # Pending first, then newest. Column headers still sort natively on top of this.
    out = out.assign(_p=~out["status"].isin(Q.PENDING_STATUSES))
    return out.sort_values(["_p", date_col], ascending=[True, False]).drop(columns="_p")


def action_bar(item: dict, *, capability: str, actions: dict, proposed: str = "") -> None:
    """The human step. Shows any decision already taken, and allows a new one.

    Re-deciding appends rather than overwrites: the queue shows the latest, the log keeps
    both. A past decision is a record of what was decided at the time, and editing it away
    destroys the audit value that justifies keeping it.
    """
    prior = Q.latest_by_item().get(item["item_id"])
    if prior:
        extra = ""
        if prior.get("destination"):
            extra += f" → **{prior['destination']}**"
        if prior.get("note"):
            extra += f" — {prior['note']}"
        st.success(f"**{STATUS_LABEL.get(prior['action'], prior['action'])}** "
                   f"by {prior['by']} at {prior['at'].replace('T', ' ')}{extra}")

    st.markdown("**Nothing has happened yet. A person decides.**"
                if not prior else "**Change the decision?** The original stays in the log.")

    # A correction that does not say WHERE it should have gone is the most expensive
    # omission in this system: it records that the model was wrong without recording HOW,
    # which is the only version of the fact that can improve anything.
    dest, note = "", ""
    if actions.keys() & Q.NEEDS_DESTINATION:
        a, b = st.columns([2, 3])
        dest = a.selectbox("If rerouting, the right team is",
                           team_names(), key=f"dest_{capability}_{item['item_id']}")
        note = b.text_input("Note (optional)", key=f"note_{capability}_{item['item_id']}",
                            max_chars=MAX_NOTE_CHARS,
                            placeholder="why the proposal was wrong")

    with st.container(horizontal=True):
        for action, label in actions.items():
            if st.button(label, key=f"{capability}_{item['item_id']}_{action}",
                         type="primary" if action in ("accepted", "escalated") else "secondary"):
                Q.record(item["item_id"], action, capability=capability,
                         by=current_operator(),
                         proposed=proposed, reason_code=item.get("reason_code", ""),
                         note=note,
                         destination=dest if action in Q.NEEDS_DESTINATION else "")
                st.rerun()


def bulk_bar(rows: "pd.DataFrame", *, capability: str, actions: dict) -> None:
    """Act on several items at once.

    This exists because of risk R2. A handler forced to click through twenty confident
    proposals one at a time learns to click without reading, which is precisely the
    automation bias the whole design is meant to avoid. Better to let them clear the
    obvious ones deliberately, in one action they can see the size of, than to make
    inattention the path of least resistance.
    """
    st.divider()
    pending = rows[rows["status"].isin(Q.PENDING_STATUSES)]
    st.subheader(f"{len(rows)} items selected")
    if len(pending) < len(rows):
        st.caption(f"{len(rows) - len(pending)} of them already have a decision. "
                   "Acting again appends a new one; the original stays in the log.")

    counts = rows["status"].value_counts().to_dict()
    st.markdown(" ".join(f"{status_chip(s)} ×{n}" for s, n in counts.items()))

    st.markdown("**Nothing has happened yet. A person decides.**")
    # A reroute has to say WHERE, and one bulk button cannot. Offering it here recorded a
    # blank destination — the omission queue_store calls the most expensive in this system.
    actions = {a: l for a, l in actions.items() if a not in Q.NEEDS_DESTINATION}
    with st.container(horizontal=True):
        for action, label in actions.items():
            if st.button(f"{label} — all {len(rows)}", key=f"bulk_{capability}_{action}"):
                for _, r in rows.iterrows():
                    Q.record(r["item_id"], action, capability=capability,
                             by=current_operator(),
                             proposed=str(r.get("proposed_team") or r.get("rule", "")),
                             reason_code=r.get("reason_code", ""),
                             note=f"bulk action over {len(rows)} items")
                st.rerun()


SLA_COLOUR = {"breached": "red", "due soon": "orange", "on track": "green"}


def sla_chip(state: str, days_left) -> str:
    """Deadline state as a badge. Empty when there is no target for this item type."""
    if not state:
        return ""
    if state == "breached":
        return f":red-badge[{abs(int(days_left))}d past target]"
    return f":{SLA_COLOUR.get(state, 'gray')}-badge[{int(days_left)}d left]"
