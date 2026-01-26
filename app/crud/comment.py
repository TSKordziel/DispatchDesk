import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.comment import Comment


def create_comment(
    db: Session,
    *,
    ticket_id: uuid.UUID,
    author_id: uuid.UUID,
    body: str,
) -> Comment:
    comment = Comment(ticket_id=ticket_id, author_id=author_id, body=body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments_for_ticket(db: Session, *, ticket_id: uuid.UUID) -> list[Comment]:
    statement = (
        select(Comment)
        .where(Comment.ticket_id == ticket_id)
        .order_by(Comment.created_at.asc(), Comment.id.asc())
    )
    return db.execute(statement).scalars().all()
