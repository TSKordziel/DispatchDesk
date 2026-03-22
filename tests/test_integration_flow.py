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


def _set_role(db, email: str, role: UserRole) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    user.role = role
    db.commit()
    return user


def test_full_integration_flow(client, db):
    _register_user(client, "requester@test.com", "password123456")
    requester_token = _login_user(client, "requester@test.com", "password123456")

    _register_user(client, "agent@test.com", "password123456")
    agent = _set_role(db, "agent@test.com", UserRole.agent)
    agent_token = _login_user(client, "agent@test.com", "password123456")

    ticket_response = client.post(
        "/tickets",
        json={"title": "Printer issue in lobby", "description": "Paper jam on floor 1"},
        headers=_auth_header(requester_token),
    )
    assert ticket_response.status_code == 201
    ticket_id = ticket_response.json()["id"]

    assign_response = client.post(
        f"/tickets/{ticket_id}/assign",
        json={"assignee_id": str(agent.id)},
        headers=_auth_header(agent_token),
    )
    assert assign_response.status_code == 200
    assert assign_response.json()["assigned_to_id"] == str(agent.id)

    transition_response = client.post(
        f"/tickets/{ticket_id}/transition",
        json={"to_status": TicketStatus.triaged.value},
        headers=_auth_header(agent_token),
    )
    assert transition_response.status_code == 200
    assert transition_response.json()["status"] == TicketStatus.triaged.value

    comment_response = client.post(
        f"/tickets/{ticket_id}/comments",
        json={"body": "Acknowledged, investigating."},
        headers=_auth_header(requester_token),
    )
    assert comment_response.status_code == 201
    assert comment_response.json()["body"] == "Acknowledged, investigating."

    tag_response = client.post(
        "/tags",
        json={"name": "Ops"},
        headers=_auth_header(requester_token),
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["id"]
    assert tag_response.json()["name"] == "ops"

    attach_response = client.post(
        f"/tickets/{ticket_id}/tags/{tag_id}",
        headers=_auth_header(requester_token),
    )
    assert attach_response.status_code == 200
    assert attach_response.json()["id"] == tag_id

    list_response = client.get(
        "/tickets",
        params={"q": "Printer"},
        headers=_auth_header(requester_token),
    )
    assert list_response.status_code == 200
    assert list_response.headers.get("X-Request-ID")
    assert any(item["id"] == ticket_id for item in list_response.json())
