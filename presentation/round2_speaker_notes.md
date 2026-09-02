# Slide 1 — Assist
[Beat. Don't read the slide.]
[Whole deck: you are in the room with Chleo's team. Speak to them as "you". Step out only at
the very end if the staff want the assessor view.]

Last time we met, I pitched you one thing. You told me to build all three. So that's what
you're going to see — three capabilities, all running, and one number I'd rather tell you
myself than let you find later.

# Slide 2 — What changed after Round 1
[30 seconds. Don't linger.]

Nothing changed direction. Same sector, same firm, same lead use case — because nothing you
said challenged them.

What changed is scope. You asked for all three, and all three are built. And two things got
harder rather than easier: I now have a real ROI number instead of a cost estimate, and I've
done the AI Act work I deliberately refused to guess at last time.

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

But the reason you haven't solved it isn't technical. It's that you told me you don't trust
AI, because you can't see what it does.

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

[Run it.] Green ticks mean each step executed. It's proposed Disputes and fraud. And look
at why — it quoted your customer's own sentence back at you. Not a summary. Her words.

Then it stopped and waited for a person.

[If time, edit the complaint and re-run.] Watch what happens when it isn't sure. It doesn't
fail. It says which check stopped it, in words your handler can act on.

[Three things to say before you move on.]

Tools: n8n, because your team can read it as boxes and arrows — a Python script would have
been quicker to write and impossible to show you.

What it does not prove is accuracy. It agrees with the public dataset's labels sixty per
cent of the time, and those labels were picked by the customer filing the complaint, from a
dropdown. That's agreement, not accuracy — and I'll come back to what it costs to fix.

In production the trigger is your case system rather than a button, rejected inputs get
traced too, and delivery is confirmed back — today it records the decision, not the receipt.

# Slide 6 — The number I'd rather you heard from me
[Slow down. Do not apologise for this slide.]

If I build this for you as a one-off, it does not pay back. Minus thirty-one per cent over
three years. Break-even lands in month sixty-nine.

I could have made that number positive. I'd have had to start the benefits on day one, or
quietly cut the oversight cost. Both would have been lies, and you'd have found them.

Here's what's actually going on. The capability is fine. The commercial shape is wrong. You
need about three thousand eight hundred complaints a year for a bespoke build to pay for
itself, and you have two and a half thousand. You are a third too small — which is a fact
about your size, not about the technology.

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

It's not Annex Three, because it never evaluates anyone's creditworthiness — that's the trap
everyone expects to catch a bank, and it's why credit scoring is something I refuse to
build. And Article Four, AI literacy, applies to you today whatever the tier, which is why
training is funded rather than assumed.

I've left two questions for your counsel, both about anomaly flagging, and both worth
answering before it's built rather than after.

On the right, the thing I'd rather you heard from me. We pseudonymise the reference — but
the complaint narrative goes to the model in full. Anyone who tells you "it's fine, the data
is pseudonymised" hasn't read the system. So the transfer work is a gate before any pilot on
real customer data, not something we discover later.

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

It works, it's lawful, and it doesn't yet pay for itself at your size.

[Beat.] I'd rather you heard that third one from me now than found it in month three.

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
