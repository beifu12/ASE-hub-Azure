from fastapi.testclient import TestClient


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"


def _login_admin(client: TestClient) -> str:
    """Helper to log in and return the JWT token from the JSON body."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "Demo0523"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    return data["access_token"]


def test_login_success(client):
    token = _login_admin(client)
    assert token


def test_login_failure(client):
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_unauthorized_access(client):
    response = client.get("/api/reports")
    assert response.status_code == 401


def test_translate_endpoint(client):
    token = _login_admin(client)
    response = client.get(
        "/api/translate?q=availability",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "query" in data


def test_status_endpoint(client):
    token = _login_admin(client)
    response = client.get(
        "/api/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_updates_endpoint(client):
    token = _login_admin(client)
    response = client.get(
        "/api/updates",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
