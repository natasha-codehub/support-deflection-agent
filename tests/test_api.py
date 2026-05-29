import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("ORG_NAME", "AcmeCo Industrial")
os.environ.setdefault("ORG_DOMAIN", "B2B industrial gas distribution")

from fastapi.testclient import TestClient


def get_client():
    from main import app
    return TestClient(app)


def test_health():
    client = get_client()
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "chroma_collection_size" in data
    assert data["chroma_collection_size"] > 0


def test_chat_happy_path_order_status():
    client = get_client()
    res = client.post(
        "/chat",
        json={"session_id": "test-session-1", "message": "Where is my order ORD-4521?"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["tier"] in ("high", "medium", "low")
    assert "confidence_score" in data
    assert "intent" in data
    assert data["session_id"] == "test-session-1"
    assert isinstance(data["sources"], list)


def test_chat_escalation_out_of_scope():
    client = get_client()
    res = client.post(
        "/chat",
        json={"session_id": "test-session-2", "message": "Can you book me a flight to Chicago?"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["escalated"] is True
    assert data["tier"] == "low"
    assert data["escalation_reason"] is not None


def test_analytics_returns_counts():
    client = get_client()
    # Seed some queries
    client.post("/chat", json={"session_id": "test-sess-3", "message": "How do I submit a tax cert?"})
    client.post("/chat", json={"session_id": "test-sess-4", "message": "What is the weather today?"})

    res = client.get("/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_queries"] > 0
    assert 0.0 <= data["deflection_rate"] <= 1.0


def test_tools_orders_lookup():
    from tools import orders_lookup, pod_lookup
    order = orders_lookup("ORD-4521")
    assert order is not None
    assert order["order_id"] == "ORD-4521"
    assert order["status"] == "In Transit"

    missing = orders_lookup("ORD-9999")
    assert missing is None


def test_tools_pod_lookup():
    from tools import pod_lookup
    pod = pod_lookup("ORD-4522")
    assert pod is not None
    assert "pod_url" in pod

    no_pod = pod_lookup("ORD-4521")
    assert no_pod is None


def test_confidence_scoring():
    from agent import _score_confidence, _assign_tier
    chunks_high = [{"score": 0.92}, {"score": 0.88}, {"score": 0.85}]
    assert _assign_tier(_score_confidence(chunks_high)) == "high"

    chunks_medium = [{"score": 0.75}, {"score": 0.70}, {"score": 0.68}]
    assert _assign_tier(_score_confidence(chunks_medium)) == "medium"

    chunks_low = [{"score": 0.50}, {"score": 0.45}]
    assert _assign_tier(_score_confidence(chunks_low)) == "low"

    assert _score_confidence([]) == 0.0
