from fastapi import APIRouter, status

from app.core.types import CurrentUser, DbSession
from app.schemas.tag import TagCreate, TagOut
from app.services import tags as tag_service

router = APIRouter()


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    return tag_service.create_tag(db, name=payload.name, actor=current_user)
