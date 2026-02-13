import uuid
from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)


class TagOut(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True
