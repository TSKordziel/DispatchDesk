from sqlalchemy.orm import Session

from sqlalchemy import select, func

from app.models.user import User
from app.models.enums import UserRole

def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.execute(statement).scalar_one_or_none()

def get_user_by_id(db: Session, user_id) -> User | None:
    statement = select(User).where(User.id == user_id)
    return db.execute(statement).scalar_one_or_none()

def create_user(db: Session, *, email: str, password_hash: str, role: UserRole = UserRole.requester) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def has_any_users(db: Session) -> bool:
    statement = select(func.count()).select_from(User)
    return db.execute(statement).scalar_one() > 0