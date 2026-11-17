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


class EventPublisher(Protocol):
    def publish_created(self, ticket: Ticket) -> None:
        ...


class TicketService:
    def __init__(
        self,
        repository: TicketRepository,
        publisher: EventPublisher
    ):
        self.repository = repository
        self.publisher = publisher

    def create_ticket(
        self,
        title: str,
        description: str,
        creator_id: str,
        category_id: str
    ) -> Ticket:
        ticket = self.repository.create(
            title=title,
            description=description,
            creator_id=creator_id,
            category_id=category_id
        )

        self.publisher.publish_created(ticket)

        return ticket

    def get_ticket(self, ticket_id: str) -> Ticket:
        return self.repository.get(ticket_id)