import uuid
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.core.permissions import get_ticket_or_404, require_can_view_ticket
from app.crud import tag as tag_crud
from app.crud import ticket_tag as ticket_tag_crud
from app.models.user import User


def _normalize_tag_name(name: str) -> str:
    return name.strip().lower()


def create_tag(db: Session, *, name: str, actor: User):
    normalized = _normalize_tag_name(name)
    existing = tag_crud.get_tag_by_name(db, normalized)
    if existing:
        #raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
        return existing
    return tag_crud.create_tag(db, name=normalized)


def attach_tag_to_ticket(db: Session, *, ticket_id: uuid.UUID, tag_id: uuid.UUID, actor: User):
    ticket = get_ticket_or_404(db, ticket_id)
    require_can_view_ticket(actor, ticket)

    tag = tag_crud.get_tag(db, tag_id)
    if tag is None:
        not_found("Tag")

    existing = ticket_tag_crud.get_ticket_tag(db, ticket_id=ticket_id, tag_id=tag_id)
    if existing:
        return tag

    ticket_tag_crud.create_ticket_tag(db, ticket_id=ticket_id, tag_id=tag_id)
    return tag


def detach_tag_from_ticket(db: Session, *, ticket_id: uuid.UUID, tag_id: uuid.UUID, actor: User) -> None:
    ticket = get_ticket_or_404(db, ticket_id)
    require_can_view_ticket(actor, ticket)

    tag = tag_crud.get_tag(db, tag_id)
    if tag is None:
        not_found("Tag")

    ticket_tag_crud.delete_ticket_tag(db, ticket_id=ticket_id, tag_id=tag_id)
