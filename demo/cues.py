"""The demo scripts, as cue lists.

One list per demo. Each cue pairs what is SAID with what happens ON SCREEN, and that
pairing is the point: the recorder performs the action, then holds the frame for exactly as
long as the narration for that cue lasts. Nothing is timed by hand, so nothing drifts.

The words here are the shot lists already written into `poc/poc_documentation.md` and
`mvp/mvp_documentation.md`, so the recording and the documentation cannot say different
things about the same demo.

Actions:
    ("goto", url)        navigate
    ("nav", "text")      click a sidebar page whose label contains text
    ("click", "text")    click a button whose label contains text
    ("row", n)           select row n of the canvas data grid
    ("scroll_to", "text") scroll until the element containing text is in view
    ("wait", seconds)    do nothing; let the narration run over a still frame
"""
from __future__ import annotations

MVP_URL = "http://localhost:8502"

# --------------------------------------------------------------------------- UC-1..3 MVP
# pf-05 gives slide 9 one to two minutes and asks for the UPGRADE: "here is what the POC
# showed was possible, here is the beginning of the real product." So it opens on the thing
# the workflow could not do — a queue — rather than on a classification.
MVP = [
    {"do": ("goto", MVP_URL + "/triage"),
     "say": "The workflow classified one complaint at a time. This is a morning's work, "
            "already read."},
    {"do": ("scroll_to", "Tick one to read it"),
     "say": "Sixty complaints, each one proposed a team overnight. Nobody typed them in — "
            "they arrived in the case system and the queue picked them up."},
    {"do": ("scroll_to", "Past the target"),
     "say": "And this is the column a regulated firm actually lives on: how old each "
            "complaint is, and how long is left before the first-response target. "
            "Forty-two of these are already past it."},
    {"do": ("row", 0),
     "say": "Open one."},
    {"do": ("scroll_to", "Because the customer wrote"),
     "say": "It proposes a team, and it has to quote the sentence that decided it — the "
            "customer's own words, not a summary. A guard checks that sentence is really "
            "in the complaint."},
    {"do": ("scroll_to", "Checks"),
     "say": "On the right, every check it ran, by name, and the one it failed. Not a "
            "confidence score. A list."},
    # The press has to be VISIBLE before it happens. In the first cut the click fired at
    # the top of the cue and the narration played over the aftermath, so the one moment the
    # whole design rests on was never on screen.
    {"do": ("scroll_to", "A person decides"),
     "say": "And nothing has happened yet. The system has proposed. Someone still has to "
            "press that."},
    {"do": ("click", "Accepted — routed as proposed"),
     "say": "Pressed. It leaves the queue, and the press is recorded beside what the system "
            "proposed."},
    {"do": ("nav", "Decision log"),
     "say": "That pairing is the audit record. A proposal with nobody's decision next to it "
            "is a suggestion nobody owns."},
    {"do": ("nav", "Overview"),
     "say": "And this is what the chief executive sees: what it proposed, what her people "
            "did about it, and how often they agreed. Same six checks behind all three "
            "capabilities — only the evidence changes."},
]

# --------------------------------------------------------------------------------- POC
# Deliverable 2 wants 2-5 minutes end to end; pf-05 gives slide 4 a 2-3 minute slot, so this
# targets three. pf-05 also names the three beats to narrate as it runs — trigger, the AI,
# the output — and three things to say afterwards: tools and why, what it does and does not
# prove, and what production would change.
#
# Requires an authenticated session on the cohort n8n instance. The recorder checks and
# stops with a clear message rather than filming a login page.
POC_URL = "https://ac-ft-26-07-06.n8n.irn.hk/workflow/NkRpklvLHKgcP3Ol"

POC = [
    {"do": ("goto", POC_URL),
     "say": "This is the proof of concept — nine steps, left to right. That is the whole "
            "system, and you can read it without me."},
    {"do": ("wait", 0),
     "say": "The trigger is a complaint arriving on a known product. Here it is a button; "
            "in production it is an event from the case system."},
    {"do": ("click", "Run demo"),
     "say": "Here the AI reads the complaint and proposes a queue. It has to quote the "
            "sentence that drove the decision, and a guard checks that sentence is really "
            "in the text."},
    {"do": ("wait", 6),
     "say": "Green ticks mean each step executed. And this is the output the handler "
            "receives: a team, a confidence, and the customer's own words as the reason."},
    {"do": ("wait", 0),
     "say": "Three things before we move on. The tool is n8n, because a client's team can "
            "read it as boxes and arrows — a Python script would have been faster to write "
            "and impossible to show a chief executive."},
    {"do": ("wait", 0),
     "say": "What it proves is that the decision is inspectable and that a fabricated "
            "quotation gets caught. What it does not prove is accuracy: sixty per cent is "
            "agreement with labels a complainant chose from a dropdown, not accuracy."},
    {"do": ("wait", 0),
     "say": "And in production the trigger becomes a case-system event, rejected inputs get "
            "traced too, and delivery is confirmed back rather than assumed."},
]

SCRIPTS = {"mvp": MVP, "poc": POC}
