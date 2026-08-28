# Slide 1 — Cover
[Beat before you start. Do not read the slide.]
[Convention for the whole deck: you are in Chleo's meeting. Speak to the room as "you",
never about her as "she". The only exception is Slide 11, where you step out.]

We met at a dinner, and you told me you do not trust AI because you cannot see what it does.

So this is not a pitch about what AI could do for you. It is about one decision you can
watch happen.

Everything here runs. Every number traces back to a repository you can open.

# Slide 2 — Chleo's objection is trust, not capability
[Point at the middle card, not the left one. The fear is the slide.]

You never asked me whether AI works. You asked what it *is*, and how you would see it.

Those are the two questions your regulator will ask you as well, which is why I have built
the answer to them rather than a demo.

So I am not proposing a platform. I am proposing one place in your business where you can
watch a machine decide — and overrule it.

[Q: Is this too small to matter? — Small is the point. You cannot audit something you
bought whole.]

# Slide 3 — Three use cases, and two I will not build
[Do not read the six items. Give them four seconds to scan, then talk about the ordering.]

The three on the left are ranked by one thing only: how visible the reasoning is. Not by
which saves the most money.

The two on the right I am refusing, and I want to be explicit about why. A chatbot fails
in public, in your customer's voice, with errors nobody can bound. Credit scoring is
Annex III high-risk under the AI Act — conformity assessment and a fundamental-rights
impact assessment before a single decision goes live.

[Land this:] The fastest way to earn your trust is to tell you what not to buy.

# Slide 4 — Volume and cost are not the same picture
[Switch to the live dashboard now if the room is warm. Otherwise stay on the table.]

Read the last column, not the first.

Deposits and cards are two thirds of your volume — but a card complaint ends with money
leaving the building 5.7 times more often than a vehicle loan complaint does.

So which queue a complaint lands in is not administration. It is money. That is your
argument for accurate routing, and I am only pointing at it.

[Q: Is this your data? — No. It is the US regulator's public complaint database, 16,839
complaints, used as a proxy for the *shape* of a complaint inbox — the mix and the
language. Not a forecast of your volumes. Your real numbers come from Phase 0.]

# Slide 5 — Five categories are half of everything that arrives
[Let the 46.1% sit. This is the slide the whole proposal rests on.]

Sixty-four categories exist. Five of them are nearly half your inbox.

That is what makes this buildable. I am not asking a model to be good at sixty-four
things — I am asking it to be good at five and to admit when it is outside them.

It is the difference between "AI for complaints", which I could not finish, and something
I can hand you working.

# Slide 6 — You can watch it decide
[Switch to the live n8n window. If the demo is cold, narrate the chevrons and play the
recording.]

This is running now. Not a mockup.

Here is the part that answers your actual question: you can open any step and read the
real data going through it. Not my description of what it did — the thing itself.

And notice where the chain ends. A person decides. The machine never routes anything on
its own.

[If you have time, expand one guard:] The fourth check is the interesting one. The model
has to quote your customer's own words back, and we verify that quote is really in the
complaint before anyone sees it.

[Q: Why n8n rather than code? — Because you can read it. That is the entire reason.]

# Slide 7 — It caught itself fabricating a reason
[Slow right down. This is the most important slide in the deck.]

Four times out of sixty, the model invented its justification — it produced a quote that
was not in the complaint at all. Confidently.

Every one was caught, because the system checks the quote against the text instead of
trusting it.

That bottom row is the one to look at. Nothing was silently wrong. A system that explains
itself convincingly but falsely is far more dangerous than one that says nothing, and it
is the failure I have instrumented for.

# Slide 8 — What it cannot do yet
[Do not soften this. Say the number plainly.]

Sixty per cent. That is not good enough to deploy, and I am showing you rather than
burying it, because the reason matters more than the number.

I checked whether the model was simply weak. It agrees with *itself* nearly ninety per
cent of the time — it is stable. It disagrees with the public label systematically.

So I looked at who writes that label. Your customer does, from a dropdown, untrained. It
records which box a member of the public ticked. It is not a record of which team should
have handled the case.

Measured against it, any vendor's accuracy figure means less than it appears to.

# Slide 9 — The model is not the cost. Oversight is.
[Pause on the first row. Let someone react to 29 cents.]

Twenty-nine cents a year. That is measured, not estimated.

What actually costs money is the review — someone accountable for watching it. That is
the £5,600 line, and I would not remove it.

Which means at your volume, choosing a model is not a budget decision at all. It is an
accuracy decision. The model six times more expensive would still cost about five euro a
year.

[Q: So why not always use the best model? — At this volume you should. That is the point.]

# Slide 10 — What I would do next, and what it costs
[Slow on Phase 0. It is the unusual part and the part they will question.]

Fixed fee per phase, because you told me your problem is uncertainty and I am not going
to hand you an open-ended commitment.

Phase 0 buys something odd: two of your own handlers labelling three hundred complaints,
before any AI at all. It is worth buying even if you never build this, because it tells
you whether your own categories can be applied consistently by anybody.

You are committing fourteen thousand to reach a decision — not twenty-four and a half to
a deployment. Phase 2 only happens if the pilot earns it.

[If pressed on ROI:] The break-even is four avoided ombudsman referrals a year. I am not
claiming we hit it. That is what the pilot measures.

# Slide 11 — Close: what I want your feedback on
[Stop pitching. Drop the client voice — this is to you as assessors, not as Chleo.]

The questions are on the slide, so I will not read them.

The one I actually want pushed on is the first. I have built this pitch around admitting
a weak number early, on the bet that an honest sixty per cent buys more trust than a
confident eighty-five would.

I think that is right. I am not certain it survives contact with a real client, and that
is the thing I would most like you to take apart.

# Slide 12 — Backup: three corrections made before any analysis
[Only if data quality is questioned.]

Three things the data appeared to say, and did not.

The July cliff is the one that would have caught me. The CFPB only publishes a complaint
once the firm has responded, so the newest weeks are always thin. Read naively it is a
73% collapse in complaints and a wonderful slide. It is an artefact — I cut the window at
27 June.

The other two are on the slide. The pattern is the point: each would have produced a
confident, wrong answer that no test would have caught.

# Slide 13 — Backup: the compliance position
[Only if the legal seat asks.]

Limited risk, and the reasoning is what matters: it classifies and routes, a human
resolves, and it never touches creditworthiness.

What holds it there is the human decision boundary. If it ever routes autonomously that
is a new assessment, not an upgrade to this one.

I am deliberately not giving you a final classification today. Round 2 owes the
step-by-step reasoning. A confident tier label without that work is exactly the unearned
certainty you were right to distrust in the first place.

# Slide 14 — Backup: every number and where it came from
[Only if sourcing is challenged.]

Everything on these slides is either measured by me or cited to a regulator.

Where a figure is a judgement rather than a measurement — the minutes per complaint, the
employer on-costs — it is labelled as a judgement in the cost model. I have not dressed
an estimate up as a finding anywhere in this deck.
