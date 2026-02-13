import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base



class TicketTag(Base):
    __tablename__ = "ticket_tags"

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        primary_key=True
    )

    tag_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )

    # future metadata:

    # Relationships:
    ticket = relationship("Ticket", back_populates="ticket_tags")
    tag = relationship("Tag", back_populates="ticket_tags")