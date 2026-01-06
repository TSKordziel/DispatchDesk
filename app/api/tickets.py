import uuid
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.ticket import Ticket
from app.models.enums import UserRole

from app.schemas.ticket import TicketCreate, TicketOut

router = APIRouter(prefix="/tickets", tags=["tickets"])


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
    if current_user.role == UserRole.requester and ticket.created_by_id != current_user.id:
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