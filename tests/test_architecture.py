import unittest

from helpdesk.application import TicketService
from helpdesk.domain import Ticket


class MemoryRepository:
    def __init__(self):
        self.tickets = {}

    def create(
        self,
        title,
        description,
        creator_id,
        category_id
    ):
        ticket = Ticket(
            id="ticket-001",
            title=title,
            description=description,
            creator_id=creator_id,
            category_id=category_id
        )

        self.tickets[ticket.id] = ticket

        return ticket

    def get(self, ticket_id):
        return self.tickets[ticket_id]


class RecordingPublisher:
    def __init__(self):
        self.events = []

    def publish_created(self, ticket):
        self.events.append(ticket.id)


class ArchitectureTest(unittest.TestCase):
    def test_create_ticket(self):
        repository = MemoryRepository()
        publisher = RecordingPublisher()

        service = TicketService(
            repository,
            publisher
        )

        ticket = service.create_ticket(
            title="Не работает принтер",
            description="Ошибка печати",
            creator_id="user-anna",
            category_id="hardware"
        )

        self.assertEqual(
            ticket.title,
            "Не работает принтер"
        )

        self.assertEqual(
            repository.get(ticket.id),
            ticket
        )

        self.assertEqual(
            publisher.events,
            [ticket.id]
        )


if __name__ == "__main__":
    unittest.main()