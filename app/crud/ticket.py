import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.ticket import Ticket

def create_ticket(db: Session, *, title: str, description: str | None, created_by_id: uuid.UUID) -> Ticket:
    ticket = Ticket(title=title, description=description, created_by_id=created_by_id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_ticket(db: Session, ticket_id: uuid.UUID) -> Ticket | None:
    return db.get(Ticket, ticket_id)

def list_tickets(db: Session, *, limit: int, offset: int, created_by_id: uuid.UUID | None = None) -> list[Ticket]:
    statement = select(Ticket).order_by(Ticket.created_at.desc()).limit(limit).offset(offset)
    if created_by_id is not None:
        statement = statement.where(Ticket.created_by_id == created_by_id)
    return db.execute(statement).scalars().all()
