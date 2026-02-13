import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.models.user import User

from app.schemas.comment import CommentCreate, CommentRead
from app.services import comments as comment_service

router = APIRouter()


@router.post(
    "/{ticket_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    ticket_id: uuid.UUID,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return comment_service.create_comment(db, ticket_id, payload, current_user)


@router.get(
    "/{ticket_id}/comments",
    response_model=list[CommentRead],
)
def list_comments(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return comment_service.list_comments(db, ticket_id, current_user)
