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
    ("point", "text")    glide the cursor onto that element without clicking
    ("wait", seconds)    do nothing; let the narration run over a still frame
"""
from __future__ import annotations

MVP_URL = "http://localhost:8502"

# --------------------------------------------------------------------------- UC-1..3 MVP
# pf-05 gives slide 9 one to two minutes and asks for the UPGRADE: "here is what the POC
# showed was possible, here is the beginning of the real product." So it opens on the thing
# the workflow could not do — a queue — rather than on a classification.
# Every beat moves the cursor to the thing being described. A cue that only talks leaves a
# still frame, which is what the first cut was: correct, complete, and unwatchable.
MVP = [
    {"do": ("goto", MVP_URL + "/triage"),
     "say": "The workflow classified one complaint at a time. This is a morning's work, "
            "already read."},
    {"do": ("point", "Tick one to read it"),
     "say": "Sixty complaints, each one already proposed a team. Nobody typed them in — "
            "they arrived in the case system and the queue picked them up."},
    {"do": ("point", "Past the target"),
     "say": "And this is what a regulated firm actually lives on. How old each complaint "
            "is, and how long is left before the first-response target."},
    {"do": ("point", "Target is 15 days"),
     "say": "Forty-two of these are already past it. You can sort on that column, and "
            "filter down to just the ones that need a person."},
    {"do": ("row", 0),
     "say": "Open one."},
    {"do": ("point", "Because the customer wrote"),
     "say": "It proposes a team, and it has to quote the sentence that decided it — the "
            "customer's own words, not a summary. A guard checks that sentence is really "
            "in the complaint."},
    {"do": ("point", "Checks"),
     "say": "On the right, every check it ran, by name, and the one it failed. Not a "
            "confidence score. A list."},
    {"do": ("point", "A person decides"),
     "say": "And nothing has happened yet. The system has proposed. Someone still has to "
            "press this."},
    {"do": ("click", "Accepted — routed as proposed"),
     "say": "Pressed. It leaves the queue."},
    {"do": ("nav", "Decision log"),
     "say": "And the press is recorded beside what the system proposed."},
    {"do": ("point", "Items revisited"),
     "say": "That pairing is the audit record. A proposal with nobody's decision next to "
            "it is a suggestion nobody owns."},
    {"do": ("nav", "Overview"),
     "say": "This is what the chief executive sees. What it proposed, what was held back "
            "and why."},
    {"do": ("point", "Agreement rate"),
     "say": "And how often her people actually agreed with it — the number that says "
            "whether this is working. Same six checks behind all three capabilities. Only "
            "the evidence changes."},
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
    {"do": ("point", "Complaint received"),
     "say": "The trigger is a complaint arriving on a known product. Here it is a button; "
            "in production it is an event from your case system."},
    {"do": ("point", "Normalise complaint"),
     "say": "First it checks the request is even worth spending on — a product it handles, "
            "text long enough to read. A bad request is rejected here, before a token."},
    {"do": ("click", "Execute workflow"),
     "say": "Now watch it run."},
    {"do": ("point", "Classify complaint"),
     "say": "Here the AI reads the complaint and proposes a queue. It has to quote the "
            "sentence that drove the decision, and the next step checks that sentence is "
            "really in the text."},
    {"do": ("point", "Validate and route"),
     "say": "Five guards, in a fixed order. A malformed answer, a queue that does not exist, "
            "confidence below the line, a quote that was never in the complaint — each one "
            "has its own code, so a refusal says which."},
    {"do": ("point", "Propose to handler"),
     "say": "Green ticks mean each step executed. And this is the output the handler "
            "receives: a team, a confidence, and the customer's own words as the reason."},
    {"do": ("point", "Send to human review"),
     "say": "When any guard fires, the complaint comes down here instead — to a person, "
            "with the reason written down. Nothing is silently dropped and nothing is "
            "silently guessed."},
    {"do": ("point", "Trace to LangSmith"),
     "say": "And every run leaves a monitoring record on this branch. It hangs off to the "
            "side deliberately: observing the decision must never be able to change it."},
    {"do": ("point", "Run demo"),
     "say": "Three things before we move on. The tool is n8n, because your team can read it "
            "as boxes and arrows — a Python script would have been faster to write and "
            "impossible to show you."},
    {"do": ("point", "Classify complaint"),
     "say": "What it proves is that the decision is inspectable, and that a fabricated "
            "quotation gets caught. What it does not prove is accuracy: sixty per cent is "
            "agreement with labels a complainant chose from a dropdown."},
    {"do": ("point", "Complaint received"),
     "say": "And in production the trigger becomes a case-system event, rejected inputs get "
            "traced too, and delivery is confirmed back rather than assumed."},
]

SCRIPTS = {"mvp": MVP, "poc": POC}
