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
            id="test-ticket-001",
            title=title,
            description=description,
            creator_id=creator_id,
            category_id=category_id
        )

        self.tickets[ticket.id] = ticket

        return ticket

    def get(self, ticket_id):
        return self.tickets[ticket_id]


class TestTicketService(unittest.TestCase):

    def setUp(self):
        self.repository = MemoryRepository()
        self.service = TicketService(self.repository)

    def test_create_ticket(self):

        ticket = self.service.create_ticket(
            title="Test ticket",
            description="Test description",
            creator_id="user-anna",
            category_id="software"
        )

        self.assertEqual(ticket.title, "Test ticket")
        self.assertEqual(ticket.status.value, "NEW")

        self.assertIn(
            ticket.id,
            self.repository.tickets
        )

    def test_get_ticket(self):

        created = self.service.create_ticket(
            title="Test ticket",
            description="Test description",
            creator_id="user-anna",
            category_id="software"
        )

        received = self.service.get_ticket(created.id)

        self.assertEqual(received.id, created.id)
        self.assertEqual(received.title, created.title)

    def test_unknown_ticket(self):

        with self.assertRaises(KeyError):
            self.service.get_ticket("unknown-id")


if __name__ == "__main__":
    unittest.main()