import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.rbac import require_admin
from app.schemas.user import UserOut, UserRoleUpdateRequest
from app.services import users as user_service

router = APIRouter()


@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: uuid.UUID,
    payload: UserRoleUpdateRequest,
    db: Session = Depends(get_db),
    actor=Depends(require_admin),
):
    return user_service.update_user_role(db, user_id, payload.role, actor)
