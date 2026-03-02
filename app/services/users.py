import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.user import User
from app.crud import user as user_crud


def update_user_role(db: Session, user_id: uuid.UUID, role: UserRole, actor: User) -> User:
    user = user_crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if role == UserRole.admin:
        raise HTTPException(status_code=422, detail="Cannot promote to admin via API")

    user.role = role
    db.commit()
    db.refresh(user)
    return user
