from app.tools.customer import (
    get_customer,
    get_transactions,
)


def test_customer_001_transactions():
    result = get_transactions("cliente001")

    transaction_ids = [
        tx["id"]
        for tx in result["transactions"]
    ]

    assert "TX001" in transaction_ids
    assert "TX002" in transaction_ids
    assert "TX003" not in transaction_ids


def test_customer_002_transactions():
    result = get_transactions("cliente002")

    transaction_ids = [
        tx["id"]
        for tx in result["transactions"]
    ]

    assert "TX003" in transaction_ids
    assert "TX001" not in transaction_ids
    assert "TX002" not in transaction_ids


def test_unknown_customer():
    result = get_customer("cliente999")

    assert result["error"] == "Customer not found"


def test_unknown_customer_transactions():
    result = get_transactions("cliente999")

    assert "error" in result
    assert "transactions" not in result
