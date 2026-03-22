import uuid

from sqlalchemy.orm import Session

from app.core.policy import apply_transition
from app.core.permissions import (
    get_ticket_or_404,
    get_user_or_404,
    require_can_assign,
    require_can_transition,
    require_can_view_ticket,
)

from app.crud import ticket as ticket_crud

from app.models.user import User
from app.models.enums import UserRole, TicketStatus, TicketPriority

from app.schemas.ticket import TicketCreate


def create_ticket(db: Session, payload: TicketCreate, actor: User):
    return ticket_crud.create_ticket(
        db,
        title=payload.title,
        description=payload.description,
        created_by_id=actor.id,
    )

def get_ticket(db: Session, ticket_id: uuid.UUID, actor: User):
    ticket = get_ticket_or_404(db, ticket_id)
    require_can_view_ticket(actor, ticket)
    return ticket

def list_tickets(
    db: Session,
    *,
    limit: int,
    offset: int,
    actor: User,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    assigned_to_id: uuid.UUID | None = None,
    tag: str | None = None,
    q: str | None = None,
):
    created_by_filter = actor.id if actor.role == UserRole.requester else None
    normalized_tag = tag.strip().lower() if tag is not None else None
    normalized_q = q.strip() if q is not None else None
    return ticket_crud.list_tickets(
        db,
        limit=limit,
        offset=offset,
        created_by_id=created_by_filter,
        status=status,
        priority=priority,
        assigned_to_id=assigned_to_id,
        tag=normalized_tag,
        q=normalized_q,
    )

def assign_ticket(db: Session, ticket_id: uuid.UUID, assignee_id: uuid.UUID, actor: User):
    ticket = get_ticket_or_404(db, ticket_id)
    assignee = get_user_or_404(db, assignee_id, resource="Assignee")
    require_can_assign(actor, assignee)

    ticket.assigned_to_id = assignee.id
    db.commit()
    db.refresh(ticket)
    return ticket

def transition_ticket(db: Session, ticket_id: uuid.UUID, to_status: TicketStatus, actor: User):
    ticket = get_ticket_or_404(db, ticket_id)
    require_can_transition(actor, ticket, to_status)

    apply_transition(ticket, to_status)
    db.commit()
    db.refresh(ticket)
    return ticket

def update_priority(db: Session, ticket_id: uuid.UUID, priority: TicketPriority, actor: User):
    ticket = get_ticket_or_404(db, ticket_id)
    ticket.priority = priority
    db.commit()
    db.refresh(ticket)
    return ticket
