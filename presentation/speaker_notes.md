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

The left column is ranked by one thing: how visible the reasoning is. Not by which saves
most.

The two on the right I am refusing. A chatbot fails in public, in your customer's voice,
with errors nobody can bound. Credit scoring is Annex III high-risk under the AI Act.

[Land this:] The fastest way to earn your trust is to tell you what not to buy.

# Slide 4 — This is the dashboard you would open
[Switch to the live dashboard here if you can. This slide is the fallback, and it is a
real screenshot of the same thing — use it if the demo is cold.]

Four numbers across the top. Only the third is in money.

Hold on to the fourth: 46% of what arrives could be sorted automatically. Not "AI will
transform complaints" — a share of something you already do.

Every panel says what it means in plain English underneath. No statistics language
anywhere, deliberately.

# Slide 5 — Volume and cost are not the same picture
[Switch to the live dashboard now if the room is warm. Otherwise stay on the table.]

Read the last column, not the first.

Deposits and cards are two thirds of your volume — but a card complaint ends with money
leaving the building 5.7 times more often than a vehicle loan complaint does.

So which queue a complaint lands in is not administration. It is money. That is your
argument for accurate routing, and I am only pointing at it.

[Q: Is this your data? — No. It is the US regulator's public complaint database, 16,839
complaints, used as a proxy for the *shape* of a complaint inbox — the mix and the
language. Not a forecast of your volumes. Your real numbers come from Phase 0.]

# Slide 6 — Five categories are half of everything that arrives
[Let the 46.1% sit. This is the slide the whole proposal rests on.]

Sixty-four categories exist. Five of them are nearly half your inbox.

That is what makes this buildable. I am not asking a model to be good at sixty-four
things — I am asking it to be good at five and to admit when it is outside them.

It is the difference between "AI for complaints", which I could not finish, and something
I can hand you working.

# Slide 7 — You can watch it decide
[Switch to the live n8n window. If the demo is cold, narrate the chevrons and play the
recording.]

Four steps, and notice where the chain ends. A person decides. The machine never routes
anything on its own.

The third box is where the work is. The model's answer is treated as a claim, not a
result — it gets checked before anyone sees it.

[If you have time, expand one guard:] The fourth check is the interesting one. The model
has to quote your customer's own words back, and we verify that quote is really in the
complaint before anyone sees it.

[Q: Why n8n rather than code? — Because you can read it. That is the entire reason.]

# Slide 8 — Here it is, actually running
[Switch to the live n8n window. This screenshot is the fallback if the demo is cold.]

Green ticks all the way across, on a real complaint from the corpus.

The bottom panel is the interesting part — the proposed team, the confidence, and the
customer's own words it relied on. It sent this one to Disputes and fraud, exactly where
the regulator's label put it.

Nothing here is a mockup. Click any node, read its real input and output.

# Slide 9 — It caught itself fabricating a reason
[Slow right down. This is the most important slide in the deck.]

Four times out of sixty, the model invented its justification — confidently quoting words
that were not in the complaint.

Every one was caught, because the system checks the quote against the text rather than
trusting it.

Look at the bottom row. Nothing was silently wrong. A system that explains itself
convincingly but falsely is the failure I instrument for.

# Slide 10 — One of those four, opened up
[Do not rush this. It is the proof behind the previous slide.]

One of the four, on the record.

Eighty per cent confident, an entirely plausible queue. But look near the bottom — evidence
is not verbatim. So it was stopped, with a reason code, and went to a person.

That record exists for all sixty decisions, including every one where nothing happened.
That is what I mean by watching it.

# Slide 11 — What it cannot do yet
[Do not soften this. Say the number plainly.]

Sixty per cent. Not good enough to deploy, and I am showing you rather than burying it.

I checked whether the model was simply weak. It agrees with itself nearly ninety per cent
of the time — stable, but systematically at odds with the public label.

So I looked at who writes that label. Your customer does, from a dropdown, untrained. It
records which box a member of the public ticked, not which team should have handled it.

# Slide 12 — The model is not the cost. Oversight is.
[Pause on the first row. Let someone react to 29 cents.]

Twenty-nine cents a year. That is measured, not estimated.

What actually costs money is the review — someone accountable for watching it. That is
the £5,600 line, and I would not remove it.

Which means at your volume, choosing a model is not a budget decision at all. It is an
accuracy decision. The model six times more expensive would still cost about five euro a
year.

[Q: So why not always use the best model? — At this volume you should. That is the point.]

# Slide 13 — What I would do next, and what it costs
[Slow on Phase 0. It is the unusual part and the part they will question.]

Fixed fee per phase, because your problem is uncertainty.

Phase 0 buys something odd: two of your handlers labelling three hundred complaints before
any AI at all. Worth buying even if you never build this — it tells you whether your
categories can be applied consistently by anybody.

Fourteen thousand to reach a decision, not twenty-four and a half to a deployment.

[If pressed on ROI:] The break-even is four avoided ombudsman referrals a year. I am not
claiming we hit it. That is what the pilot measures.

# Slide 14 — Close: what I want your feedback on
[Stop pitching. Drop the client voice — this is to you as assessors, not as Chleo.]

The questions are on the slide, so I will not read them.

Push me on the first. I built this pitch around admitting a weak number early, betting
that an honest sixty per cent buys more trust than a confident eighty-five.

I think that is right. I am not certain it survives contact with a real client.

# Slide 15 — Backup: three corrections made before any analysis
[Only if data quality is questioned.]

Three things the data appeared to say, and did not.

The July cliff is the one that would have caught me. The CFPB only publishes a complaint
once the firm has responded, so the newest weeks are always thin. Read naively it is a
73% collapse in complaints and a wonderful slide. It is an artefact — I cut the window at
27 June.

The other two are on the slide. The pattern is the point: each would have produced a
confident, wrong answer that no test would have caught.

# Slide 16 — Backup: the compliance position
[Only if the legal seat asks.]

Limited risk, and the reasoning is what matters: it classifies and routes, a human
resolves, and it never touches creditworthiness.

What holds it there is the human decision boundary. If it ever routes autonomously that
is a new assessment, not an upgrade to this one.

I am deliberately not giving you a final classification today. Round 2 owes the
step-by-step reasoning. A confident tier label without that work is exactly the unearned
certainty you were right to distrust in the first place.

# Slide 17 — Backup: every number and where it came from
[Only if sourcing is challenged.]

Everything on these slides is either measured by me or cited to a regulator.

Where a figure is a judgement rather than a measurement — the minutes per complaint, the
employer on-costs — it is labelled as a judgement in the cost model. I have not dressed
an estimate up as a finding anywhere in this deck.
