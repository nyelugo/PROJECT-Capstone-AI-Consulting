# Slide 1 — Assist
[Beat. Don't read the slide.]
[Whole deck: you are in the room with Chleo's team. Speak to them as "you". Step out only at
the very end if the staff want the assessor view.]

Three capabilities, all running. One decision you can watch end to end. And the business
case as it actually came out.

# Slide 2 — What changed after Round 1
[30 seconds. Don't linger.]

Direction is unchanged: same sector, same firm, same lead use case.

Scope widened. Round 1 proposed three use cases and built one; all three are built now. And
two things got harder rather than easier — a real ROI number in place of a cost estimate,
and the AI Act work Round 1 deliberately refused to guess at.

# Slide 3 — Three jobs, one shape
Three jobs your people do, and they're the same job wearing three coats.

Routing: two and a half thousand complaints a year, sixty-four categories. Two of your
handlers read the same complaint and pick different categories — not because either is
wrong, but because neighbouring categories describe the same event.

Reporting: the regulatory return gets built by hand, under deadline, by the people who can
least afford the day.

And fraud. Seven per cent of your complaints are unauthorised transactions — by the time you
hear about it, the money has gone.

[Land this:] High volume, low complexity, unstructured text. The shape a firm your size can
neither automate with rules nor afford to staff properly.

What stops this being solved isn't technical. It is that nobody can see what such a system
does — and a decision you cannot see is one you cannot sign off.

# Slide 4 — One decision spine, three capabilities
So here's the answer to that.

Four steps. It validates what comes in. The model proposes something. Guards check the
proposal is actually grounded in evidence that exists. And then a person decides.

[Point at the last arrow.] That step is not a feature, it is the whole design. There is no
setting where this routes, files or blocks anything by itself.

Every capability is those same four steps. Only the evidence changes — a sentence from the
complaint, a figure we computed, or the transaction's own values.

[Land this:] Which is why building all three cost 1.3 times building one — not three times.

[Point at the strip.] And the checks earn it. On one batch this week it caught a fabrication
in all three: two quotes that weren't in the complaint, six values that weren't in the
transaction, one figure we never computed.

# Slide 5 — The proof of concept
[Switch to the live n8n window. This slide is your fallback if it's cold.]

Nine steps, left to right. That's the entire system — you can read it without me.

[Run it.] Green ticks mean each step executed. It proposed Disputes and fraud, and quoted
the customer's own sentence as the reason. Not a summary — her words. Then it stopped and
waited for a person.

[If time, edit the complaint and re-run.] When it isn't sure it doesn't fail. It says which
check stopped it, in words a handler can act on.

[Three things to say before you move on.]

Tools: n8n, because your team can read it as boxes and arrows — a Python script would have
been quicker to write and impossible to show you.

What it does not prove is accuracy. It agrees with the public dataset's labels sixty per
cent of the time, and those labels were picked by the complainant from a dropdown. That is
agreement, not accuracy.

In production the trigger is your case system rather than a button, rejected inputs get
traced too, and delivery is confirmed back — today it records the decision, not the receipt.

# Slide 6 — What it returns
[Slow down. Do not apologise for this slide.]

Built as a one-off for a firm this size, it does not pay back. Minus thirty-one per cent
over three years, break-even in month sixty-nine.

That number could have been positive — start the benefits on day one, or trim the oversight
line. Both would have been wrong, and both would have surfaced in the pilot.

The capability is fine; the commercial shape is wrong. A bespoke build needs about three
thousand eight hundred complaints a year to pay for itself, and this firm has two and a
half thousand — a third too small. That is a fact about size, not about the technology.

[Point at the bottom two rows.] Move the oversight in-house after handover and it's minus
nine. Share the build across five firms your size and it turns positive. Do both and it's
plus ninety-six. The system is identical in every row. The only thing changing is who pays
for the build.

[Land this:] So I'm not asking you to fund a deployment. Eighteen thousand two hundred buys
you a decision, on your own data.

# Slide 7 — The three that could derail this
Not the full matrix — twelve risks are scored in the pack. Three you should care about.

The first is that I'm wrong about the value. Likelihood four, impact five, and I've priced
it rather than argued it away: fixed fee per phase means you can stop at eighteen thousand.

The second is the one nobody sells you. Your handlers stop reading and just click accept.
[Beat.] So I measure acceptance per handler, and anything above ninety-seven per cent is a
failure condition — not a success. That's the one number in here a vendor would never offer
you.

Third: oversight costing more than it saves. One shared design means one review covers all
three, and it's instrumented from day one so you'll know the real cost by the end of the
pilot rather than in year two.

[Land this:] The two biggest risks aren't technical. They're about how you run it.

# Slide 8 — Where this sits in law
[This is your Compliance Officer's slide. Slow down.]

Not high-risk under the AI Act. But the reason matters more than the label, so here it is.

Not Annex Three, because it never evaluates creditworthiness — the trap everyone expects to
catch a bank, and why credit scoring is excluded by design. Article Four, AI literacy,
applies today whatever the tier, which is why training is funded rather than assumed.

Two questions are left for counsel, both on anomaly flagging, both cheaper to answer before
it is built.

On the right, the part worth stating plainly. We pseudonymise the reference — but the
complaint narrative goes to the model in full. Anyone who says "it's fine, the data is
pseudonymised" has not read the system. So the transfer work is a gate before any pilot on
real customer data.

[Land this:] What keeps this out of the high-risk tier isn't a clever argument. It's a design
property: it proposes, a person decides. Take that away and the classification changes.

# Slide 9 — How this would go
Three phases, and the first one is the odd one.

Phase zero buys two of your handlers labelling three hundred complaints, before any AI
touches anything. That's the ground truth that doesn't exist today. And it's worth buying
even if you never build this — because if two of your trained people only agree seventy per
cent of the time, no software will do better, and your problem is the taxonomy, not the
technology. That's a finding worth five thousand six hundred on its own.

Phase one is sixty days of shadow running. It proposes alongside your team, nobody acts on
it, nothing changes for a customer. And we measure the gap between what it said and what
your handler did.

Phase two only happens if it clears three gates: eighty per cent accuracy against your own
labels, handler acceptance between seventy-five and ninety-seven, and zero ungrounded
outputs reaching a person. That last one is absolute.

# Slide 10 — The beginning of the real product
[Switch to the live app. Backup recording if it's cold.]

The workflow showed you it was possible. This is the product.

[Point at the list.] It's a queue — read overnight. Nobody types a complaint into a box it
already arrived in.

[Point at the deadline column.] And that's the column your regulator asks about. Your own
book had three hundred and thirty-five that missed a deadline; this one sorts by it.

[Open a row.] Every check it ran, by name, and the one it failed. Not a confidence score —
a list.

[Point at the buttons.] Nothing has happened yet. Someone has to press that, and the press
is recorded next to what the system proposed. A proposal with nobody's decision beside it
isn't a decision, it's a suggestion nobody owns.

# Slide 11 — What I'm asking for
[Stop pitching.]

A sixty-day shadow pilot on your own complaints. Eighteen thousand two hundred. Nobody acts
on a single suggestion.

It works, it's lawful, and it does not yet pay for itself at this size.

[Beat.] The pilot is what settles the third one.

# Slide 12 — Backup
[Divider. Don't present.]

# Slide 13 — Backup: why 60.5% is not accuracy
[If challenged on accuracy.]

Ask it the same complaint twice and it answers the same way nine times in ten. So it's
consistent — it just disagrees with the official label. And that label was picked by the
customer filing the complaint, from a dropdown, with no training.

The fix isn't a cleverer model. It's better labels. That's exactly what Phase 0 buys.

# Slide 14 — Backup: the anomaly detector's 100%
[If someone quotes the 100% back at you approvingly.]

Don't let me get away with that number. I wrote the detector's thresholds and I wrote the
generator that planted the anomalies. So it measures whether my code agrees with itself.

It's the same trap as the sixty per cent, and I've bound the caveat to the figure in the
code so it can't be lifted onto a slide on its own. Only a pilot on real traffic settles it.

# Slide 15 — Backup: AI Act classification, step by step
[If Legal wants the reasoning.]

Six steps. Step four is the one that matters: it's not an Annex Three use, because it never
evaluates creditworthiness.

Step five is the interesting one. If step four ever fails, anomaly flagging alone becomes
high-risk — because it profiles, and the derogation can't save something that profiles.
Triage and reporting stay outside. That asymmetry is exactly why anomaly flagging is built
last and can be switched off without touching the other two.

# Slide 16 — Backup: what actually leaves the building
[If Data Protection presses.]

Three rows. The identifier never leaves — that part is tested, not assumed. The narrative
does, in full, and the quoted sentence is stored in monitoring.

Which is why the transfer work is a gate rather than a task. And the practical answer is
cheap: the model is four thousandths of one per cent of running cost, so we can choose a
provider on data protection instead of on price.

# Slide 17 — Backup: what the pilot has to prove
[If asked how you'd know it worked.]

Five gates. Miss any of the first three and we don't proceed.

The acceptance rate has a ceiling as well as a floor, for the reason on slide seven.

And note the last row: if anomaly flagging alone fails, we ship the other two. The
architecture allows that, and the compliance work already flags it as the capability
carrying the risk.

# Slide 18 — Backup: anomaly flagging
[If asked how the fraud one works.]

The split matters. A deterministic detector decides what's unusual — arithmetic, same answer
every time. The model only explains why, in language an analyst can act on. A language model
can't compute a baseline and its mistakes aren't auditable, so it never chooses what to look
at.

It ranks by how far something departs from that account's own normal, never by the amount. A
large but ordinary payment on a wealthy account doesn't outrank a small impossible one on a
modest account. A predicted payout never orders the queue.

And the guard earns its place here too. Six of fifty-six case notes quoted a figure that
wasn't in the transaction record. Every one was stopped before an analyst saw it.
