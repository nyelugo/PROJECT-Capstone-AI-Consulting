# Round 1 Presentation — Clean Speaker Notes

## Main presentation — Slides 1–5

### Slide 1 — See exactly what the AI does

We met over dinner, and you told me you do not trust AI because you cannot see what it does.

So I am not asking you to believe a promise. I am going to show you a single decision from start to finish.

The workflow runs, its reasoning is visible, and every number traces back to the project evidence.

### Slide 2 — A mid-size bank needs AI it can inspect

You asked 2 questions: what exactly is the AI, and how would you see what it is doing?

I considered 3 use cases: complaint triage, anomaly flagging, and reporting assistance. I ranked them by how clearly we can inspect the reasoning, not by the largest promised saving.

Triage comes first because we can watch the decision. The system proposes a team, shows the supporting words, and lets a person confirm or reject it.

I am ruling out a chatbot because it can fail publicly in the firm’s voice. I am ruling out credit scoring because it is an Annex III high-risk use under the EU AI Act.

The fastest way to earn your trust is to be clear about what you should not buy.

Now let me show you the opportunity in real complaint data.

### Slide 3 — 4 numbers define the opportunity

This dashboard uses public CFPB data as a proxy. These are not your firm’s numbers; Phase 0 measures your real complaint mix and volume.

The analysis contains 16,839 complaints. 98.0% received a timely response, while 12.7% ended with monetary relief.

The key number is 46.1%: 5 of 64 issue categories account for almost half of the complaints. That suggests a bounded starting point instead of asking a model to handle every issue equally well.

The public data tells us where to investigate. Your own data decides what enters the pilot.

Now let me show you a decision you can inspect.

### Slide 4 — Every decision is visible—and uncertain cases stop

Here is the workflow processing a real complaint. It proposes the Disputes and Fraud team, quotes the customer’s words as evidence, and stops for a person to confirm.

The monitoring view records every decision. Of 60 cases, 52 produced a proposal. 4 stopped for low confidence, and 4 because the quoted evidence was not in the complaint.

Those fabricated quotations matter most. The model sounded convincing, but the validation check caught them and sent each case to human review.

The broader evaluation produced 60.5% team-level agreement against consumer-selected CFPB labels. That is not deployment-quality evidence, and those labels are not expert routing decisions.

The process runs and can be observed. Accuracy must now be measured against the client’s expert-labelled complaints. That is why the proposal is staged.

### Slide 5 — €14,000 to decide, not €24,500 to deploy

The proposal uses a fixed fee for each phase because the problem is uncertainty.

Phase 0 costs €5,600. 2 experienced handlers label 300 complaints independently, creating the trustworthy reference set we need.

Phase 1 costs €8,400 and runs an assist-only pilot beside the existing process. Together, the phases cost €14,000 and reach a real decision point.

Annual operation is estimated at €7,400, almost entirely for human oversight and the platform. Under the stated assumptions, the model calls cost about €0.29 per year. The model is not the expensive part; accountable operation is.

I am not claiming it will prevent 4 ombudsman referrals a year. The pilot must test that hypothesis.

The ask is €14,000 to reach an evidence-based decision, not €24,500 for a deployment that has not earned approval.

That is my proposal. Thank you. For Round 2, I would most value your view on whether the evidence, controls, and staged investment make Phase 0 a credible next step.

## Appendix for questions — Slides 6–13

### Slide 6 — Why complaint triage comes first

I ranked the 3 proposed use cases by how visible and controllable their reasoning can be.

Complaint triage can propose a team and show the exact evidence behind the proposal. Anomaly flagging can identify unusual patterns for a person to investigate. Reporting assistance can draft material while leaving approval with a named employee.

I ruled out 2 uses. A customer-facing chatbot could make public errors in the firm’s voice. Credit scoring directly affects access to financial services and is classified as high-risk under the EU AI Act.

The point is not to find the most impressive use case. It is to choose a use case whose risks can be bounded and whose decisions can be examined.

### Slide 7 — 5 categories account for 46.1% of complaints

This chart explains how I bounded the initial scope.

In the public dataset, 5 of 64 issue categories account for 46.1% of complaints. That makes it possible to test a narrow, high-volume starting point instead of pretending the model can handle the entire taxonomy equally well.

I would not assume that 46.1% applies to the client. Phase 0 must measure the client’s own concentration and decide which categories belong in the pilot.

The public result is a reason to investigate a focused scope, not a forecast of the client’s complaint book.

### Slide 8 — Complaint volume does not predict monetary relief

This slide separates how often complaints occur from how consequential they may be.

Checking and savings accounts and credit cards produce most of the complaint volume in this dataset. But monetary relief appears in 17.2% of credit-card complaints, compared with 3.0% for vehicle-lending complaints. That is a 5.7× difference.

The implication is that routing priorities should not be based on volume alone. Product type and likely consequence also matter.

This is a signal from public data, not a forecast for the client. The client’s own product mix, resolution costs, and escalation patterns must be measured during discovery and the pilot.

### Slide 9 — All 60 monitored decisions are accounted for

In the 60-case monitoring sample, 52 complaints passed all validation checks and produced a proposal.

4 were sent to human review because the model’s evidence quotation was not present verbatim in the complaint. Another 4 were sent to human review because confidence was below the threshold.

Every case in the sample has a recorded outcome and a reason code. 0 cases disappeared into an unexplained bucket.

This does not prove that every proposal was correct. It proves that proposals, rejections, and non-decisions can all be traced and discussed.

### Slide 10 — 60.5% agreement makes expert labels essential

The 60.5% result should not be interpreted as a clean measure of model accuracy.

When the same model classified the same complaints again, it selected the same team approximately 89% of the time. It was relatively consistent with itself but disagreed much more often with the CFPB label.

The CFPB issue label is selected by the person filing the complaint, using a product-specific menu. It is not an expert judgement about which internal team should handle the case.

This suggests label quality is a major measurement bottleneck, but it does not prove that the model is correct. Phase 0 resolves that uncertainty by asking experienced handlers to create an expert-labelled reference set and by measuring their agreement with one another.

### Slide 11 — 3 data corrections changed the story

3 data problems could have produced confident but misleading conclusions.

First, recent complaint volume appeared to collapse by 73% because the regulator publishes complaints only after the company responds or enough time passes. I removed the incomplete period and ended the analysis window on 27 June.

Second, the apparent response-time field was 0 for 96% of records because it measured the regulator’s routing process, not the firm’s handling time. I excluded it.

Third, 2 different timeliness fields created apparently conflicting percentages. I separated their meanings instead of treating them as the same metric.

The lesson is that a field can be complete and still mean the wrong thing for the business question.

### Slide 12 — Human review bounds the compliance position

My Round 1 compliance position is deliberately preliminary.

This system proposes an internal complaint-routing team. It does not assess creditworthiness, determine access to a financial service, or make the final decision on a customer’s complaint. A human remains responsible for confirming the route and resolving the case.

On that intended use, I do not currently see it matching the Annex III creditworthiness use that is classified as high-risk. However, classification depends on the exact intended purpose, deployment context, data flows, and degree of human control.

Round 2 therefore needs a step-by-step classification and obligations assessment. If the system begins routing automatically or influencing substantive customer outcomes, that is a new assessment, not a minor product upgrade.

### Slide 13 — Every number is measured, sourced, or assumed

Every figure in the pitch fits 1 of 3 categories: measured in this project, taken from a named public source, or explicitly labelled as an assumption or professional judgement.

The complaint analysis comes from the public CFPB dataset. The client-size and complaint-rate estimates use stated FCA benchmarks and scenario assumptions. The model behaviour comes from the project’s own evaluations. Soft inputs such as minutes per complaint, employer on-costs, and platform cost are labelled as judgements in the cost model.

The purpose of this slide is not to claim certainty. It is to make clear which figures are evidence, which are external benchmarks, and which must be validated during Phase 0 and the pilot.
