def _register_user(client, email: str, password: str):
    return client.post("/auth/register", json={"email": email, "password": password})


def _login_user(client, email: str, password: str):
    return client.post("/auth/login", data={"username": email, "password": password})


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assert_error_envelope(response, expected_code: str):
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["code"] == expected_code
    assert payload["error"]["request_id"]
    assert response.headers.get("X-Request-ID") == payload["error"]["request_id"]


def test_register_login_me_success(client, db):
    email = "auth@test.com"
    try:
        register = _register_user(client, email, "password123456")
        assert register.status_code == 201

        login = _login_user(client, email, "password123456")
        assert login.status_code == 200
        token = login.json()["access_token"]

        me = client.get("/auth/me", headers=_auth_header(token))
        assert me.status_code == 200
        assert me.json()["email"] == email
    finally:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if user:
            db.delete(user)
            db.commit()


def test_login_wrong_password_returns_error_envelope(client):
    _register_user(client, "auth2@test.com", "password123456")

    response = _login_user(client, "auth2@test.com", "wrongpassword")
    assert response.status_code == 401
    _assert_error_envelope(response, "unauthorized")


def test_me_without_token_returns_error_envelope(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    _assert_error_envelope(response, "unauthorized")


def test_register_duplicate_email_returns_error_envelope(client):
    _register_user(client, "dup@test.com", "password123456")
    response = _register_user(client, "dup@test.com", "password123456")
    assert response.status_code == 400
    _assert_error_envelope(response, "bad_request")
from sqlalchemy import select

from app.models.user import User
