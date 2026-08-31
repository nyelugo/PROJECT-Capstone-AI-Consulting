# Assist — MVP documentation

**Capstone Round 2 · working MVP.** Three capabilities, one decision spine, a person in
every loop. Nothing in this application acts on a customer, a case or an account. It
proposes, shows its reasoning, and waits.

---

## Run it

```bash
cd PROJECT-Capstone-AI-Consulting
conda activate bootcamp-env          # or any Python 3.11+ environment
pip install -r requirements.txt
streamlit run mvp/app.py
```

Opens on <http://localhost:8501>. On macOS, double-click **`run_mvp.command`**; on Windows,
**`run_mvp.bat`**.

### Keys

One key is required, one is optional.

| Variable | Required | What happens without it |
|---|---|---|
| `OPENAI_API_KEY` | **yes** | The app loads and explains itself, and every capability button is disabled with a message naming the file to fix |
| `LANGSMITH_API_KEY` | no | Everything works; decisions are not sent to monitoring, and the app says so under each result |
| `LANGSMITH_ENDPOINT` | no | Defaults to `https://eu.api.smith.langchain.com` — this workspace is EU-hosted, and a US endpoint returns 403 in a way that reads as a bad key |

Keys are read from `~/.config/ironhack/.env.local` (one shared file for all Ironhack work),
or a repo-local `.env.local`, or the environment — in that order. `.env.example` lists the
names. **No key value is ever printed**: the sidebar shows presence as a length and an
8-character digest, which is enough to tell "wrong key" from "no key" without exposing one.

### Test it without a key or a network

```bash
python -m mvp.test_spine        # 27 guard cases, all three capabilities
```

Exercises every rejection path against a stubbed model. Each case asserts the reason code
**and** the stage that stopped it — a test that only checked "went to a human" would pass
for the wrong reason, and the entire claim of this system is that a refusal says why.

---

## What it does

| Tab | Use case | Proposes | Grounded in |
|---|---|---|---|
| Triage a complaint | UC-1 | A routing queue and team | A verbatim quote from the complaint |
| Draft a report section | UC-3 | 3–5 sentences of report prose | Figures computed by `dashboard/metrics.py` |
| Review a flagged pattern | UC-2 | An analyst case note | The transaction record's own values |
| Decision log | — | Nothing | What the system proposed, beside what the person did |

## How it is built

```
validate input → model proposes → guards verify it is grounded → a human confirms
```

Every capability is that shape. `mvp/spine.py` owns the control structure; a capability
supplies only a prompt, a scope rule and a grounding rule. Adding a fourth would not touch
the spine, the error handling, the reason-code vocabulary or the trace record.

```
mvp/
├── spine.py                 the six guards, the reason codes, the Decision record
├── runtime.py               keys, the model client, pseudonymisation, tracing
├── app.py                   Streamlit UI — one renderer for all three capabilities
├── test_spine.py            27 guard cases, no network, no keys
├── capabilities/
│   ├── triage.py            UC-1 · reads classifier/prompt.py, unchanged
│   ├── reporting.py         UC-3 · reads dashboard/metrics.py, unchanged
│   └── anomaly.py           UC-2 · deterministic detector + explainer
└── synth/
    ├── make_transactions.py deterministic generator, anomalies planted with labels
    └── transactions.csv     2,069 transactions · 40 accounts · 2026-04-01 to 2026-06-29
```

Triage and reporting import the **Round 1 modules directly**, not a fork. The MVP, the n8n
POC and the Round 1 dashboard therefore cannot disagree about a classification or a figure
— a difference between the demo and the product would make the demo evidence for nothing.

### The six guards, in declared order

Order is part of the contract: a proposal failing two guards is always reported under the
first, so reason-code distributions stay comparable across capabilities and across rounds.

| Stage | Fails as | Meaning |
|---|---|---|
| input | `REJECT_INVALID_INPUT` | The request never met the contract. Costs no tokens |
| call | `ERROR_MODEL_CALL` | The model call itself failed |
| parse | `REJECT_MALFORMED_OUTPUT` | Not valid JSON, or confidence was not a number |
| scope | `REJECT_QUEUE_NOT_IN_PRODUCT`, `REJECT_OUT_OF_TAXONOMY`, `REJECT_METRIC_NOT_PUBLISHED`, `REJECT_ACCOUNT_NOT_IN_LEDGER` | The thing proposed does not exist |
| confidence | `REJECT_LOW_CONFIDENCE` | Below 0.70. Abstention is a correct answer |
| grounding | `REJECT_EVIDENCE_NOT_VERBATIM`, `REJECT_FIGURE_NOT_COMPUTED`, `REJECT_VALUE_MISMATCH` | The proposal cited something that is not there |

Codes carried unchanged from Round 1's `classifier/decide.py` still mean what they meant, so
Round 1 and Round 2 monitoring data are directly comparable.

The UI renders this ladder beside every result, with a tick against each check passed and a
cross against the one that stopped it. That display **is** the answer to Chleo's objection:
not "trust it", but "here is every check, by name, and here is the one it failed".

### Error handling

`spine.run()` never raises. Every exit is a `Decision` carrying a reason code, including a
crash — a capability that failed and a capability that abstained are both observable
outcomes, and they must not look the same in monitoring. "Cannot tell" is not "nothing
happened". Concretely: a missing key, a network failure, a timeout, malformed JSON, a
number where a string was expected, and an unparseable request all resolve to a reason code
and a rendered result, never a stack trace on screen.

### Monitoring

Every decision is sent to LangSmith project `capstone-mvp` with its reason code, failed
stage, capability, latency and pseudonymous reference. Tracing is a **leaf**: it is called
after the `Decision` already exists, it returns a bool, and nothing downstream reads it.
Round 1 wired a trace step inline into the n8n workflow, where it replaced the payload and
broke the routing that followed — observing must not affect the observed. Monitoring being
down cannot stop the system deciding.

### Personal data

The reference attached to every decision and trace is a salted pseudonym (`cx_…`). Raw
complaint references and account identifiers never enter the record — `test_spine.py`
asserts this rather than assuming it. Pseudonymisation is idempotent, because in Round 1
re-hashing an already-hashed reference produced a second valid-looking alias that joined to
nothing, and every presence check passed while the key was useless.

---

## What is measured, and what is not

**Triage.** 60.5% agreement with CFPB labels; 88.0% self-agreement on repeat runs. This is
**agreement, not accuracy** — the CFPB label was chosen by the complainant from a dropdown,
not assigned by an expert. No accuracy figure exists for this system, and Phase 0 (two
handlers labelling 300 complaints) is what would create one. See `classifier/FINDINGS.md`.

**Reporting.** The grounding guard is measured by construction: `test_spine.py` shows an
invented percentage rejected and the real figure accepted, including when rounded. What is
**not** measured is whether the prose is *good* — a draft can be fully grounded and still
emphasise the wrong thing. That is why a compliance officer accepts or rejects every draft.

**Anomaly.** The detector finds 100% of planted anomalies across all four patterns, at 97.1%
precision (56 candidates, 103 transactions flagged, 100 planted). **Do not report this as a
detection rate.** The detector's thresholds and the data generator were written by the same
author, so it measures whether the code agrees with itself — structurally the same trap as
the 60.5%. The caveat is bound to the figure in `score()`'s return value so it cannot be
lifted onto a slide alone. What it does establish: the detector is deterministic, covers all
four patterns rather than only the easy one, and its false-positive rate is measurable.

## Known limitations

1. **The grounding scan reads digits, not words.** "five transactions" is not checked;
   "5 transactions" is. A model writing figures as words could evade the check.
2. **Reporting confidence is weakly calibrated** — observed at 1.00 on live runs where a
   0.85 would have been more honest. The grounding guard, not the confidence, is what
   actually protects this capability.
3. **The decision log is per-session.** Closing the browser loses it. A production version
   writes to the case system, which is also where receipt would be confirmed — see below.
4. **The trace records the decision, not the delivery.** A successful trace proves the
   system decided, not that a handler received it. Carried over from Round 1, still open.
5. **Anomaly detection runs on a fixed batch**, not a stream. Thresholds are static and
   would need per-portfolio tuning before a pilot.
6. **Rejected input is traced only from the MVP**, not from the n8n POC, where validation
   throws before the trace fan-out.
7. **One model, one temperature.** No fallback if `gpt-4o-mini` is unavailable; the call
   surfaces as `ERROR_MODEL_CALL` and the work goes to a person, which is the correct
   failure but not a resilient one.

## What would be different in production

Case-system integration in place of the session log; per-portfolio detector thresholds;
expert labels from Phase 0 replacing complainant labels as the triage benchmark; a real
transaction feed replacing `synth/`; retention and deletion wired to the GDPR register in
`compliance/gdpr_documentation.md`; and an on-call owner for the monitoring project, which
the cost model already funds as the largest running line.
