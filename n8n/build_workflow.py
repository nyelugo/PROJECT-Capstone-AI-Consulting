"""Generate n8n/workflow.json from the tested prompt and taxonomy.

The workflow is GENERATED, never hand-edited, so the prompt running in n8n is byte-for-byte
the prompt measured in classifier/evaluate.py. Editing the JSON by hand would let the demo
drift away from the evidence.

Run: python n8n/build_workflow.py
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LANGSMITH_ENDPOINT = "https://eu.api.smith.langchain.com"   # EU workspace
LANGSMITH_PROJECT = "capstone-triage-live"                  # tracing project, not the eval
sys.path.insert(0, str(ROOT / "classifier"))
import decide as D            # noqa: E402
import prompt as P            # noqa: E402
import teams as T             # noqa: E402

# A real complaint from the corpus, so the demo runs on genuine text.
df = pd.read_csv(ROOT / "data" / "complaints_triage.csv.gz")
row = df[(df["Product"] == "Checking or savings account")
         & (df["Consumer complaint narrative"].str.len().between(500, 1100))
         ].sample(1, random_state=11).iloc[0]
SAMPLE_PRODUCT = str(row["Product"])
SAMPLE_NARRATIVE = str(row["Consumer complaint narrative"])
SAMPLE_TRUTH = str(row["Issue"])


# Input validation at the boundary. The output guards check what the MODEL says; this
# checks what the CALLER says, which matters more for the webhook - that entry point is
# untrusted. Rejecting here costs nothing; rejecting after the classifier costs an API
# call to reach a conclusion that was knowable up front.
NORMALISE_CODE = """// Validate and normalise the incoming complaint BEFORE any model call.
// Both entry points converge here: the manual demo item, and the webhook body.
const TAXONOMY = %s;
const MIN_CHARS = 20;
const MAX_CHARS = 6000;

const src = $input.first().json;
const raw = src.body ?? src;                       // webhook nests under .body

const clean = (v) => (typeof v === 'string' ? v.trim() : v);
const product   = clean(raw.product);
let   narrative = clean(raw.narrative);

const reject = (why) => {
  // Fail fast and loudly. No model call is made, so a malformed request costs nothing.
  throw new Error('REJECT_INVALID_INPUT: ' + why);
};

if (typeof product !== 'string' || !product)  reject('product is missing or not a string');
if (!(product in TAXONOMY))                   reject(`unknown product ${JSON.stringify(product)} - expected one of: ${Object.keys(TAXONOMY).join(', ')}`);
if (typeof narrative !== 'string' || !narrative) reject('narrative is missing or not a string');
if (narrative.length < MIN_CHARS)             reject(`narrative is ${narrative.length} characters; at least ${MIN_CHARS} are needed to classify`);

if (narrative.length > MAX_CHARS) narrative = narrative.slice(0, MAX_CHARS);

return [{ json: { product, narrative, narrative_chars: narrative.length, t0: Date.now() } }];
""" % json.dumps(P.PRODUCT_QUEUES)

PARSE_CODE = """// Parse the model's answer, then validate it before trusting it.
// Reason CODES and their order are generated from classifier/decide.py so the n8n POC and
// the LangSmith monitoring can never describe the same rejection differently.
const TAXONOMY = %s;
const QUEUE_TO_TEAM = %s;
const THRESHOLD = %s;
const REASONS = %s;

const input = $('Normalise complaint').first().json;
const product = input.product;
const raw = $input.first().json.choices?.[0]?.message?.content ?? '{}';

let parsed = {}, malformed = false;
try { parsed = JSON.parse(raw); } catch (e) { malformed = true; }

const queue = String(parsed.queue ?? '');
const confidence = Number(parsed.confidence ?? 0);
const evidence = String(parsed.evidence ?? '');

const validQueues = TAXONOMY[product] ?? ['OTHER'];
const queueIsValid = validQueues.includes(queue);
// The quote must actually appear in the complaint. A fabricated quote manufactures false
// justification, which is worse than giving no justification at all.
const evidenceIsVerbatim = evidence.length > 0 &&
  input.narrative.toLowerCase().includes(evidence.slice(0, 60).toLowerCase());

// Guard order is declared, not emergent. A complaint failing two guards is always
// reported under the first, so the reason-code distribution stays comparable over time.
let code;
if (malformed)                   code = 'REJECT_MALFORMED_OUTPUT';
else if (!queueIsValid)          code = 'REJECT_QUEUE_NOT_IN_PRODUCT';
else if (queue === 'OTHER')      code = 'REJECT_OUT_OF_TAXONOMY';
else if (confidence < THRESHOLD) code = 'REJECT_LOW_CONFIDENCE';
else if (!evidenceIsVerbatim)    code = 'REJECT_EVIDENCE_NOT_VERBATIM';
else                             code = 'OK_PROPOSED';

const decision = code === 'OK_PROPOSED' ? 'PROPOSE_TO_HANDLER' : 'HUMAN_REVIEW';

return [{ json: {
  product,
  proposed_queue: queueIsValid ? queue : null,
  proposed_team: code === 'OK_PROPOSED' ? (QUEUE_TO_TEAM[queue] ?? 'HUMAN_REVIEW') : 'HUMAN_REVIEW',
  confidence,
  evidence,
  evidence_is_verbatim: evidenceIsVerbatim,
  decision,
  reason_code: code,
  reason: REASONS[code],
  narrative: input.narrative,
}}];
""" % (json.dumps(P.PRODUCT_QUEUES), json.dumps(T.QUEUE_TO_TEAM), P.CONFIDENCE_THRESHOLD, json.dumps(D.REASONS))


def node(name, ntype, tv, pos, params, **extra):
    n = {"parameters": params, "id": name.lower().replace(" ", "-"), "name": name,
         "type": ntype, "typeVersion": tv, "position": pos}
    n.update(extra)
    return n


nodes = [
    node("Run demo", "n8n-nodes-base.manualTrigger", 1, [-560, 60], {}),
    node("Complaint received", "n8n-nodes-base.webhook", 2, [-560, 260], {
        "httpMethod": "POST", "path": "complaint-triage",
        "responseMode": "lastNode", "options": {}}),
    node("Sample complaint", "n8n-nodes-base.set", 3.4, [-340, 60], {
        "assignments": {"assignments": [
            {"id": "p", "name": "product", "value": SAMPLE_PRODUCT, "type": "string"},
            {"id": "n", "name": "narrative", "value": SAMPLE_NARRATIVE, "type": "string"}]},
        "options": {}}),
    node("Normalise complaint", "n8n-nodes-base.code", 2, [-120, 160], {
        "jsCode": NORMALISE_CODE}),
    node("Classify complaint", "n8n-nodes-base.httpRequest", 4.2, [100, 160], {
        "method": "POST", "url": "https://api.openai.com/v1/chat/completions",
        "authentication": "predefinedCredentialType", "nodeCredentialType": "openAiApi",
        "sendBody": True, "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n"
                    f"  model: {json.dumps(P.MODEL)},\n"
                    "  temperature: 0,\n"
                    "  response_format: { type: 'json_object' },\n"
                    "  messages: [\n"
                    f"    {{ role: 'system', content: {json.dumps(P.SYSTEM_PROMPT)} }},\n"
                    "    { role: 'user', content: 'Product: ' + $json.product + "
                    "'\\n\\nQueues available for this product:\\n' + "
                    f"({json.dumps(P.PRODUCT_QUEUES)}[$json.product] || ['OTHER'])"
                    ".map(q => '- ' + q).join('\\n') + "
                    "'\\n\\nComplaint:\\n' + $json.narrative }\n"
                    "  ]\n}) }}",
        "options": {}},
         credentials={"openAiApi": {
             "id": os.environ.get("N8N_OPENAI_CREDENTIAL_ID", "SET_ON_IMPORT"),
             "name": os.environ.get("N8N_OPENAI_CREDENTIAL_NAME", "Ugo_OpenAI")}}),
    node("Validate and route", "n8n-nodes-base.code", 2, [320, 160], {
        "jsCode": PARSE_CODE}),
    node("Trace to LangSmith", "n8n-nodes-base.httpRequest", 4.2, [560, 400], {
        "method": "POST", "url": LANGSMITH_ENDPOINT + "/runs",
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendBody": True, "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n"
                    # LangSmith requires a 32-hex or UUID run id; an execution id with a
                    # timestamp appended is rejected with 422.
                    "  id: Array.from({length:32},()=>Math.floor(Math.random()*16).toString(16)).join(''),\n"
                    "  name: 'complaint_triage_n8n',\n"
                    "  run_type: 'chain',\n"
                    "  start_time: new Date($('Normalise complaint').item.json.t0).toISOString(),\n"
                    "  end_time: new Date().toISOString(),\n"
                    f"  session_name: {json.dumps(LANGSMITH_PROJECT)},\n"
                    "  inputs: { product: $json.product, narrative_chars: ($json.narrative || '').length },\n"
                    "  outputs: {\n"
                    "    decision: $json.decision, reason_code: $json.reason_code,\n"
                    "    proposed_team: $json.proposed_team, proposed_queue: $json.proposed_queue,\n"
                    "    confidence: $json.confidence, evidence_is_verbatim: $json.evidence_is_verbatim,\n"
                    # The quote the model relied on. Without it, monitoring can say a
                    # decision passed the verbatim check but not what the check passed —
                    # and the quote is the answer to "why was this routed here?".
                    # NOTE: this is a fragment of customer text. Public CFPB data here;
                    # sending it in production is a Round 2 GDPR decision, not a default.
                    "    evidence: $json.evidence,\n"
                    "    environment: 'demo', source: 'n8n'\n"
                    "  }\n"
                    "}) }}",
        "options": {}},
         # Observing must never affect the observed: if LangSmith is unreachable the
         # complaint still gets routed. Telemetry is fire-and-forget.
         onError="continueRegularOutput",
         credentials={"httpHeaderAuth": {
             "id": os.environ.get("N8N_LANGSMITH_CREDENTIAL_ID", "SET_ON_IMPORT"),
             "name": os.environ.get("N8N_LANGSMITH_CREDENTIAL_NAME", "Ugo_LangSmith")}}),
    node("Safe to propose?", "n8n-nodes-base.if", 2, [760, 160], {
        "conditions": {"options": {"caseSensitive": True, "version": 2},
                       "combinator": "and",
                       "conditions": [{"id": "c1",
                                       "leftValue": "={{ $json.decision }}",
                                       "rightValue": "PROPOSE_TO_HANDLER",
                                       "operator": {"type": "string", "operation": "equals"}}]},
        "options": {}}),
    node("Propose to handler", "n8n-nodes-base.set", 3.4, [1000, 60], {
        "assignments": {"assignments": [
            {"id": "a", "name": "outcome", "value": "PROPOSED", "type": "string"},
            {"id": "b", "name": "team", "value": "={{ $json.proposed_team }}", "type": "string"},
            {"id": "c", "name": "queue", "value": "={{ $json.proposed_queue }}", "type": "string"},
            {"id": "d", "name": "why_this_team", "value": "={{ $json.evidence }}", "type": "string"},
            {"id": "e", "name": "confidence", "value": "={{ $json.confidence }}", "type": "number"},
            {"id": "f", "name": "handler_action",
             "value": "Confirm or override. The complaint is not routed until you do.",
             "type": "string"}]},
        "options": {}}),
    node("Send to human review", "n8n-nodes-base.set", 3.4, [1000, 280], {
        "assignments": {"assignments": [
            {"id": "a", "name": "outcome", "value": "HUMAN_REVIEW", "type": "string"},
            {"id": "b", "name": "team", "value": "Unassigned — needs a person", "type": "string"},
            {"id": "c", "name": "why_no_proposal", "value": "={{ $json.reason }}", "type": "string"},
            {"id": "r", "name": "reason_code", "value": "={{ $json.reason_code }}", "type": "string"},
            {"id": "d", "name": "confidence", "value": "={{ $json.confidence }}", "type": "number"}]},
        "options": {}}),
]

connections = {
    "Run demo": {"main": [[{"node": "Sample complaint", "type": "main", "index": 0}]]},
    "Sample complaint": {"main": [[{"node": "Normalise complaint", "type": "main", "index": 0}]]},
    "Complaint received": {"main": [[{"node": "Normalise complaint", "type": "main", "index": 0}]]},
    "Normalise complaint": {"main": [[{"node": "Classify complaint", "type": "main", "index": 0}]]},
    "Classify complaint": {"main": [[{"node": "Validate and route", "type": "main", "index": 0}]]},
    # Fan-out: the routing decision and the telemetry leave the same output in parallel.
    # Tracing is a leaf - nothing downstream reads its response - so if LangSmith is slow,
    # unreachable or returns rubbish, the complaint is routed exactly as it would have been.
    "Validate and route": {"main": [[
        {"node": "Safe to propose?", "type": "main", "index": 0},
        {"node": "Trace to LangSmith", "type": "main", "index": 0},
    ]]},
    "Safe to propose?": {"main": [
        [{"node": "Propose to handler", "type": "main", "index": 0}],
        [{"node": "Send to human review", "type": "main", "index": 0}]]},
}

wf = {"name": "Capstone — Complaint Triage POC (assist-only)",
      "nodes": nodes, "connections": connections,
      "settings": {"executionOrder": "v1"}, "pinData": {}}

out = Path(__file__).parent / "workflow.json"
out.write_text(json.dumps(wf, indent=2))
print(f"wrote {out}  ({len(nodes)} nodes)")
print(f"sample complaint: {SAMPLE_PRODUCT} | true label: {SAMPLE_TRUTH} | "
      f"{len(SAMPLE_NARRATIVE)} chars")
(Path(__file__).parent / "sample_complaint.json").write_text(json.dumps(
    {"product": SAMPLE_PRODUCT, "narrative": SAMPLE_NARRATIVE,
     "cfpb_label": SAMPLE_TRUTH}, indent=2))
