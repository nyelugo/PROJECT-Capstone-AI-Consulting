# Slide 1 — Cover
[Hold for a beat before starting. Do not read the slide.]

I met Chleo at a dinner. She runs a mid-size financial services firm, and she told me she
does not trust AI because she cannot see what it does.

So this is not a pitch about what AI could do for her. It is a pitch about one decision she
can watch happen.

Everything I am about to show you runs. The numbers are reproducible from the repository.

# Slide 2 — Chleo's objection is trust, not capability
Three things I took from that dinner.

Her firm: about 500 staff, a quarter of a million retail customers, EU-established.

Her fear, in her own words: AI is not transparent. She kept asking what "the AI" actually
is, and how she would sign up. Those are not naive questions. They are the right ones.

So the job is not to build her a platform. It is to find one place in her business where a
machine makes a decision, and she can watch it, and disagree with it.

[Q: Isn't she just uninformed? — No. She is asking for auditability, which is exactly what
her regulator will ask for too.]

# Slide 3 — Three use cases, and two I will not build
Three I would build. Complaint triage — it reads a complaint and proposes which team should
handle it. Anomaly flagging, where every flag carries its reason. And reporting assistance,
which drafts what a person then signs.

Two I refuse. A customer-facing chatbot fails in public, in her customer's voice, and its
errors are unbounded. Credit scoring is Annex III high-risk under the EU AI Act — that is
conformity assessment and a fundamental-rights impact assessment before a single decision
goes live.

[Land this line:] I think the fastest way to earn a sceptical CEO's trust is to be the
consultant who tells her what not to buy.

# Slide 4 — Volume and cost are not the same picture
This is from her dashboard, built on 16,839 real complaints from the public CFPB database.

Deposits and cards are two thirds of the volume. But look at the last column — credit card
complaints end with money paid out 17.2% of the time, against 3.0% for vehicle loans. Nearly
six times.

So where a complaint lands is not an administrative detail. It has money attached to it.
That is the argument for getting routing right, and it is her argument, not mine.

[If asked about the data:] US regulatory data, used as a proxy for the shape of a complaint
inbox — the mix of issues and the language — not a forecast of her volumes. I say that on
the dashboard itself.

# Slide 5 — Five categories are half of everything that arrives
This is the finding the whole proposal rests on.

There are 64 issue categories. Five of them are 46% of everything that arrives.

That means the model does not have to be good at 64 things. It has to be good at five, and
it has to be willing to say "I don't know" about the rest.

That is a scope Chleo can approve and a risk she can bound. It is the difference between
"AI for complaints" and something I can actually finish.

# Slide 6 — You can watch it decide
[Switch to the live n8n window if time allows; otherwise narrate the diagram.]

A complaint arrives. The model proposes a team. Four guards check that proposal. A handler
sees the reason and decides.

Every branch ends at a person. Nothing is routed by the machine.

And this is the part that answers her actual question — in n8n she can open any step and
read the exact data going in and out. Not a description of what it did. The thing itself.

The four guards: valid JSON, a queue that actually exists for that product, confidence above
0.70, and the quote must appear verbatim in the complaint. Any failure goes to a human with
the reason stated.

[Q: Why n8n and not code? — Because she can read it. That is the whole point.]

# Slide 7 — It caught itself fabricating a reason
60 decisions traced in LangSmith. Every one accounted for.

52 passed all checks. Four were stopped because the model's confidence was too low. And four
were stopped because the justification quote it gave was not actually in the complaint.

[Slow down here.] It made up its reason. Four times out of sixty. And the system caught
every one, because the guard checks the quote against the text rather than trusting it.

A system that explains itself convincingly but falsely is more dangerous than one that says
nothing at all. That is the failure mode Chleo should be afraid of, and it is the one we
instrument for.

# Slide 8 — What it cannot do yet
Here is the number I could have left off this deck.

60.5% correct team assignment. That is not deployable. I am telling you because the reason
matters more than the number.

I tested whether the model was just weak. It agrees with itself 88 to 89% of the time — it
is stable. It disagrees with the public label systematically, not randomly.

Then I looked at who assigns that label. It is chosen by the customer filing the complaint,
from a dropdown, with no training. It records which box a member of the public ticked. It is
not a record of which team should handle the case.

So measuring a triage model against it measures agreement with untrained self-selection.
Any vendor quoting an accuracy figure built this way is quoting a number that does not mean
what it appears to mean.

# Slide 9 — The model is not the cost. Oversight is.
The API costs 29 cents a year. That is not a typo, and it is measured, not estimated —
684 input tokens and 49 output tokens per complaint, at list price.

The platform is €1,800. The quarterly accuracy review is €5,600 — that is someone
accountable for watching it.

97% of the running cost is human oversight. Four thousandths of one percent is the model.

Which means model choice is not a financial decision at her volume. It is an accuracy
decision. Even the model six times more expensive would cost about €5 a year.

[Q: So why not use the best model always? — At this volume, you should. That is the point.]

# Slide 10 — What I would do next, and what it costs
Three phases, fixed fee, because a client whose objection is uncertainty should not be handed
an open-ended commitment.

Phase 0 is two weeks and €5,600 — two of her handlers label 300 complaints. That produces
the ground truth she does not currently have. It is worth buying even if she never builds
any AI, because it tells her whether her own categories can be applied consistently by
anyone.

Phase 1 is the pilot: it proposes, nobody acts on it, and we measure against her labels.

Phase 2 only happens if the pilot passes.

She commits €14,000 to reach a decision, not €24,500 to a deployment.

And the break-even is concrete: the running cost is covered if this prevents four ombudsman
referrals a year, at €760 each. Whether it does is what the pilot is for. I am not claiming
it does.

# Slide 11 — Close: what I want your feedback on
[Step out of the pitch here. Change tone — this is to the room as assessors, not as Chleo.]

Three things I would genuinely like challenged.

First — I lead with "this is not deployable yet, and here is the number." I think that is
stronger than a confident 85%. It might just lose the room.

Second — Phase 0 sells a labelling exercise before any AI at all. Does that read as rigour,
or as stalling?

Third — I refuse two use cases on stage. Does that build authority, or does it sound
negative?

If you only push me on one thing, push me on the first.

# Slide 12 — Backup: three corrections made before any analysis
[Only if asked about data quality.]

Three things the data appeared to say that were false.

Complaints looked like they fell 73% in July. They did not — the CFPB only publishes a
complaint once the firm has responded, so recent weeks are structurally incomplete. I cut
the window at 27 June.

Handling time looked like a service metric. It is zero for 96% of records because it
measures the regulator's own routing, not any firm's speed. I dropped it.

And two different timeliness fields were on screen together — 98.0% answered on time next to
0.6% "untimely" — which reads as a contradiction. They measure different things, so I
relabelled one.

Each of those would have produced a confident wrong answer.

# Slide 13 — Backup: the compliance position
[Only if the legal seat asks.]

Preliminary view: limited risk. It classifies and routes; a human resolves. It is not Annex
III creditworthiness assessment.

What keeps it there is the human decision boundary. If it ever routes autonomously, that is
a new assessment, not an upgrade.

GDPR applies regardless of tier — complaint text is personal data, so legal basis, retention
and a DPIA are Round 2 deliverables.

The open risk I would flag now is model hosting region. An EU customer's complaint text must
not leave the EEA by accident.

I am deliberately not giving you a final classification. Round 2 owes the step-by-step
reasoning. A confident tier label without that work is exactly the unearned certainty Chleo
is right to distrust.

# Slide 14 — Backup: every number and where it came from
[Only if challenged on sourcing.]

The corpus is the CFPB public API. The complaint rate is FCA aggregate data for the second
half of 2025. The ombudsman fee is the published FOS figure. The token counts I measured
myself. The accuracy figure is 240 complaints, stratified, fixed seed.

Everything on these slides is either measured or cited. Where a number is a judgement — the
triage minutes, the on-costs — it is labelled as a judgement in the cost model, not dressed
up as a measurement.
