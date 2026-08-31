"""Assist — the MVP. One decision spine, three capabilities, a person in every loop.

Run:  streamlit run mvp/app.py

What this is beyond the POC. The n8n POC proved a complaint could be classified and routed
with a reason. This is the same decision spine wired to three capabilities, with the part
the POC could only imply made explicit: the **human confirmation step**. Nothing here acts.
Every capability ends with a proposal on screen and a person clicking, and what the person
clicked is recorded next to what the system proposed — which is the record that makes the
whole thing auditable, and the thing a workflow diagram cannot show you.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mvp import runtime as R                                    # noqa: E402
from mvp.spine import run, STAGES, PROPOSE                      # noqa: E402
from mvp.capabilities.triage import Triage                      # noqa: E402
from mvp.capabilities.reporting import Reporting, SECTIONS      # noqa: E402
from mvp.capabilities.anomaly import Anomaly, detect, RULES     # noqa: E402

BLUE, AMBER, RED, GREY = "#2a78d6", "#d99000", "#c0392b", "#8a8f98"

st.set_page_config(page_title="Assist", page_icon="🛡", layout="wide")
st.markdown("""<style>
  .stApp {background:#fbfbfd}
  div[data-testid="stMetricValue"] {font-size:1.6rem}
  .lad {font-family:ui-monospace,Menlo,monospace;font-size:.82rem;line-height:1.7}
  .pill {display:inline-block;padding:.12rem .5rem;border-radius:.7rem;font-size:.72rem;
         font-weight:600;letter-spacing:.02em}
</style>""", unsafe_allow_html=True)

# Streamlit reruns this whole script on every click, so a decision that exists only
# inside an `if st.button(...)` branch is gone by the time the user acts on it — and the
# human-confirmation click lands on a widget that no longer exists and is silently
# discarded. The decision is therefore held in session state and rendered unconditionally.
# The human step is the point of this application; it cannot be the fragile part.
for _k, _v in (("log", []), ("last", {}), ("traced", {}), ("recorded", set())):
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ------------------------------------------------------------------ shared presentation

def ladder(d) -> str:
    """The guard ladder, showing exactly how far the proposal got.

    This is the transparency claim made literal. Chleo's objection was that you cannot see
    what the AI does; this shows every check it passed and the one it did not, by name.
    """
    stop = d.failed_stage
    out = []
    for s in STAGES:
        if stop is None:
            out.append(f"<span style='color:{BLUE}'>&#10003;</span> {s}")
        elif s == stop:
            out.append(f"<span style='color:{RED}'>&#10007;</span> <b>{s}</b> — {d.reason_code}")
            break
        else:
            out.append(f"<span style='color:{BLUE}'>&#10003;</span> {s}")
    return "<div class='lad'>" + "<br>".join(out) + "</div>"


def render(d, key: str, *, accept_label: str, review_label: str):
    """One renderer for all three capabilities — the shared spine, made visible."""
    proposed = d.decision == PROPOSE
    colour = BLUE if proposed else AMBER
    label = "PROPOSED" if proposed else "HELD FOR A PERSON"
    left, right = st.columns([3, 2])

    with left:
        st.markdown(
            f"<span class='pill' style='background:{colour}1a;color:{colour}'>{label}</span>"
            f"<span class='pill' style='background:#eee;color:{GREY}'>{d.reason_code}</span>",
            unsafe_allow_html=True)
        st.markdown(f"### {d.summary}")
        st.caption(d.reason)

        if d.capability == "triage" and d.payload.get("evidence"):
            st.markdown("**Because the customer wrote:**")
            st.info(f"“{d.payload['evidence']}”")
        if d.capability == "reporting" and d.payload.get("narrative"):
            st.markdown("**Draft:**")
            st.success(d.payload["narrative"])
        if d.capability == "anomaly" and d.payload.get("explanation"):
            st.markdown("**Case note:**")
            st.info(d.payload["explanation"])
            if d.payload.get("next_check"):
                st.markdown(f"**Fastest check:** {d.payload['next_check']}")
        if d.grounding_detail:
            st.caption(f"Grounding check — {d.grounding_detail}")

    with right:
        st.markdown("**Checks**")
        st.markdown(ladder(d), unsafe_allow_html=True)
        c = f"{d.confidence:.2f}" if isinstance(d.confidence, (int, float)) else "—"
        st.caption(f"confidence {c} · {d.latency_ms} ms · {d.model} · ref {d.ref}")

    if key in st.session_state.recorded:
        st.success("Recorded in the decision log. Nothing else happens automatically.")
        return
    st.markdown("**A person decides. Nothing has happened yet.**")
    a, b, _ = st.columns([1, 1, 3])
    if a.button(accept_label, key=f"acc_{key}", type="primary", disabled=not proposed):
        _record(d, key, "accepted by handler")
    if b.button(review_label, key=f"rev_{key}"):
        _record(d, key, "overridden — sent to review")


def _record(d, key: str, action: str):
    st.session_state.recorded.add(key)
    st.session_state.log.insert(0, {
        "at": datetime.now().strftime("%H:%M:%S"),
        "capability": d.capability, "proposed": d.summary,
        "reason_code": d.reason_code, "human": action,
        "confidence": d.confidence, "ref": d.ref,
    })
    st.toast(f"Recorded: {action}")
    st.rerun()


def fire(cap, request, slot: str):
    """Run one capability and keep the result. Any failure is a Decision, never a crash."""
    with st.spinner("Working…"):
        d = run(cap, request, call=R.call_model)
        st.session_state.traced[slot] = R.trace(d, {"capability": cap.name})
    st.session_state.last[slot] = d
    st.session_state.recorded.discard(slot)      # a new proposal needs a new human action


def show(slot: str, **kw):
    d = st.session_state.last.get(slot)
    if d is None:
        return
    render(d, slot, **kw)
    if not st.session_state.traced.get(slot, False):
        st.caption("Not traced to monitoring — LANGSMITH_API_KEY is not configured.")


# --------------------------------------------------------------------------- the sidebar

with st.sidebar:
    st.markdown("### Assist")
    st.caption("Proposes. Never decides.")
    st.divider()
    st.markdown("**System**")
    ok_model = R.env("OPENAI_API_KEY") is not None
    st.markdown(f"{'🟢' if ok_model else '🔴'} model key {R.key_fingerprint('OPENAI_API_KEY')}")
    st.markdown(f"{'🟢' if R.env('LANGSMITH_API_KEY') else '🟠'} monitoring "
                f"{R.key_fingerprint('LANGSMITH_API_KEY')}")
    if not ok_model:
        st.error("Add OPENAI_API_KEY to ~/.config/ironhack/.env.local, then reload.")
    st.divider()
    st.caption("Every capability runs the same six checks. What differs is only what "
               "counts as evidence.")

st.title("Assist")
st.caption("Three decisions a complaints operation makes every day — each one proposed "
           "with its reason, each one confirmed by a person.")

t1, t2, t3, t4 = st.tabs(["Triage a complaint", "Draft a report section",
                          "Review a flagged pattern", "Decision log"])

# ------------------------------------------------------------------------------ triage
with t1:
    import prompt as P
    st.markdown("**UC-1** · proposes a routing queue, grounded in a **verbatim quote** "
                "from the complaint.")
    products = sorted(P.PRODUCT_QUEUES)
    col1, col2 = st.columns([1, 2])
    product = col1.selectbox("Product", products, index=products.index("Credit card")
                             if "Credit card" in products else 0)
    cid = col2.text_input("Complaint reference", "C-100482",
                          help="Pseudonymised before anything is stored or traced.")
    narrative = st.text_area(
        "What the customer wrote", height=150,
        value=("I was charged twice for the same purchase on my credit card statement and "
               "the bank has not refunded the duplicate charge after three phone calls."))
    if st.button("Triage", type="primary", disabled=not ok_model):
        fire(Triage(), {"complaint_id": cid, "product": product, "narrative": narrative},
             "triage")
    show("triage", accept_label="Send to that team",
         review_label="Send to a human instead")

# --------------------------------------------------------------------------- reporting
with t2:
    st.markdown("**UC-3** · drafts report prose, grounded in **figures this system "
                "computed**. Any number it invents is caught before you read it.")
    col1, col2 = st.columns(2)
    section = col1.selectbox("Section", list(SECTIONS))
    audience = col2.text_input("Audience", "the board risk committee")
    st.caption(f"Covers: {SECTIONS[section]['brief']}")
    if st.button("Draft it", type="primary", disabled=not ok_model):
        fire(Reporting(), {"section": section, "audience": audience}, "report")
    show("report", accept_label="Accept into the report",
         review_label="Reject the draft")

# ----------------------------------------------------------------------------- anomaly
with t3:
    st.markdown("**UC-2** · a deterministic detector selects; the model only **explains**. "
                "Ranked by departure from each account's own normal — never by amount.")
    cands = detect()
    labels = [f"{c['candidate_id']} · {c['rule'].replace('_',' ')} · "
              f"{c['times_normal']}x normal · {c['txn_count']} txn · EUR {c['amount_eur']:,.2f}"
              for c in cands]
    pick = st.selectbox(f"Candidates raised on the batch ({len(cands)})", range(len(cands)),
                        format_func=lambda i: labels[i])
    c = cands[pick]
    st.caption(f"Rule: **{c['rule']}** — {RULES[c['rule']]} · {c['date']} · "
               f"{c['category']} · {c['channel']} · {c['country']}")
    if st.button("Explain this flag", type="primary", disabled=not ok_model):
        fire(Anomaly(), {"candidate": c}, "anomaly")
    show("anomaly", accept_label="Escalate to an analyst", review_label="Dismiss")

# --------------------------------------------------------------------------------- log
with t4:
    st.markdown("**What the system proposed, and what the person did about it.** "
                "This pairing is the audit record — a proposal with no human action beside "
                "it is an incomplete record, not a decision.")
    if not st.session_state.log:
        st.info("Nothing yet. Run something on one of the other tabs.")
    else:
        import pandas as pd
        df = pd.DataFrame(st.session_state.log)
        st.dataframe(df, width="stretch", hide_index=True)
        agreed = sum(1 for r in st.session_state.log if r["human"].startswith("accepted"))
        m1, m2, m3 = st.columns(3)
        m1.metric("Decisions recorded", len(df))
        m2.metric("Accepted by the handler", agreed)
        m3.metric("Overridden", len(df) - agreed)
        st.caption("In production this is the number that matters: not whether the model "
                   "was right, but how often a handler agreed with it.")
