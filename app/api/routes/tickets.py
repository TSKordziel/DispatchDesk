import uuid

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, HTTPException, Query

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.core.policy import can_view_ticket, can_assign, can_transition_ticket, apply_transition
from app.core.rbac import require_agent

from app.models.ticket import Ticket
from app.models.enums import UserRole
from app.models.user import User

from app.schemas.ticket import TicketCreate, TicketOut, TicketAssignRequest, TicketTransitionRequest

router = APIRouter()


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        created_by_id=current_user.id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Enforce requester ownership
    if not can_view_ticket(current_user, ticket): # current_user.role == UserRole.requester and ticket.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")

    return ticket

@router.get("", response_model=list[TicketOut])
def list_tickets(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    stmt = (
        select(Ticket)
        .order_by(Ticket.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if current_user.role == UserRole.requester:
        stmt = stmt.where(Ticket.created_by_id == current_user.id)

    tickets = db.execute(stmt).scalars().all()
    return tickets

@router.post("/{ticket_id}/assign", response_model=TicketOut)
def assign_ticket(
    ticket_id: uuid.UUID,
    payload: TicketAssignRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(require_agent),
):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    assignee = db.get(User, payload.assignee_id)
    if assignee is None:
        raise HTTPException(status_code=404, detail="Assignee not found")

    # Recommended: only allow assigning to agent/admin
    if not can_assign(actor, assignee):
        raise HTTPException(status_code=403, detail="Forbidden")

    ticket.assigned_to_id = assignee.id
    ticket.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/transition", response_model=TicketOut)
def transition_ticket(
    ticket_id: uuid.UUID,
    payload: TicketTransitionRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(require_agent),
):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    to_status = payload.to_status

    # Optional but matches your spec intent:
    # only the assigned agent can transition (admin can override)
    if not can_transition_ticket(actor, ticket, to_status):
        raise HTTPException(status_code=422, detail="Invalid transition or not allowed")

    apply_transition(ticket, to_status)
    ticket.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(ticket)
    return ticket
