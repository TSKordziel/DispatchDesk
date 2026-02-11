def _register_user(client, email: str, password: str):
    return client.post("/auth/register", json={"email": email, "password": password})


def _login_user(client, email: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_ticket(client, token: str, title: str = "Test ticket"):
    response = client.post(
        "/tickets",
        json={"title": title, "description": None},
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_comment_as_owner(client):
    _register_user(client, "owner@test.com", "password123456")
    token = _login_user(client, "owner@test.com", "password123456")
    ticket_id = _create_ticket(client, token)

    response = client.post(
        f"/tickets/{ticket_id}/comments",
        json={"body": "hello"},
        headers=_auth_header(token),
    )

    assert response.status_code == 201
    assert response.json()["body"] == "hello"
    assert response.json()["ticket_id"] == ticket_id


def test_create_comment_forbidden_for_other_requester(client):
    _register_user(client, "owner@test.com", "password123456")
    owner_token = _login_user(client, "owner@test.com", "password123456")
    ticket_id = _create_ticket(client, owner_token)

    _register_user(client, "other@test.com", "password123456")
    other_token = _login_user(client, "other@test.com", "password123456")

    response = client.post(
        f"/tickets/{ticket_id}/comments",
        json={"body": "nope"},
        headers=_auth_header(other_token),
    )

    assert response.status_code == 403


def test_list_comments_returns_in_order(client):
    _register_user(client, "owner@test.com", "password123456")
    token = _login_user(client, "owner@test.com", "password123456")
    ticket_id = _create_ticket(client, token)

    first = client.post(
        f"/tickets/{ticket_id}/comments",
        json={"body": "first"},
        headers=_auth_header(token),
    )
    assert first.status_code == 201

    second = client.post(
        f"/tickets/{ticket_id}/comments",
        json={"body": "second"},
        headers=_auth_header(token),
    )
    assert second.status_code == 201

    response = client.get(
        f"/tickets/{ticket_id}/comments",
        headers=_auth_header(token),
    )

    assert response.status_code == 200
    payload = response.json()
    assert [item["body"] for item in payload] == ["first", "second"]
