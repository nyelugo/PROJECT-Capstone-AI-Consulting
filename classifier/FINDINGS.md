# Classifier Findings — What the Evidence Actually Says

Author: Ugo Ahukannah
Capstone Round 1 · Supporting `n8n/` (POC) and the Round 2 MVP

All figures reproducible: `python classifier/evaluate.py 40 <model>` and
`python classifier/ambiguity_test.py`. Raw output in `eval_results_*.json`,
`eval_predictions_*.csv`, `ambiguity_results.json`.

---

## Headline

**The triage mechanism works and is stable. The accuracy number cannot honestly be
established from public data, because the public labels are not expert judgements —
they are the boxes members of the public ticked when filing.**

That is the finding to take to Chleo, and it changes what she should buy first.

## What was measured

Sample: 240 complaints, 40 per product, stratified, seed 42. Ground truth: the CFPB's own
`Issue` label, folded to OTHER below the 1% per-product floor.

| Measure | gpt-4o-mini | gpt-4o |
|---|---:|---:|
| Exact-label accuracy | 45.0% | 48.3% |
| **Team-level accuracy** (volume-weighted) | **56.8%** | **60.5%** |
| Team accuracy on auto-routed items | 61.4% | 64.2% |
| Auto-routed (not seen by a human) | 91.7% | 79.2% |
| Invented a queue that does not exist | 0.4% | 0.0% |
| Evidence quote genuinely verbatim | 93.8% | 99.6% |
| Mean tokens per complaint | 726 | 723 |

A model roughly 17× more expensive buys about 4 percentage points. **The bottleneck is not
the model.**

## Three things that were wrong, and how they were found

### 1. The task was ill-posed (found by checking the data)
The first evaluation scored 40%. The cause was not the prompt: the CFPB issue taxonomy is
**product-scoped**. "Managing an account" exists only under checking/savings; "Problem
with a purchase shown on your statement" only under credit card. The model was being asked
to guess a label partly determined by a field it was never given.

**Fix:** the classifier is product-conditioned. It receives the product and only that
product's queues. In a real deployment the product is always known — a complaint arrives
attached to an account.

### 2. Abstention was conflated with out-of-scope (found by reading the errors)
11 of 29 errors were the model confidently choosing OTHER at 0.8–0.9 when a valid queue
existed. The prompt had told it OTHER "is a good outcome", so it took the exit.

**Fix:** the two mechanisms are now separate. `OTHER` means *outside the taxonomy*.
Confidence below 0.70 means *uncertain*. A queue the model invents for the wrong product
is treated as an abstention — it does not get to route to a queue that does not exist.

### 3. The metric measured the wrong thing (found by reading the confusion pairs)
Errors clustered on genuine synonyms: "Fraud or scam" ↔ "Unauthorized transactions",
"Managing an account" ↔ "Problem with a lender charging your account", "Opening" ↔
"Closing an account". Both members of each pair reach the **same team**.

**Fix:** the 47 queues map to **7 teams** (`classifier/teams.py`), and routing is scored
at team level, with exact-label accuracy still reported beside it so nothing is hidden.
A mid-size firm has teams, not 47 queues.

## The test that changed the conclusion

The obvious explanation for ~60% was that the task is inherently ambiguous — that any two
people would label these complaints differently. **That hypothesis was tested and it is
false.**

Running gpt-4o twice over the same 100 complaints at temperature 1:

| | |
|---|---:|
| Self-agreement, exact queue | **88.0%** |
| Self-agreement, team | **89.0%** |

The model is highly self-consistent. It reaches ~89% agreement with itself and ~60% with
the CFPB label. **The disagreement is systematic, not noise.** The model applies the
taxonomy one way, consistently; the complainant applied it another way.

That makes sense once you look at who assigns the label: **the CFPB `Issue` value is
chosen by the person filing the complaint**, from a product-specific menu, with no
training and no incentive to be consistent with anyone else. It is a faithful record of
what a member of the public picked. It is not a record of which team should handle the case.

## What follows for the client

1. **Do not evaluate a triage model against consumer-selected labels.** It measures
   agreement with untrained self-selection, not routing quality. Any vendor quoting an
   accuracy figure built this way is quoting a number that does not mean what it appears
   to mean.
2. **The cheapest next step is a labelling exercise, not a model.** Two experienced
   complaint handlers independently label ~300 of the firm's own complaints to the firm's
   own teams. That gives (a) a real ground truth, (b) a measured human agreement rate,
   which is the actual ceiling, and (c) the pilot's success criterion. It costs days, not
   months, and it is worth doing whether or not any AI is ever bought.
3. **The transparency mechanism is already proven.** 99.6% of the model's evidence quotes
   are genuinely verbatim from the complaint — it reliably shows its work. That is the
   part of Chleo's objection that has been answered by this POC.
4. **Do not auto-route yet.** At a measured 64% team accuracy against the only labels
   available, the honest configuration is assist-only: the model proposes a team and
   quotes its reason, a human confirms. Auto-routing is a decision for after the pilot,
   on real labels.

## Honest limitations

- 240 complaints per model is enough to rank the options, not enough for a precise figure.
  The ~±6pp interval does not change any conclusion above.
- The corpus is US regulatory-escalation data used as a structural proxy. Chleo's own
  complaint mix will differ.
- The 7-team mapping is a reasonable reconstruction of how a mid-size firm organises, not
  Chleo's actual org chart. Her teams would replace it on day one of a pilot.
- Verbalised confidence is poorly calibrated: gpt-4o-mini auto-routed 91.7% of complaints,
  including ones it got wrong. The confidence threshold is a weak gate on its own, which
  is the second reason the recommended configuration is assist-only.
