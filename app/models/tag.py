import uuid

from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        Text,
        unique=True,
        index=True,
        nullable=False
    )
    # Relationships
    ticket_tags = relationship("TicketTag", back_populates="tag", cascade="all, delete-orphan",)

