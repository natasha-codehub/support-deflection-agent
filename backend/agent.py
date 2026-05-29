import json
import google.generativeai as genai
from config import (
    GEMINI_API_KEY, GEMINI_MODEL, ORG_NAME, ORG_DOMAIN,
    CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, RAG_SCORING_WINDOW,
)
from rag import get_relevant_chunks
from tools import orders_lookup, pod_lookup
from memory import get_history, add_turn

genai.configure(api_key=GEMINI_API_KEY)

TOOL_INTENTS = {"order_status", "pod_lookup"}
ALL_INTENTS = {"order_status", "pod_lookup", "tax_exemption", "refund_dispute", "account_setup", "out_of_scope"}

INTENT_PROMPT = """You are a support query classifier for {org_name}, a {org_domain} company.

Classify the user query into exactly one intent and extract any entities present.

Intents:
- order_status: questions about order location, shipping status, ETA, delivery confirmation
- pod_lookup: requests for proof of delivery documents
- tax_exemption: questions about tax certificates, tax-exempt status, exemption applications
- refund_dispute: short pay claims, billing discrepancies, refund requests, dispute processes
- account_setup: account management, adding users, account manager contact, billing email, payment terms, delivery locations
- out_of_scope: anything not covered above

Entities to extract (use null if not present):
- order_id: format ORD-XXXX
- account_id: format ACC-XXXX
- location_name: city or site name mentioned
- invoice_number: format INV-XXXX

Respond with valid JSON only, no markdown:
{{"intent": "<intent>", "entities": {{"order_id": null, "account_id": null, "location_name": null, "invoice_number": null}}}}\

Query: {query}"""

RESPONSE_PROMPT = """You are a support agent for {org_name}, a {org_domain} company.

Answer ONLY from the provided context below. If the context is insufficient, say so explicitly. Never fabricate order details, policy rules, or contact information.

When citing information, reference the source document name naturally (e.g., "According to our tax exemption policy...").

Context from knowledge base:
{kb_context}

{tool_context}

Conversation history:
{history}

User query: {query}

Respond concisely and helpfully. If you cannot answer from the context, say: "I don't have enough information to answer that accurately. Let me connect you with our support team."
"""


def _call_gemini(prompt: str) -> str:
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()


def _score_confidence(chunks: list[dict]) -> float:
    if not chunks:
        return 0.0
    window = chunks[:RAG_SCORING_WINDOW]
    scores = [c["score"] for c in window]
    return round(sum(scores) / len(scores), 4)


def _assign_tier(score: float) -> str:
    if score >= CONFIDENCE_HIGH:
        return "high"
    if score >= CONFIDENCE_MEDIUM:
        return "medium"
    return "low"


def classify_intent(query: str) -> dict:
    prompt = INTENT_PROMPT.format(org_name=ORG_NAME, org_domain=ORG_DOMAIN, query=query)
    try:
        raw = _call_gemini(prompt)
        # Strip markdown fences if present
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(raw)
    except Exception:
        return {
            "intent": "out_of_scope",
            "entities": {"order_id": None, "account_id": None, "location_name": None, "invoice_number": None},
        }


def run_agent(session_id: str, message: str) -> dict:
    # Step 1: classify intent
    classification = classify_intent(message)
    intent = classification.get("intent", "out_of_scope")
    entities = classification.get("entities", {})

    # Step 2: out_of_scope → immediate escalation
    if intent == "out_of_scope":
        add_turn(session_id, "user", message)
        add_turn(session_id, "assistant", "[escalated: out of scope]")
        return {
            "reply": "",
            "tier": "low",
            "confidence_score": 0.0,
            "intent": intent,
            "sources": [],
            "escalated": True,
            "escalation_reason": "Query type not in scope for automated support",
            "tool_used": None,
        }

    # Step 3: RAG retrieval
    try:
        chunks = get_relevant_chunks(message)
    except Exception:
        chunks = []

    # Step 4: tool call (conditional)
    tool_result = None
    tool_used = None
    if intent in TOOL_INTENTS:
        order_id = entities.get("order_id")
        if order_id:
            if intent == "order_status":
                tool_result = orders_lookup(order_id)
                tool_used = "orders_lookup"
            elif intent == "pod_lookup":
                tool_result = pod_lookup(order_id)
                tool_used = "pod_lookup"

    # Step 5: confidence scoring
    confidence = _score_confidence(chunks)
    # If tool returned a result, boost confidence for data-backed answers
    if tool_result is not None:
        confidence = max(confidence, CONFIDENCE_HIGH)
    tier = _assign_tier(confidence)

    # Step 6: escalate if low confidence
    if tier == "low":
        add_turn(session_id, "user", message)
        add_turn(session_id, "assistant", "[escalated: low confidence]")
        return {
            "reply": "",
            "tier": "low",
            "confidence_score": confidence,
            "intent": intent,
            "sources": [],
            "escalated": True,
            "escalation_reason": "Query not covered with sufficient confidence in knowledge base",
            "tool_used": tool_used,
        }

    # Step 7: build response prompt
    kb_context = "\n\n---\n".join(
        f"[Source: {c['metadata']['source_file']}]\n{c['text']}" for c in chunks
    ) or "No relevant KB context found."

    tool_context = ""
    if tool_result:
        tool_context = f"TOOL RESULT ({tool_used}):\n{json.dumps(tool_result, indent=2)}"

    history = get_history(session_id)
    history_text = "\n".join(f"{t['role'].upper()}: {t['content']}" for t in history[-6:]) or "None"

    prompt = RESPONSE_PROMPT.format(
        org_name=ORG_NAME,
        org_domain=ORG_DOMAIN,
        kb_context=kb_context,
        tool_context=tool_context,
        history=history_text,
        query=message,
    )

    try:
        reply = _call_gemini(prompt)
    except Exception as e:
        add_turn(session_id, "user", message)
        add_turn(session_id, "assistant", "[escalated: service error]")
        return {
            "reply": "",
            "tier": "low",
            "confidence_score": 0.0,
            "intent": intent,
            "sources": [],
            "escalated": True,
            "escalation_reason": "Service temporarily unavailable",
            "tool_used": tool_used,
        }

    # Add disclaimer for medium tier
    if tier == "medium":
        reply += "\n\n*Based on our policy documentation — please verify with your account team for account-specific details.*"

    add_turn(session_id, "user", message)
    add_turn(session_id, "assistant", reply)

    sources = [
        {"file": c["metadata"]["source_file"], "section": ""}
        for c in chunks[:3]
    ]
    # Deduplicate sources by file
    seen = set()
    unique_sources = []
    for s in sources:
        if s["file"] not in seen:
            seen.add(s["file"])
            unique_sources.append(s)

    return {
        "reply": reply,
        "tier": tier,
        "confidence_score": confidence,
        "intent": intent,
        "sources": unique_sources,
        "escalated": False,
        "escalation_reason": None,
        "tool_used": tool_used,
    }
