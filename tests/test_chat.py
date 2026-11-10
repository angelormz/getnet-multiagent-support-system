
from fastapi.testclient import TestClient

from app.main import app
from app.agents.router import RouteDecision
from app.agents.escalation import (evaluate_escalation,handle_escalation,)


client = TestClient(app)


def mock_route(monkeypatch, route):
    monkeypatch.setattr(
        "app.main.route_message",
        lambda message: RouteDecision(route=route),
    )


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_knowledge(monkeypatch):
    mock_route(monkeypatch, "knowledge")

    monkeypatch.setattr(
        "app.main.handle_knowledge",
        lambda message: {
            "answer": "Get Smart accepts Visa.",
            "sources": ["https://www.getnet.net/mx/"],
            "status": "success",
        },
    )

    response = client.post(
        "/chat",
        json={
            "message": "What cards does Get Smart accept?",
            "user_id": "cliente001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["agents_used"] == [
        "router",
        "knowledge",
    ]
    assert data["status"] == "success"
    assert len(data["sources"]) == 1


def test_support(monkeypatch):
    mock_route(monkeypatch, "support")

    monkeypatch.setattr(
        "app.main.handle_support",
        lambda message, user_id: {
            "answer": "TX001 deposit is pending.",
            "status": "success",
        },
    )

    response = client.post(
        "/chat",
        json={
            "message": "Check transaction TX001",
            "user_id": "cliente001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["agents_used"] == [
        "router",
        "support",
    ]
    assert "TX001" in data["answer"]


def test_both(monkeypatch):
    mock_route(monkeypatch, "both")

    monkeypatch.setattr(
        "app.main.handle_support",
        lambda message, user_id: {
            "answer": "TX001 deposit is pending.",
            "status": "success",
        },
    )

    monkeypatch.setattr(
        "app.main.handle_knowledge",
        lambda message: {
            "answer": "Getnet Portal provides reports.",
            "sources": ["https://www.getnet.net/mx/"],
            "status": "success",
        },
    )

    response = client.post(
        "/chat",
        json={
            "message": "Check TX001 and Getnet Portal",
            "user_id": "cliente001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["agents_used"] == [
        "router",
        "support",
        "knowledge",
    ]
    assert "TX001" in data["answer"]
    assert "Getnet Portal" in data["answer"]
    assert data["status"] == "success"


def test_invalid_message():
    response = client.post(
        "/chat",
        json={
            "message": "",
            "user_id": "cliente001",
        },
    )

    assert response.status_code == 422


def test_missing_user_id():
    response = client.post(
        "/chat",
        json={
            "message": "Hello",
        },
    )

    assert response.status_code == 422


def test_both_partial_information(monkeypatch):
    mock_route(monkeypatch, "both")

    monkeypatch.setattr(
        "app.main.handle_support",
        lambda message, user_id: {
            "answer": "TX001 deposit is pending.",
            "status": "success",
        },
    )

    monkeypatch.setattr(
        "app.main.handle_knowledge",
        lambda message: {
            "answer": "No documentation found.",
            "sources": [],
            "status": "insufficient_information",
        },
    )

    response = client.post(
        "/chat",
        json={
            "message": "Check TX001 and policies",
            "user_id": "cliente001",
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["status"]
        == "insufficient_information"
    )

# TEST 8: Detectar una solicitud de escalamiento
def test_escalation_detection():

    result = evaluate_escalation(
        "Tengo un cargo no reconocido."
    )

    assert result["requires_escalation"] is True
    assert result["reason"] == "suspected_fraud"


# TEST 9: Verificar el endpoint de escalamiento
def test_escalation_endpoint(monkeypatch):

    def fake_create_ticket(user_id, message, reason):
        return {
            "ticket_id": "ESC-TEST1234",
            "status": "pending_human_review",
            "reason": reason,
        }

    monkeypatch.setattr(
        "app.agents.escalation.create_ticket",
        fake_create_ticket,
    )

    response = client.post(
        "/chat",
        json={
            "message": (
                "Tengo un cargo no reconocido "
                "y necesito hablar con una persona."
            ),
            "user_id": "cliente001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "pending_human_review"
    assert data["agents_used"] == ["escalation"]
    assert "ESC-TEST1234" in data["answer"]


# TEST 10: Verificar que no se escala una consulta normal
def test_no_escalation():

    result = evaluate_escalation(
        "¿Qué tarjetas acepta Get Smart?"
    )

    assert result["requires_escalation"] is False
    assert result["reason"] is None
