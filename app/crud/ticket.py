import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.tag import Tag
from app.models.ticket_tag import TicketTag

from app.models.ticket import Ticket
from app.models.enums import TicketPriority, TicketStatus

def create_ticket(db: Session, *, title: str, description: str | None, created_by_id: uuid.UUID) -> Ticket:
    ticket = Ticket(title=title, description=description, created_by_id=created_by_id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_ticket(db: Session, ticket_id: uuid.UUID) -> Ticket | None:
    return db.get(Ticket, ticket_id)

def list_tickets(
    db: Session,
    *,
    limit: int,
    offset: int,
    created_by_id: uuid.UUID | None = None,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    assigned_to_id: uuid.UUID | None = None,
    tag: str | None = None,
) -> list[Ticket]:
    statement = select(Ticket).order_by(Ticket.created_at.desc()).limit(limit).offset(offset)
    if created_by_id is not None:
        statement = statement.where(Ticket.created_by_id == created_by_id)
    if status is not None:
        statement = statement.where(Ticket.status == status)
    if priority is not None:
        statement = statement.where(Ticket.priority == priority)
    if assigned_to_id is not None:
        statement = statement.where(Ticket.assigned_to_id == assigned_to_id)
    if tag is not None:
        statement = (
            statement.join(TicketTag, TicketTag.ticket_id == Ticket.id)
            .join(Tag, Tag.id == TicketTag.tag_id)
            .where(Tag.name == tag)
            .distinct()
        )
    return db.execute(statement).scalars().all()
