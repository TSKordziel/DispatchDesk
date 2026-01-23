import uuid

from fastapi import APIRouter, Depends, status, Query

from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.core.rbac import require_agent

from app.models.user import User

from app.schemas.ticket import TicketCreate, TicketOut, TicketAssignRequest, TicketTransitionRequest

from app.services import tickets as ticket_service

router = APIRouter()


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ticket_service.create_ticket(db, payload, current_user)

@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ticket_service.get_ticket(db, ticket_id, current_user)

@router.get("", response_model=list[TicketOut])
def list_tickets(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ticket_service.list_tickets(db, limit=limit, offset=offset, actor=current_user)

@router.post("/{ticket_id}/assign", response_model=TicketOut)
def assign_ticket(
    ticket_id: uuid.UUID,
    payload: TicketAssignRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(require_agent),
):
    return ticket_service.assign_ticket(db, ticket_id, assignee_id=payload.assignee_id, actor=actor)


@router.post("/{ticket_id}/transition", response_model=TicketOut)
def transition_ticket(
    ticket_id: uuid.UUID,
    payload: TicketTransitionRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(require_agent),
):
    return ticket_service.transition_ticket(db, ticket_id, payload.to_status, actor)
