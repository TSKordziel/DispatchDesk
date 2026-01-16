from app.models.enums import TicketStatus

ALLOWED_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.new: {TicketStatus.triaged},
    TicketStatus.triaged: {TicketStatus.in_progress, TicketStatus.blocked},
    TicketStatus.in_progress: {TicketStatus.blocked, TicketStatus.done, TicketStatus.triaged},
    TicketStatus.blocked: {TicketStatus.in_progress, TicketStatus.triaged},
    TicketStatus.done: set(),
}

def can_transition(from_status: TicketStatus, to_status: TicketStatus) -> bool:
    return to_status in ALLOWED_TRANSITIONS.get(from_status, set())
