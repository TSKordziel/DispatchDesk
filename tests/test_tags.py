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

def _create_tag(client, token: str, name: str):
    return client.post(
        "/tags",
        json={"name": name},
        headers=_auth_header(token),
    )


# Tag uniqueness + normalization

def test_create_tag_normalizes_and_idempotent(client):
    _register_user(client, "user@test.com", "password123456")
    token = _login_user(client, "user@test.com", "password123456")

    res1 = _create_tag(client, token, "Urgent")
    assert res1.status_code == 201
    assert res1.json()["name"] == "urgent"

    res2 = _create_tag(client, token, " urgent ")
    assert res2.status_code == 201
    assert res2.json()["name"] == "urgent"

    assert res1.json()["id"] == res2.json()["id"]

# Attach tag idempotent

def test_attach_tag_idempotent(client):
    _register_user(client, "user@test.com", "password123456")
    token = _login_user(client, "user@test.com", "password123456")

    ticket_id = _create_ticket(client, token)
    tag_res = _create_tag(client, token, "ops")
    tag_id = tag_res.json()["id"]

    res1 = client.post(
        f"/tickets/{ticket_id}/tags/{tag_id}",
        headers=_auth_header(token),
    )
    assert res1.status_code == 200

    res2 = client.post(
        f"/tickets/{ticket_id}/tags/{tag_id}",
        headers=_auth_header(token),
    )
    assert res2.status_code == 200

# Detach tag idempotent

def test_detach_tag_idempotent(client):
    _register_user(client, "user@test.com", "password123456")
    token = _login_user(client, "user@test.com", "password123456")

    ticket_id = _create_ticket(client, token)
    tag_res = _create_tag(client, token, "ops")
    tag_id = tag_res.json()["id"]

    client.post(
        f"/tickets/{ticket_id}/tags/{tag_id}",
        headers=_auth_header(token),
    )

    res1 = client.delete(
        f"/tickets/{ticket_id}/tags/{tag_id}",
        headers=_auth_header(token),
    )
    assert res1.status_code == 204

    res2 = client.delete(
        f"/tickets/{ticket_id}/tags/{tag_id}",
        headers=_auth_header(token),
    )
    assert res2.status_code == 204