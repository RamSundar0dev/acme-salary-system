from fastapi.testclient import TestClient
from app.main import app


def test_login_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "hr.manager@acme.corp", "password": "AcmeHR2026!SecurePass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # Verify auth cookie is also set
    assert "auth_token" in response.cookies


def test_login_invalid_password(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "hr.manager@acme.corp", "password": "WrongPassword123!"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user_profile(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "hr.manager@acme.corp"
    assert data["role"] == "hr_manager"
    assert data["is_active"] is True


def test_unauthorized_access_rejected():
    # Fresh client without cookies or auth headers must be rejected with 401
    with TestClient(app) as unauth_client:
        response = unauth_client.get("/api/v1/employees")
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]
