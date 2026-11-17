from .domain import (
    User,
    TicketCategory,
    TicketComment,
    TicketStatusChange,
    TicketStatus,
    Ticket,
    now
)

from .adapters import JsonTicketRepository


HelpDesk = JsonTicketRepository