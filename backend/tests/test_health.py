from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_route_exists():
    response = client.get("/health")
    assert response.status_code in (200, 500)