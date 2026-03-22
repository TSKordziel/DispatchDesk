import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(
        from_attributes = True,
    )
    id: uuid.UUID
    email: EmailStr
    role: UserRole
    is_active: bool

    # class Config:
    #     from_attributes = True


class UserRoleUpdateRequest(BaseModel):
    role: UserRole
