from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.enums import UserRole
from app.crud.user import create_user, has_any_users

def ensure_bootstrap_admin(db: Session, email: str, password: str) -> None:
    email = email.strip().lower()

    # If any user already exists, do nothing
    if has_any_users(db):
        return

    pw_hash = hash_password(password)
    create_user(db, email=email, password_hash=pw_hash, role=UserRole.admin)
