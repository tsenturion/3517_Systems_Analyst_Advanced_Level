from typing import Protocol

from .domain import Ticket


class TicketRepository(Protocol):
    def create(
        self,
        title: str,
        description: str,
        creator_id: str,
        category_id: str
    ) -> Ticket:
        ...

    def get(self, ticket_id: str) -> Ticket:
        ...


class TicketService:
    def __init__(self, repository: TicketRepository):
        self.repository = repository

    def create_ticket(
        self,
        title: str,
        description: str,
        creator_id: str,
        category_id: str
    ) -> Ticket:
        return self.repository.create(
            title=title,
            description=description,
            creator_id=creator_id,
            category_id=category_id
        )

    def get_ticket(self, ticket_id: str) -> Ticket:
        return self.repository.get(ticket_id)