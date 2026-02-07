from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.tag import Tag


def get_tag(db: Session, tag_id) -> Tag | None:
    return db.get(Tag, tag_id)


def get_tag_by_name(db: Session, name: str) -> Tag | None:
    statement = select(Tag).where(Tag.name == name)
    return db.execute(statement).scalar_one_or_none()


def create_tag(db: Session, *, name: str) -> Tag:
    tag = Tag(name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
