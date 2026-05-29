from datetime import datetime
from collections import defaultdict

_escalation_log: list[dict] = []
_query_log: list[dict] = []

# Seeded demo data so the analytics panel is populated on first load
_query_log = [
    {"session_id": "demo-1", "intent": "order_status", "tier": "high", "confidence": 0.91, "escalated": False, "ts": "2026-05-28T10:12:00"},
    {"session_id": "demo-1", "intent": "pod_lookup", "tier": "high", "confidence": 0.88, "escalated": False, "ts": "2026-05-28T10:13:00"},
    {"session_id": "demo-2", "intent": "tax_exemption", "tier": "high", "confidence": 0.93, "escalated": False, "ts": "2026-05-28T11:00:00"},
    {"session_id": "demo-3", "intent": "refund_dispute", "tier": "medium", "confidence": 0.72, "escalated": False, "ts": "2026-05-28T11:30:00"},
    {"session_id": "demo-4", "intent": "account_setup", "tier": "high", "confidence": 0.85, "escalated": False, "ts": "2026-05-28T12:00:00"},
    {"session_id": "demo-5", "intent": "out_of_scope", "tier": "low", "confidence": 0.41, "escalated": True, "ts": "2026-05-28T12:15:00"},
    {"session_id": "demo-6", "intent": "order_status", "tier": "high", "confidence": 0.90, "escalated": False, "ts": "2026-05-29T09:00:00"},
    {"session_id": "demo-7", "intent": "tax_exemption", "tier": "medium", "confidence": 0.68, "escalated": False, "ts": "2026-05-29T09:30:00"},
    {"session_id": "demo-8", "intent": "refund_dispute", "tier": "low", "confidence": 0.58, "escalated": True, "ts": "2026-05-29T10:00:00"},
    {"session_id": "demo-9", "intent": "account_setup", "tier": "high", "confidence": 0.87, "escalated": False, "ts": "2026-05-29T10:45:00"},
]


def log_query(session_id: str, intent: str, tier: str, confidence: float, escalated: bool):
    _query_log.append({
        "session_id": session_id,
        "intent": intent,
        "tier": tier,
        "confidence": confidence,
        "escalated": escalated,
        "ts": datetime.utcnow().isoformat(),
    })


def log_escalation(session_id: str, intent: str, reason: str, query: str):
    _escalation_log.append({
        "session_id": session_id,
        "intent": intent,
        "reason": reason,
        "query": query,
        "ts": datetime.utcnow().isoformat(),
    })


def get_analytics() -> dict:
    total = len(_query_log)
    if total == 0:
        return {
            "total_queries": 0,
            "deflected": 0,
            "escalated": 0,
            "deflection_rate": 0.0,
            "avg_confidence": 0.0,
            "escalated_intents": [],
        }
    escalated = sum(1 for q in _query_log if q["escalated"])
    deflected = total - escalated
    avg_conf = sum(q["confidence"] for q in _query_log) / total

    intent_counts: dict[str, int] = defaultdict(int)
    for q in _query_log:
        if q["escalated"]:
            intent_counts[q["intent"]] += 1

    return {
        "total_queries": total,
        "deflected": deflected,
        "escalated": escalated,
        "deflection_rate": round(deflected / total, 3),
        "avg_confidence": round(avg_conf, 3),
        "escalated_intents": [{"intent": k, "count": v} for k, v in intent_counts.items()],
    }
