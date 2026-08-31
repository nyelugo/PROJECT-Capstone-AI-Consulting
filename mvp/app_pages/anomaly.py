"""UC-2 — explain a flagged transaction pattern, grounded in the record's own values."""
import streamlit as st

from mvp.capabilities.anomaly import Anomaly, detect, RULES
from mvp.ui import fire, show, model_ready

st.title("Review a flagged pattern")
st.caption("A deterministic detector selects; the model only explains. Ranked by how far "
           "a pattern departs from that account's own normal — never by the amount.")

cands = detect()
labels = [f"{c['candidate_id']} · {c['rule'].replace('_', ' ')} · {c['times_normal']}x normal "
          f"· {c['txn_count']} txn · €{c['amount_eur']:,.2f}" for c in cands]
pick = st.selectbox(f"Candidates raised on this batch ({len(cands)})", range(len(cands)),
                    format_func=lambda i: labels[i])
c = cands[pick]

with st.container(border=True):
    st.markdown(f"**{c['rule'].replace('_', ' ').capitalize()}** — {RULES[c['rule']]}")
    m = st.columns(4)
    m[0].metric("Transactions", c["txn_count"])
    m[1].metric("Total", f"€{c['amount_eur']:,.0f}")
    m[2].metric("This account's median", f"€{c['account_median_eur']:,.0f}")
    m[3].metric("Times normal", f"{c['times_normal']}x")
    st.caption(f"{c['date']} · {c['category']} · {c['channel']} · {c['country']}")

if st.button("Explain this flag", type="primary", disabled=not model_ready(),
             icon=":material/travel_explore:"):
    fire(Anomaly(), {"candidate": c}, "anomaly")

show("anomaly", accept_label="Escalate to an analyst", review_label="Dismiss")
