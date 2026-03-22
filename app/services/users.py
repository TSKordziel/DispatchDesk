import uuid

from sqlalchemy.orm import Session

from app.core.errors import unprocessable
from app.core.permissions import get_user_or_404
from app.models.enums import UserRole
from app.models.user import User


def update_user_role(db: Session, user_id: uuid.UUID, role: UserRole, actor: User) -> User:
    user = get_user_or_404(db, user_id)

    if role == UserRole.admin:
        unprocessable("Cannot promote to admin via API")

    user.role = role
    db.commit()
    db.refresh(user)
    return user
