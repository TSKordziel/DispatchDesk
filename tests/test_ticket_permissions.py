from sqlalchemy import select

from app.models.enums import UserRole, TicketStatus
from app.models.user import User


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


def _set_role(db, email: str, role: UserRole) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    user.role = role
    db.commit()
    return user


def _assert_error_envelope(response, expected_code: str):
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["code"] == expected_code
    assert payload["error"]["request_id"]
    assert response.headers.get("X-Request-ID") == payload["error"]["request_id"]


def test_requester_cannot_read_other_requester_ticket(client):
    _register_user(client, "owner@test.com", "password123456")
    owner_token = _login_user(client, "owner@test.com", "password123456")
    ticket_id = _create_ticket(client, owner_token)

    _register_user(client, "other@test.com", "password123456")
    other_token = _login_user(client, "other@test.com", "password123456")

    response = client.get(
        f"/tickets/{ticket_id}",
        headers=_auth_header(other_token),
    )

    assert response.status_code == 403
    _assert_error_envelope(response, "forbidden")


def test_agent_can_read_any_ticket(client, db):
    _register_user(client, "requester@test.com", "password123456")
    requester_token = _login_user(client, "requester@test.com", "password123456")
    ticket_id = _create_ticket(client, requester_token)

    _register_user(client, "agent@test.com", "password123456")
    _set_role(db, "agent@test.com", UserRole.agent)
    agent_token = _login_user(client, "agent@test.com", "password123456")

    response = client.get(
        f"/tickets/{ticket_id}",
        headers=_auth_header(agent_token),
    )
    assert response.status_code == 200


def test_requester_cannot_assign_or_transition(client, db):
    assignee_email = "assignee@test.com"
    try:
        _register_user(client, "requester2@test.com", "password123456")
        requester_token = _login_user(client, "requester2@test.com", "password123456")
        ticket_id = _create_ticket(client, requester_token)

        assignee = _register_user(client, assignee_email, "password123456")
        assignee_id = assignee.json()["id"]

        assign_response = client.post(
            f"/tickets/{ticket_id}/assign",
            json={"assignee_id": assignee_id},
            headers=_auth_header(requester_token),
        )
        assert assign_response.status_code == 403
        _assert_error_envelope(assign_response, "forbidden")

        transition_response = client.post(
            f"/tickets/{ticket_id}/transition",
            json={"to_status": TicketStatus.in_progress.value},
            headers=_auth_header(requester_token),
        )
        assert transition_response.status_code == 403
        _assert_error_envelope(transition_response, "forbidden")
    finally:
        user = db.execute(select(User).where(User.email == assignee_email)).scalar_one_or_none()
        if user:
            db.delete(user)
            db.commit()


def test_agent_cannot_transition_ticket_assigned_to_other_agent(client, db):
    _register_user(client, "requester3@test.com", "password123456")
    requester_token = _login_user(client, "requester3@test.com", "password123456")
    ticket_id = _create_ticket(client, requester_token)

    _register_user(client, "agent1@test.com", "password123456")
    agent1 = _set_role(db, "agent1@test.com", UserRole.agent)
    agent1_token = _login_user(client, "agent1@test.com", "password123456")

    _register_user(client, "agent2@test.com", "password123456")
    _set_role(db, "agent2@test.com", UserRole.agent)
    agent2_token = _login_user(client, "agent2@test.com", "password123456")

    assign_response = client.post(
        f"/tickets/{ticket_id}/assign",
        json={"assignee_id": str(agent1.id)},
        headers=_auth_header(agent1_token),
    )
    assert assign_response.status_code == 200

    transition_response = client.post(
        f"/tickets/{ticket_id}/transition",
        json={"to_status": TicketStatus.in_progress.value},
        headers=_auth_header(agent2_token),
    )
    assert transition_response.status_code == 422
    _assert_error_envelope(transition_response, "unprocessable")
