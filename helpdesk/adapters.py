import json
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from .domain import Ticket
from .messaging import publish_ticket_created


class JsonTicketRepository:
    def __init__(self):
        self.path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "tickets.json"
        )

        rows = (
            json.loads(self.path.read_text(encoding="utf-8"))
            if self.path.exists()
            else []
        )

        self.tickets = {
            row["id"]: Ticket.from_dict(row)
            for row in rows
        }

    def save(self):
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temporary = self.path.with_suffix(".tmp")

        temporary.write_text(
            json.dumps(
                [
                    asdict(ticket)
                    for ticket in self.tickets.values()
                ],
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        temporary.replace(self.path)

    def create(
        self,
        title: str,
        description: str,
        creator_id: str,
        category_id: str
    ):
        ticket = Ticket(
            id=str(uuid4()),
            creator_id=creator_id,
            category_id=category_id,
            title=title,
            description=description
        )

        self.tickets[ticket.id] = ticket
        self.save()

        return ticket

    def get(self, ticket_id: str):
        return self.tickets[ticket_id]


class RabbitEventPublisher:
    def publish_created(self, ticket: Ticket):
        publish_ticket_created(ticket)