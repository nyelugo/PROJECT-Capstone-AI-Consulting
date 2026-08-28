# Slide 1 — Cover
[Beat. Do not read the slide.]
[Whole deck: you are in Chleo's meeting. Speak to the room as "you". The exception is the
close, where you step out and address the staff.]

We met at a dinner, and you told me you don't trust AI because you can't see what it does.

So this isn't a pitch about what AI could do for you. It's about one decision you can watch
happen. Everything here runs, and every number traces back to a repository you can open.

# Slide 2 — Context
You never asked me whether AI works. You asked what it *is*, and how you'd see it. Those
are the two questions your regulator will ask you as well.

So: a firm your size, and three candidates — triage, anomaly flagging, reporting help. They
are ranked by one thing only, which is how visible the reasoning is. Not by which saves
most. Triage is first because you can watch it work.

And two I'm refusing. A chatbot fails in public, in your customer's voice. Credit scoring
is high-risk under the AI Act — months of conformity work before a single decision goes
live.

[Land this:] The fastest way to earn your trust is to tell you what not to buy.

Let me show you what triage looks like on real complaints.

# Slide 3 — Dashboard
[Switch to the live dashboard if you can. This screenshot is the fallback.]

First, whose numbers these are, because it matters — they're not yours. This is the public
regulator's database standing in for your book until Phase 0 measures the real thing. The
shape transfers: the mix of issues, the language, how cases end. The volume doesn't, and I
won't pretend otherwise.

Four numbers across the top. Two of them you already report to your regulator, so they need
no explaining. The third is the only one in money — one complaint in eight ends with you
paying something out.

The fourth is the one to hold on to. Forty-six per cent of everything that arrives sits in
five of sixty-four categories. That's what makes this small enough to build honestly: I'm
not asking a machine to be good at sixty-four things.

Here it is doing that.

# Slide 4 — POC and monitoring
[Switch to the live n8n window, then the monitoring view. The screenshots are the fallback
if either demo is cold.]

On the left, the workflow running on a real complaint. Green ticks mean every step
executed. It proposed Disputes and fraud — quoting your customer's own words as its reason
— and then it stopped and waited for a person.

On the right, that same decision opened up in monitoring. Sixty decisions traced, every one
on the record, including the ones where nothing happened.

And this is the part I'd want you to hear. Four times out of sixty, the model made up its
justification — it quoted words that weren't in the complaint at all, confidently. The
check caught every one and sent it to a person with the reason written down.

[Point at the dark strip.] Which is why I'm not asking you to switch anything on. It picks
the right team sixty per cent of the time on this data. That is not good enough to route on
its own — so it proposes, and a person decides. That's the honest configuration until a
pilot on your data says otherwise.

# Slide 5 — Cost, timeline and the ask
Fixed fee per phase, because your problem is uncertainty and I won't hand you an open-ended
commitment.

Phase 0 buys something odd: two of your handlers labelling three hundred complaints before
any AI at all. That's the ground truth that doesn't exist today, and it's worth buying even
if you never build this — it tells you whether your own categories can be applied
consistently by anybody.

Running cost is seven thousand four hundred a year, of which the AI itself is twenty-nine
cents. The rest is someone accountable for watching it, and I wouldn't remove it.

Two assumptions, on the slide. The volume is the regulator's rate applied to a firm your
size, so treat the euros as an order of magnitude. And the return rests on avoiding
ombudsman referrals — four a year covers the running cost. I'm not claiming we hit it.
That's what the pilot measures.

Fourteen thousand to reach a decision. Not twenty-four and a half to a deployment.

# Slide 6 — Close
[Stop pitching. Drop the client voice — this is to you as assessors, not as Chleo.]

One thing I'd genuinely like taken apart.

I've built this pitch around admitting a weak number early rather than a confident one. I
think an honest sixty per cent buys more trust from a sceptical client than a polished
eighty-five would.

I think that's right. I'm not certain it survives contact with a real client, and that's
what I'd most like you to push on.

# Slide 7 — Backup: use cases and refusals
[If asked why these three, or why not a chatbot.]

Ranked by visible reasoning. The refusals matter as much: a chatbot's errors are unbounded
and public, and credit scoring is Annex III high-risk — conformity assessment and a
fundamental-rights impact assessment before go-live.

# Slide 8 — Backup: category concentration
[If asked how the scope was bounded.]

Five of sixty-four categories carry 46.1% of the volume. Concentration like that is a
property of complaint books generally, not of one firm — which is why I'd expect it to
hold for you even though the volume won't.

# Slide 9 — Backup: volume vs cost
[If asked where the money actually goes.]

Deposits and cards are two thirds of the volume here, but money leaves the building 5.7
times more often on a card complaint than a vehicle loan. That ratio follows from how the
products work, not from who the firm is — so it should hold for you.

# Slide 10 — Backup: the full decision record
[If asked how often it fails, or what happens then.]

Fifty-two proposed cleanly. Four stopped because the quote wasn't real, four because
confidence was too low. Bottom row is the one that matters: nothing was silently wrong.

# Slide 11 — Backup: why 60% is not the model's fault
[If challenged on accuracy.]

Ask it the same complaint twice and it answers the same way nine times in ten — so it's
consistent, it just disagrees with the official label. And that label was picked by the
customer filing the complaint, from a dropdown, untrained.

So the fix isn't a cleverer model, it's better labels. That is exactly what Phase 0 buys.

# Slide 12 — Backup: data corrections
[If data quality is questioned.]

The July cliff would have caught me. The regulator only publishes a complaint once the firm
has responded, so recent weeks are always thin — read naively that's a 73% collapse and a
wonderful slide. It's an artefact. I cut the window at 27 June. The other two are the same
pattern: confident, wrong, and invisible to any test.

# Slide 13 — Backup: compliance
[If the legal seat asks.]

Limited risk, and the reasoning matters more than the label: it classifies and routes, a
human resolves, it never touches creditworthiness. What holds it there is the human
decision boundary — if it ever routes on its own that's a new assessment, not an upgrade.

I'm deliberately not giving a final classification today. Round 2 owes the step-by-step
reasoning.

# Slide 14 — Backup: sources
[If sourcing is challenged.]

Everything is either measured by me or cited to a regulator. Where a figure is a judgement
rather than a measurement — minutes per complaint, employer on-costs — it's labelled as a
judgement in the cost model, not dressed up as a finding.
