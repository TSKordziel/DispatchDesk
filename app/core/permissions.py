import uuid

from sqlalchemy.orm import Session

from app.core.errors import forbidden, not_found, unprocessable
from app.core.policy import (
    can_assign,
    can_comment_on_ticket,
    can_transition_ticket,
    can_view_ticket,
)
from app.crud import ticket as ticket_crud
from app.crud import user as user_crud
from app.models.enums import TicketStatus
from app.models.ticket import Ticket
from app.models.user import User


def get_ticket_or_404(db: Session, ticket_id: uuid.UUID) -> Ticket:
    ticket = ticket_crud.get_ticket(db, ticket_id)
    if ticket is None:
        not_found("Ticket")
    return ticket


def get_user_or_404(db: Session, user_id: uuid.UUID, *, resource: str = "User") -> User:
    user = user_crud.get_user_by_id(db, user_id)
    if user is None:
        not_found(resource)
    return user


def require_can_view_ticket(actor: User, ticket: Ticket) -> None:
    if not can_view_ticket(actor, ticket):
        forbidden("Not authorized to view this ticket")


def require_can_comment(actor: User, ticket: Ticket) -> None:
    if not can_comment_on_ticket(actor, ticket):
        forbidden("Forbidden")


def require_can_assign(actor: User, assignee: User) -> None:
    if not can_assign(actor, assignee):
        forbidden("Forbidden")


def require_can_transition(actor: User, ticket: Ticket, to_status: TicketStatus) -> None:
    if not can_transition_ticket(actor, ticket, to_status):
        unprocessable("Invalid transition or not allowed")
