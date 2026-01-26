import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.policy import can_view_ticket, can_comment_on_ticket
from app.crud import ticket as ticket_crud
from app.crud import comment as comment_crud
from app.models.user import User
from app.schemas.comment import CommentCreate


def create_comment(db: Session, ticket_id: uuid.UUID, payload: CommentCreate, actor: User):
    ticket = ticket_crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not can_comment_on_ticket(actor, ticket):
        raise HTTPException(status_code=403, detail="Forbidden")

    body = payload.body.strip()
    return comment_crud.create_comment(db, ticket_id=ticket_id, author_id=actor.id, body=body)


def list_comments(db: Session, ticket_id: uuid.UUID, actor: User):
    ticket = ticket_crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not can_view_ticket(actor, ticket):
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")

    return comment_crud.list_comments_for_ticket(db, ticket_id=ticket_id)
