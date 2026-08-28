# Slide 1 — Cover
[Beat before you start. Do not read the slide.]
[Whole deck: you are in Chleo's meeting. Speak to the room as "you", never about her as
"she". The one exception is slide 14, where you step out.]

We met at a dinner, and you told me you don't trust AI because you can't see what it does.

So this isn't a pitch about what AI could do for you. It's about one decision you can watch
happen. Everything here runs, and every number traces back to a repository you can open.

Let me start with what you said.

# Slide 2 — Chleo's objection is trust, not capability
[Point at the middle card. The fear is the slide.]

You never asked me whether AI works. You asked what it *is*, and how you would see it.
Those are the two questions your regulator will ask you as well.

So I'm not proposing a platform. I'm proposing one place in your business where you can
watch a machine decide — and overrule it.

There were three candidates for that place.

[Q: Isn't this too small to matter? — Small is the point. You can't audit something you
bought whole.]

# Slide 3 — Three use cases, and two I will not build
[Four seconds to scan. Don't read the six items.]

Ranked by one thing: how visible the reasoning is. Not by which saves most. Complaint
triage is first because you can watch it work.

The right column is what I'm refusing. A chatbot fails in public, in your customer's
voice. Credit scoring is high-risk under the AI Act — months of conformity work before a
single decision goes live.

[Land this:] The fastest way to earn your trust is to tell you what not to buy.

So: complaint triage. Here's what your complaints actually look like.

# Slide 4 — This is the dashboard you would open
[Switch to the live dashboard here if you can. This slide is the fallback — it's a real
screenshot of the same thing.]

Nearly seventeen thousand real complaints, on one screen.

Four numbers across the top, and only the third is in money. Hold on to the fourth: 46% of
what arrives could be sorted automatically — a share of something you already do, not a
promise about transformation.

Two things in here matter more than the rest.

# Slide 5 — Volume and cost are not the same picture
The first one. Read the last column, not the first.

Deposits and cards are two thirds of your volume — but money leaves the building 5.7 times
more often on a card complaint than a vehicle loan.

So which queue a complaint lands in isn't administration. It's money. That's your argument
for accurate routing, not mine.

The second thing is what makes this buildable at all.

[Q: Is this your data? — No. It's the US regulator's public database, used as a proxy for
the shape of a complaint inbox, not a forecast of your volumes. Your real numbers come
from Phase 0.]

# Slide 6 — Five categories are half of everything that arrives
Sixty-four categories exist. Five of them are nearly half your inbox.

So I'm not asking a machine to be good at sixty-four things. I'm asking it to be good at
five, and to admit when it's outside them.

That's the difference between "AI for complaints", which I couldn't finish, and something
I can hand you working.

Here's how it works.

# Slide 7 — You can watch it decide
Four steps, and notice where the chain ends — a person decides. The machine never routes
anything itself.

The third box is the work: the model's answer is a claim, not a result. Four checks before
anyone sees it, and they're on the slide.

That human boundary is also what keeps this limited-risk under the AI Act.

Let me show you it running.

# Slide 8 — Here it is, actually running
[Switch to the live n8n window. This screenshot is the fallback if the demo is cold.]

Green ticks all the way across, on a real complaint.

The bottom panel is the interesting part. It sent this one to Disputes and fraud —
exactly where the regulator's own label put it.

Nothing here is a mockup. Click any node and you read its real input and output.

That's one that worked. Here's what happens when it doesn't.

# Slide 9 — It caught itself fabricating a reason
[Slow right down. This is the most important slide in the deck.]

Four times out of sixty, the model made up its justification. It confidently quoted words
that were not in the complaint at all.

Every one was caught, because the system checks the quote against the text instead of
trusting it. Bottom row — nothing was silently wrong.

A system that explains itself convincingly but falsely is more dangerous than one that
says nothing. Let me show you one.

# Slide 10 — One of those four, opened up
One of those four, on the record.

Eighty per cent confident, a plausible team — and the sentence it quoted simply wasn't in
the complaint. So it was stopped, and went to a person with the reason written down.

That record exists for all sixty decisions, including every one where nothing happened.
That's what I mean by watching it.

Which brings me to the number I could have left out of this deck.

# Slide 11 — What it cannot do yet
[Don't soften this. Say it plainly.]

Sixty per cent of the time it picks the right team. Not good enough to deploy.

I'm showing you because the reason matters more than the number. Ask it the same complaint
twice and it answers the same way nine times in ten — so it's consistent. It just
disagrees with the official label.

And who writes that label? Your customer does, from a dropdown, untrained.

So the fix isn't a cleverer model. It's better labels — which changes what I'd ask you to
buy. But first, what it costs.

# Slide 12 — The model is not the cost. Oversight is.
Twenty-nine cents a year. Measured, not estimated.

What actually costs money is the review — someone accountable for watching it. That's the
five thousand six hundred line, and I wouldn't remove it.

So at your volume, choosing a model isn't a budget decision. It's an accuracy decision —
the one six times more expensive would still cost about five euro a year.

Which makes what I'm asking for small.

[Q: So why not always use the best model? — At this volume you should. That's the point.]

# Slide 13 — What I would do next, and what it costs
Fixed fee per phase, because your problem is uncertainty.

Phase 0 buys something odd: two of your handlers labelling three hundred complaints before
any AI at all. Those are the better labels — worth buying even if you never build this,
because it tells you whether your categories can be applied consistently by anybody.

For your operations team that's about six days, and nothing changes about who decides.

Fourteen thousand to reach a decision, not twenty-four and a half to a deployment.

[If pressed on ROI: break-even is four avoided ombudsman referrals a year. I'm not
claiming we hit it. That's what the pilot measures.]

# Slide 14 — Close: what I want your feedback on
[Stop pitching. Drop the client voice — this is to you as assessors, not as Chleo.]

The questions are on the slide, so I won't read them.

Push me on the first. I built this pitch around admitting a weak number early, betting
that an honest sixty per cent buys more trust than a confident eighty-five.

I think that's right. I'm not certain it survives contact with a real client.

# Slide 15 — Backup: three corrections made before any analysis
[Only if data quality is questioned.]

Three things the data appeared to say, and didn't.

The July cliff is the one that would have caught me. The regulator only publishes a
complaint once the firm has responded, so the newest weeks are always thin. Read naively
that's a 73% collapse in complaints and a wonderful slide. It's an artefact — I cut the
window at 27 June.

The other two are on the slide. The pattern is the point: each would have produced a
confident, wrong answer that no test would have caught.

# Slide 16 — Backup: the compliance position
[Only if the legal seat wants more than the line on slide 7.]

Limited risk, and the reasoning is what matters: it classifies and routes, a human
resolves, and it never touches creditworthiness.

What holds it there is the human decision boundary. If it ever routes on its own, that's a
new assessment, not an upgrade to this one.

I'm deliberately not giving you a final classification today. Round 2 owes the
step-by-step reasoning. A confident label without that work is exactly the unearned
certainty you were right to distrust.

# Slide 17 — Backup: every number and where it came from
[Only if sourcing is challenged.]

Everything on these slides is either measured by me or cited to a regulator.

Where a figure is a judgement rather than a measurement — the minutes per complaint, the
employer on-costs — it's labelled as a judgement in the cost model. I haven't dressed an
estimate up as a finding anywhere.
