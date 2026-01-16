from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.enums import UserRole
from app.crud.user import get_user_by_email, create_user

def ensure_bootstrap_admin(db: Session, email: str, password: str) -> None:
    email = email.strip().lower()
    existing = get_user_by_email(db, email)
    if existing:
        # optionally: ensure role is admin
        if existing.role != UserRole.admin:
            existing.role = UserRole.admin
            db.commit()
        return

    pw_hash = hash_password(password)
    create_user(db, email=email, password_hash=pw_hash, role=UserRole.admin)  # requires CRUD tweak
