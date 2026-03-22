import uuid
from sqlalchemy.orm import Session

from app.core.permissions import (
    get_ticket_or_404,
    require_can_comment,
    require_can_view_ticket,
)
from app.crud import comment as comment_crud
from app.models.user import User
from app.schemas.comment import CommentCreate


def create_comment(db: Session, ticket_id: uuid.UUID, payload: CommentCreate, actor: User):
    ticket = get_ticket_or_404(db, ticket_id)
    require_can_comment(actor, ticket)

    body = payload.body.strip()
    return comment_crud.create_comment(db, ticket_id=ticket_id, author_id=actor.id, body=body)


def list_comments(db: Session, ticket_id: uuid.UUID, actor: User):
    ticket = get_ticket_or_404(db, ticket_id)
    require_can_view_ticket(actor, ticket)

    return comment_crud.list_comments_for_ticket(db, ticket_id=ticket_id)
