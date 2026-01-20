import uuid

from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.core.policy import can_view_ticket, can_assign, can_transition_ticket, apply_transition

from app.crud import ticket as ticket_crud

from app.models.user import User
from app.models.enums import UserRole
from app.models.enums import TicketStatus  # for type clarity

from app.schemas.ticket import TicketCreate


def create_ticket(db: Session, payload: TicketCreate, actor: User):
    return ticket_crud.create_ticket(
        db,
        title=payload.title,
        description=payload.description,
        created_by_id=actor.id,
    )

def get_ticket(db: Session, ticket_id: uuid.UUID, actor: User):
    ticket = ticket_crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not can_view_ticket(actor, ticket):
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")

    return ticket

def list_tickets(db: Session, *, limit: int, offset: int, actor: User):
    created_by_filter = actor.id if actor.role == UserRole.requester else None
    return ticket_crud.list_tickets(db, limit=limit, offset=offset, created_by_id=created_by_filter)

def assign_ticket(db: Session, ticket_id: uuid.UUID, assignee_id: uuid.UUID, actor: User):
    ticket = ticket_crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    assignee = db.get(User, assignee_id)
    if assignee is None:
        raise HTTPException(status_code=404, detail="Assignee not found")

    if not can_assign(actor, assignee):
        # If I want to differentiate invalid_assignee vs forbidden, make can_assign return a Decision
        raise HTTPException(status_code=403, detail="Forbidden")

    ticket.assigned_to_id = assignee.id
    db.commit()
    db.refresh(ticket)
    return ticket

def transition_ticket(db: Session, ticket_id: uuid.UUID, to_status: TicketStatus, actor: User):
    ticket = ticket_crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not can_transition_ticket(actor, ticket, to_status):
        raise HTTPException(status_code=422, detail="Invalid transition or not allowed")

    apply_transition(ticket, to_status)
    db.commit()
    db.refresh(ticket)
    return ticket
