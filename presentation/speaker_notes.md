# Round 1 Presentation — Clean Speaker Notes

## Main presentation — Slides 1–5

### Slide 1 — See exactly what the AI does

Over dinner, you told me you do not trust AI because you cannot see what it does.

So I am not asking you to believe a promise. I am going to show you 1 complaint-routing decision from start to finish.

The workflow runs, its reasoning is visible, and every number traces to project evidence, including public complaint data from the U.S. Consumer Financial Protection Bureau, or CFPB.

### Slide 2 — A mid-size bank needs AI it can inspect

You asked 2 questions: what exactly is the AI, and how would you see what it is doing?

I assessed 3 use cases: complaint triage, anomaly flagging, and reporting assistance. I ranked them by inspectability, not the largest promised saving.

Triage comes first because the system proposes a team, shows the supporting words, and lets a person confirm or reject it.

I ruled out a chatbot because it can fail publicly in the firm’s voice, and creditworthiness scoring because it is an Annex III high-risk use under the EU AI Act.

The fastest way to earn your trust is to be clear about what you should not buy.

Now let me show you the opportunity suggested by public complaint data.

### Slide 3 — 4 numbers define the opportunity

This dashboard uses public CFPB data as a proxy. These are not your firm’s numbers; Phase 0 measures your real complaint mix and volume.

The analysis contains 16,839 public complaints across 567 firms. The CFPB timely-response field is 98.0%, while 12.7% ended with monetary relief. Neither figure describes your firm’s performance.

The key number is 46.1%: 5 of 64 issue categories account for almost half the complaints. That suggests a bounded start rather than asking a model to handle every issue equally well.

The public data tells us where to investigate; your data decides what enters the pilot.

Now let me show you a decision you can inspect.

### Slide 4 — Every decision is visible—and uncertain cases stop

Here is the demo workflow processing 1 public CFPB complaint. It proposes the Disputes and Fraud team, quotes the customer’s words as evidence, and stops for human review.

LangSmith records every evaluation outcome. Of 60 cases, 52 produced a proposal; 4 stopped for low confidence and 4 because the quoted evidence was absent from the complaint.

Those fabricated quotations matter most. Validation caught them and sent each case to human review.

The broader evaluation produced 60.5% team-level agreement against consumer-selected CFPB labels. That is not deployment-quality evidence, and those labels are not expert routing decisions.

The demo is observable, but it does not establish deployment accuracy. Phase 0 creates expert labels from your complaints; Phase 1 measures performance in shadow mode. That is why the proposal is staged.

### Slide 5 — €14,000 to decide, not €24,500 to deploy

The pricing basis is €700 for each of my consulting days, contracted as a fixed fee per phase.

Phase 0 includes 8 of my consulting days, or €5,600. Over 2 weeks, 2 of your handlers label 300 complaints; their time is not included in my fee.

Phase 1 includes 12 of my consulting days, or €8,400. Over 11 weeks, that covers the build and 60-day shadow run. The system proposes; your handlers follow the existing process and do not act on suggestions. Results use the Phase 0 expert labels. Together, Phases 0 and 1 cost €14,000 and reach a decision point.

Phase 2 is contingent on the pilot passing. It includes 15 of my consulting days, or €10,500, taking the full programme to €24,500. This phase is assist-only: your handlers may use proposals, but autonomous routing requires separate approval.

Estimated annual operating cost is €7,400: 8 consultant review days cost €5,600, and the €150 monthly platform costs €1,800. Under the assumed volume, model calls add about €0.29. Accountable operation, not model calls, drives cost.

I am not claiming it will prevent 4 ombudsman referrals a year. The pilot must test that hypothesis.

The ask is €14,000 to reach an evidence-based decision, not €24,500 for a deployment that has not earned approval.

That is my proposal. Thank you. For Round 2, I would most value your view on whether the evidence, controls, and staged investment make Phase 0 a credible next step.

## Appendix for questions — Slides 7–14

### Slide 6 — Supporting evidence

*No spoken notes.*

### Slide 7 — Why complaint triage comes first

I ranked 3 candidate use cases by how visible and controllable their reasoning can be. Only complaint triage is proposed for Phase 0 and Phase 1; anomaly flagging and reporting assistance remain later options.

Complaint triage can propose a team and show the exact evidence behind the proposal. Anomaly flagging can identify unusual patterns for one of your investigators to review. Reporting assistance can draft material while leaving approval with a named employee in your firm.

I ruled out 2 uses. A customer-facing chatbot could make public errors in the firm’s voice. Creditworthiness scoring directly affects access to financial services and is classified as high-risk under the EU AI Act. A separate guardrail prevents predicted payout from determining routing priority.

The point is not to find the most impressive use case. It is to choose a use case whose risks can be bounded and whose decisions can be examined.

### Slide 8 — 5 categories account for 46.1% of complaints

This chart explains how the public data supports a bounded initial test.

In the public dataset, 5 of 64 issue categories account for 46.1% of complaints. That makes it possible to test a narrow, high-volume starting point instead of pretending the model can handle the entire taxonomy equally well.

I would not assume that 46.1% applies to the client. Phase 0 must measure the client’s own concentration and decide which categories belong in the pilot.

The public result is a reason to investigate a focused scope, not a forecast of the client’s complaint book.

### Slide 9 — Complaint volume does not predict monetary relief

This public-data slide separates how often complaints occur from how often they end with monetary relief.

Checking and savings accounts and credit cards produce most of the complaint volume in this dataset. But monetary relief appears in 17.2% of credit-card complaints, compared with 3.0% for vehicle-lending complaints. That is a 5.7× difference.

The implication is that volume alone does not describe likely monetary relief. That relationship is a hypothesis to test, not a routing rule.

This is a signal from public data, not a forecast for the client. The client’s own product mix, resolution costs, and escalation patterns must be measured during discovery and the pilot.

### Slide 10 — All 60 evaluation decisions are accounted for

In the 60-case evaluation sample recorded in LangSmith, 52 complaints produced a proposal after passing the configured validation checks. Passing those checks does not prove that the proposed team was correct.

4 were flagged for human review because the model’s evidence quotation was not present verbatim in the complaint. Another 4 were flagged because confidence was below the threshold.

Every case in the sample has a recorded outcome and a reason code. 0 cases lack a recorded outcome.

This does not prove that every proposal was correct. It proves that proposals and stops can be traced and discussed.

### Slide 11 — 60.5% agreement makes expert labels essential

The 60.5% result should not be interpreted as a clean measure of model accuracy.

When the same model classified the same complaints again, it selected the same team approximately 89% of the time. It was relatively consistent with itself but disagreed much more often with the CFPB label.

The CFPB issue label is selected by the person filing the complaint, using a product-specific menu. It is not an expert judgement about which internal team should handle the case.

The 60.5% result therefore mixes model error with label mismatch; it cannot separate them. Phase 0 resolves that uncertainty by asking experienced handlers to create an expert-labelled reference set and by measuring their agreement with one another.

### Slide 12 — 3 data corrections changed the story

3 data problems could have produced confident but misleading conclusions.

First, recent complaint volume appeared to collapse by 73% because the CFPB publishes complaints only after the company responds or enough time passes. I removed the incomplete period and ended the analysis window on 27 June 2026.

Second, the apparent response-time field was 0 for 96% of records because it measured the regulator’s routing process, not the firm’s handling time. I excluded it.

Third, 2 different timeliness fields created apparently conflicting percentages. I separated their meanings instead of treating them as the same metric.

The lesson is that a field can be complete and still mean the wrong thing for the business question.

### Slide 13 — Human review supports a preliminary compliance view

My Round 1 compliance position is deliberately preliminary. It is not a final legal classification.

This system proposes an internal complaint-routing team. It does not assess creditworthiness, determine access to a financial service, or make the final decision on a customer’s complaint. A human remains responsible for confirming the route and resolving the case.

On that intended use, I have not identified it as matching the Annex III creditworthiness use classified as high-risk. However, classification depends on the exact intended purpose, deployment context, data flows, and degree of human control.

Round 2 therefore needs a step-by-step classification and obligations assessment. If the system begins routing automatically or influencing substantive customer outcomes, that is a new assessment, not a minor product upgrade.

Round 2 must also establish the GDPR legal basis and retention period, decide whether a DPIA is required, and verify the hosting region and cross-border transfer controls. Those controls are open work, not completed safeguards.

### Slide 14 — Every number is measured, sourced, or assumed

Every figure in the pitch fits 1 of 3 categories: measured in this project, taken from a named public source, or explicitly labelled as an assumption or professional judgement.

The complaint analysis comes from the public CFPB dataset. The client-size and complaint-rate estimates use stated FCA benchmarks and scenario assumptions. The model behaviour comes from the project’s own evaluations. The 60.5% figure is agreement with CFPB-derived labels, not expert-routing accuracy. Soft inputs such as minutes per complaint, employer on-costs, and platform cost are labelled as judgements in the cost model.

The purpose of this slide is not to claim certainty. It is to make clear which figures are evidence, which are external benchmarks, and which must be validated during Phase 0 and the pilot.
