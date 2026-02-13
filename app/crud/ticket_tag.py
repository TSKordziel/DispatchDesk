import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.ticket_tag import TicketTag


def get_ticket_tag(db: Session, *, ticket_id: uuid.UUID, tag_id: uuid.UUID) -> TicketTag | None:
    statement = select(TicketTag).where(
        TicketTag.ticket_id == ticket_id,
        TicketTag.tag_id == tag_id,
    )
    return db.execute(statement).scalar_one_or_none()


def create_ticket_tag(db: Session, *, ticket_id: uuid.UUID, tag_id: uuid.UUID) -> TicketTag:
    ticket_tag = TicketTag(ticket_id=ticket_id, tag_id=tag_id)
    db.add(ticket_tag)
    db.commit()
    db.refresh(ticket_tag)
    return ticket_tag


def delete_ticket_tag(db: Session, *, ticket_id: uuid.UUID, tag_id: uuid.UUID) -> bool:
    ticket_tag = get_ticket_tag(db, ticket_id=ticket_id, tag_id=tag_id)
    if ticket_tag is None:
        return False
    db.delete(ticket_tag)
    db.commit()
    return True
