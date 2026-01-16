import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.enums import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class TicketOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    status: TicketStatus
    priority: TicketPriority
    created_by_id: uuid.UUID
    assigned_to_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None

    class Config:
        from_attributes = True

class TicketAssignRequest(BaseModel):
    assignee_id: uuid.UUID

class TicketTransitionRequest(BaseModel):
    to_status: TicketStatus
