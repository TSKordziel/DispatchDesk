from enum import Enum

# Ticket Enums:
class TicketStatus(str, Enum):
    new = "new"
    triaged = "triaged"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class TicketPriority(str, Enum):
    low = "low"
    med = "med"
    high = "high"
    urgent = "urgent"

# User Enums:
class UserRole(str, Enum):
    requester = "requester"
    agent = "agent"
    admin = "admin"