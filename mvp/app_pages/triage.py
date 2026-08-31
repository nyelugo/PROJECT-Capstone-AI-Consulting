"""UC-1 — route one complaint, grounded in a verbatim quote."""
import streamlit as st

import prompt as P                                   # path set up by mvp.capabilities
from mvp.capabilities.triage import Triage
from mvp.ui import fire, show, model_ready

st.title("Triage a complaint")
st.caption("It proposes a routing queue, and must quote the sentence that drove the "
           "decision. A guard checks that sentence is really in the complaint.")

products = sorted(P.PRODUCT_QUEUES)
with st.form("triage"):
    c1, c2 = st.columns([2, 1])
    product = c1.selectbox("Product", products,
                           index=products.index("Credit card") if "Credit card" in products else 0)
    cid = c2.text_input("Complaint reference", "C-100482",
                        help="Pseudonymised before anything is stored or traced.")
    narrative = st.text_area(
        "What the customer wrote", height=150,
        value=("I was charged twice for the same purchase on my credit card statement and "
               "the bank has not refunded the duplicate charge after three phone calls."))
    go = st.form_submit_button("Triage", type="primary", disabled=not model_ready(),
                               icon=":material/alt_route:")

if go:
    fire(Triage(), {"complaint_id": cid, "product": product, "narrative": narrative}, "triage")

show("triage", accept_label="Send to that team", review_label="Send to a person instead")
