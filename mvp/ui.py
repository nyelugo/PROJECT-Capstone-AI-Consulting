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

from datetime import datetime

import streamlit as st

from . import runtime as R
from .spine import run, STAGES, PROPOSE

BLUE, AMBER, RED, GREY = "#2a78d6", "#d99000", "#c0392b", "#8a8f98"

STATE_DEFAULTS = {"log": [], "last": {}, "traced": {}, "recorded": set()}


def init_state() -> None:
    for k, v in STATE_DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


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
                    f":gray-badge[{d.reason_code}]")
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
            c = f"{d.confidence:.2f}" if isinstance(d.confidence, (int, float)) else "—"
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
