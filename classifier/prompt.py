"""The complaint triage prompt — single source of truth.

The n8n POC (`n8n/build_workflow.py` embeds these strings) and the Round 2 MVP both read
from here, so the demo and the product cannot drift apart.

Design notes, which carry as much of the pitch as the accuracy does:

* **The classifier is product-conditioned.** A complaint always arrives attached to a
  product, and the issue taxonomy is product-scoped: 'Managing an account' exists only
  under checking/savings, 'Problem with a purchase shown on your statement' only under
  credit card. Asking a model to pick from all 64 issues without the product is not a
  hard problem, it is an ill-posed one. It gets the product, and only that product's
  queues.
* **It must quote the sentence that drove its decision**, verbatim. An unexplained label
  is exactly the opacity Chleo objects to.
* **It must return a confidence, and below THRESHOLD the complaint goes to a human.**
  Abstention is a correct answer, not a failure. So is OTHER.
"""
import json
from pathlib import Path

_TAX = json.loads((Path(__file__).parent / "taxonomy.json").read_text())

PRODUCT_QUEUES: dict[str, list[str]] = _TAX["products"]
CONFIDENCE_THRESHOLD = 0.70
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are a complaint triage assistant at a retail bank. You do not \
resolve complaints, decide outcomes, or contact customers. You read one complaint that \
has already arrived on a known product, and choose which of that product's queues should \
handle it.

You will be given the product and the exact list of queues available for it. Choose \
exactly one queue from that list, copied verbatim.

Rules:
- Choose only from the list you are given. Queues for other products do not apply.
- Prefer a named queue. Almost every real complaint belongs to one of them. Choose \
"OTHER" only when no queue on the list is even plausibly related to what the customer \
is describing — not merely because the fit is imperfect.
- When two queues could both fit, choose the more specific one and lower your confidence \
to reflect the ambiguity. Do not retreat to "OTHER" because two options overlap.
- Give a confidence between 0 and 1 reflecting how certain you are. Be honest — this is \
how uncertainty is signalled, not the "OTHER" queue. Below 0.7 a human reviews it, which \
is a good outcome.
- Quote one short verbatim phrase or sentence from the complaint that most drove your \
decision. Copy it exactly. Do not paraphrase, summarise or invent it.

Respond with JSON only:
{"queue": "<one queue, copied verbatim from the list>", "confidence": <number 0-1>, \
"evidence": "<verbatim quote from the complaint>"}"""

USER_TEMPLATE = """Product: {product}

Queues available for this product:
{queues}

Complaint:
{narrative}"""


def build_user_message(product: str, narrative: str, max_chars: int = 6000) -> str:
    queues = PRODUCT_QUEUES.get(product, ["OTHER"])
    return USER_TEMPLATE.format(
        product=product,
        queues="\n".join(f"- {q}" for q in queues),
        narrative=narrative[:max_chars],
    )


def route(product: str, queue: str, confidence: float) -> str:
    """Where a classified complaint goes. The abstention rule lives here, once.

    A queue the model invented — one not valid for this product — is treated exactly like
    an abstention. The model does not get to route to a queue that does not exist.
    """
    if queue not in PRODUCT_QUEUES.get(product, []):
        return "HUMAN_REVIEW"
    if queue == "OTHER" or confidence < CONFIDENCE_THRESHOLD:
        return "HUMAN_REVIEW"
    return "TEAM_QUEUE"
