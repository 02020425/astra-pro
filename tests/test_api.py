import pytest
from fastapi.testclient import TestClient
from astra_pro.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_list_agents_endpoint(client):
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data