from app.models.enums import UserRole
from app.models.user import User
from app.models.ticket import Ticket  # adjust path if needed


def can_view_ticket(user: User, ticket: Ticket) -> bool:
    if user.role in (UserRole.agent, UserRole.admin):
        return True
    return ticket.created_by_id == user.id
