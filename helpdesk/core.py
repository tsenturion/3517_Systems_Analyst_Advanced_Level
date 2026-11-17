import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from uuid import uuid4


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class TicketStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


@dataclass
class User:
    id: str
    full_name: str
    role: str


@dataclass
class TicketCategory:
    id: str
    name: str


@dataclass
class TicketComment:
    id: str
    author_id: str
    text: str
    created_at: str = field(default_factory=now)


@dataclass
class TicketStatusChange:
    id: str
    user_id: str
    previous_status: str
    new_status: str
    changed_at: str = field(default_factory=now)


@dataclass
class Ticket:
    id: str
    creator_id: str
    category_id: str
    title: str
    description: str

    status: TicketStatus = TicketStatus.NEW
    assignee_id: str | None = None
    created_at: str = field(default_factory=now)
    closed_at: str | None = None

    comments: list[TicketComment] = field(default_factory=list)
    changes: list[TicketStatusChange] = field(default_factory=list)

    def assign_to(self, user_id: str):
        self.assignee_id = user_id

    def add_comment(self, author_id: str, text: str):
        self.comments.append(
            TicketComment(str(uuid4()), author_id, text)
        )

    def change_status(self, new_status: TicketStatus, user_id: str):
        new_status = TicketStatus(new_status)
        previous = self.status
        self.status = new_status

        self.changes.append(
            TicketStatusChange(
                str(uuid4()),
                user_id,
                previous.value,
                new_status.value
            )
        )

        self.closed_at = (
            now() if new_status == TicketStatus.CLOSED else None
        )

    @classmethod
    def from_dict(cls, data: dict):
        data = dict(data)
        data["status"] = TicketStatus(data["status"])

        data["comments"] = [
            TicketComment(**item)
            for item in data.get("comments", [])
        ]

        data["changes"] = [
            TicketStatusChange(**item)
            for item in data.get("changes", [])
        ]

        return cls(**data)


class HelpDesk:
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
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")

        temporary.write_text(
            json.dumps(
                [asdict(t) for t in self.tickets.values()],
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
            str(uuid4()),
            creator_id,
            category_id,
            title,
            description
        )

        self.tickets[ticket.id] = ticket
        self.save()
        return ticket

    def get(self, ticket_id: str):
        return self.tickets[ticket_id]