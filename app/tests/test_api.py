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


def test_translate_zh_endpoint(client):
    """Test universal EN→ZH translation endpoint."""
    token = _login_admin(client)
    response = client.get(
        "/api/translate/zh?q=hello",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # Either translated or error (API may be unreachable in CI)
    assert "translated" in data or "error" in data


def test_translate_zh_empty(client):
    """Test universal translation with empty query."""
    token = _login_admin(client)
    response = client.get(
        "/api/translate/zh?q=",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


def test_translate_endpoint(client):
    """Test Azure glossary translate (existing)."""
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


def test_kb_search(client):
    """Test KB search endpoint with 'VM' keyword."""
    response = client.get("/api/kb/search?q=VM")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["total"] > 0
    assert len(data["results"]) > 0
    assert "title" in data["results"][0]


def test_kb_search_empty(client):
    """Test KB search with empty query returns empty results."""
    response = client.get("/api/kb/search?q=")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


def test_kb_services(client):
    """Test KB services endpoint returns domains and services."""
    response = client.get("/api/kb/services")
    assert response.status_code == 200
    data = response.json()
    assert "domains" in data
    assert "services" in data
    assert len(data["domains"]) > 0


def test_kb_stats(client):
    """Test KB stats endpoint."""
    response = client.get("/api/kb/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_entries"] > 0
