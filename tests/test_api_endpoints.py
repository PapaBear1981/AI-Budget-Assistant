import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers import health, transactions, budgets, bills
from backend.core.database import init_db
from backend.core.auth import AuthService, get_current_user


@pytest.fixture(scope="module")
def client():
    app = FastAPI()
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(transactions.router, prefix="/api/v1")
    app.include_router(budgets.router, prefix="/api/v1")
    app.include_router(bills.router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup():
        await init_db()

    test_client = TestClient(app)

    # Create test user and override dependency
    auth_service = AuthService()
    test_user = auth_service.create_user(pin="1234", device_id="test")
    app.dependency_overrides[get_current_user] = lambda: test_user

    yield test_client


def test_health_endpoint(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_transaction_crud(client):
    data = {"amount": -50.0, "description": "Groceries", "category": "Food"}
    resp = client.post("/api/v1/transactions", json=data)
    assert resp.status_code == 201
    txn_id = resp.json()["id"]

    resp = client.get("/api/v1/transactions")
    assert resp.status_code == 200
    assert any(t["id"] == txn_id for t in resp.json())


def test_budget_creation(client):
    data = {"category": "Food", "limit": 300}
    resp = client.post("/api/v1/budgets", json=data)
    assert resp.status_code == 201
    resp = client.get("/api/v1/budgets")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_bill_creation(client):
    data = {"name": "Rent", "amount": 1000, "due_date": "2024-01-01", "is_recurring": True}
    resp = client.post("/api/v1/bills", json=data)
    assert resp.status_code == 201
    resp = client.get("/api/v1/bills")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
