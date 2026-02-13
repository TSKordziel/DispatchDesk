import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=10_000)


class CommentRead(BaseModel):
    id: uuid.UUID
    ticket_id: uuid.UUID
    author_id: uuid.UUID 
    body: str
    created_at: datetime

    class Config:
        from_attributes = True