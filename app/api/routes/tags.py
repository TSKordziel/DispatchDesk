from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.tag import TagCreate, TagOut
from app.services import tags as tag_service

router = APIRouter()


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return tag_service.create_tag(db, name=payload.name, actor=current_user)
