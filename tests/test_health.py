import pytest

def test_health(client_app):
    response = client_app.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
