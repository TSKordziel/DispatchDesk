import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True