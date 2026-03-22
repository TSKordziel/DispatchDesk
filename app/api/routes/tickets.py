import uuid

from fastapi import APIRouter, status, Query

from app.core.types import AgentUser, CurrentUser, DbSession

from app.schemas.ticket import (
    TicketCreate,
    TicketOut,
    TicketAssignRequest,
    TicketTransitionRequest,
    TicketPriorityRequest,
)
from app.models.enums import TicketPriority, TicketStatus
from app.schemas.tag import TagOut

from app.services import tickets as ticket_service
from app.services import tags as tag_service

router = APIRouter()


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    return ticket_service.create_ticket(db, payload, current_user)

@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    return ticket_service.get_ticket(db, ticket_id, current_user)

@router.get("", response_model=list[TicketOut])
def list_tickets(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: TicketStatus | None = Query(None),
    priority: TicketPriority | None = Query(None),
    assigned_to: uuid.UUID | None = Query(None),
    tag: str | None = Query(None, min_length=1, max_length=100),
    q: str | None = Query(None, min_length=1, max_length=200),
):
    return ticket_service.list_tickets(
        db,
        limit=limit,
        offset=offset,
        actor=current_user,
        status=status,
        priority=priority,
        assigned_to_id=assigned_to,
        tag=tag,
        q=q,
    )

@router.post("/{ticket_id}/assign", response_model=TicketOut)
def assign_ticket(
    ticket_id: uuid.UUID,
    payload: TicketAssignRequest,
    db: DbSession,
    actor: AgentUser,
):
    return ticket_service.assign_ticket(db, ticket_id, assignee_id=payload.assignee_id, actor=actor)


@router.post("/{ticket_id}/transition", response_model=TicketOut)
def transition_ticket(
    ticket_id: uuid.UUID,
    payload: TicketTransitionRequest,
    db: DbSession,
    actor: AgentUser,
):
    return ticket_service.transition_ticket(db, ticket_id, payload.to_status, actor)


@router.patch("/{ticket_id}/priority", response_model=TicketOut)
def update_ticket_priority(
    ticket_id: uuid.UUID,
    payload: TicketPriorityRequest,
    db: DbSession,
    actor: AgentUser,
):
    return ticket_service.update_priority(db, ticket_id, payload.priority, actor)


@router.post("/{ticket_id}/tags/{tag_id}", response_model=TagOut)
def attach_tag(
    ticket_id: uuid.UUID,
    tag_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    return tag_service.attach_tag_to_ticket(
        db,
        ticket_id=ticket_id,
        tag_id=tag_id,
        actor=current_user,
    )


@router.delete("/{ticket_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def detach_tag(
    ticket_id: uuid.UUID,
    tag_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    tag_service.detach_tag_from_ticket(
        db,
        ticket_id=ticket_id,
        tag_id=tag_id,
        actor=current_user,
    )
