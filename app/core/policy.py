from datetime import datetime, timezone

from app.models.enums import UserRole, TicketStatus
from app.models.user import User
from app.models.ticket import Ticket  # adjust path if needed

from app.core.workflow import can_transition


def can_view_ticket(user: User, ticket: Ticket) -> bool:
    if user.role in (UserRole.agent, UserRole.admin):
        return True
    return ticket.created_by_id == user.id

def can_assign(actor: User, assignee: User) -> bool:
    if actor.role not in (UserRole.agent, UserRole.admin):
        return False
    return assignee.role in (UserRole.agent, UserRole.admin)

def can_transition_ticket(actor: User, ticket: Ticket, to_status: TicketStatus) -> bool:
    if actor.role not in (UserRole.agent, UserRole.admin):
        return False
    if actor.role == UserRole.agent and ticket.assigned_to_id and ticket.assigned_to_id != actor.id:
        return False

    return can_transition(ticket.status, to_status)

def apply_transition(ticket: Ticket, to_status: TicketStatus) -> None:
    ticket.status = to_status
    if to_status == TicketStatus.done:
        ticket.closed_at = datetime.now(timezone.utc)

def can_comment_on_ticket(user: User, ticket: Ticket) -> bool:
    # Same rule as view: requester only their own; agent/admin any
    return can_view_ticket(user, ticket)
