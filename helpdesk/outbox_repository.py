import json
import sqlite3

from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from .domain import Ticket, now


class SqliteTicketRepository:
    def __init__(self):
        self.path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "helpdesk.sqlite3"
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
            """)

            # Outbox хранится рядом с заявками, чтобы обе записи можно было
            # атомарно фиксировать в одной SQLite-транзакции.
            db.execute("""
                CREATE TABLE IF NOT EXISTS outbox (
                    event_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    published_at TEXT
                )
            """)

            # Перенос заявок из предыдущей версии проекта
            legacy = self.path.parent / "tickets.json"

            if legacy.exists():
                rows = json.loads(
                    legacy.read_text(encoding="utf-8")
                )

                for row in rows:
                    db.execute(
                        """
                        INSERT OR IGNORE INTO tickets
                        (id, payload) VALUES (?, ?)
                        """,
                        (
                            row["id"],
                            json.dumps(row, ensure_ascii=False)
                        )
                    )

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5)

        try:
            yield db
            # Успешный выход фиксирует все операции; исключение ниже откатывает их.
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def create(
        self,
        title: str,
        description: str,
        creator_id: str,
        category_id: str
    ) -> Ticket:
        ticket = Ticket(
            id=str(uuid4()),
            title=title,
            description=description,
            creator_id=creator_id,
            category_id=category_id
        )

        event = {
            "event_id": str(uuid4()),
            "event_type": "ticket.created",
            "version": 1,
            "occurred_at": ticket.created_at,
            "data": {
                "ticket_id": ticket.id,
                "title": ticket.title
            }
        }

        with self._connect() as db:
            # Заявка и событие создаются одной транзакцией: либо сохраняются
            # обе записи, либо ни одна из них.
            db.execute(
                "INSERT INTO tickets VALUES (?, ?)",
                (
                    ticket.id,
                    json.dumps(
                        asdict(ticket),
                        ensure_ascii=False
                    )
                )
            )

            db.execute(
                """
                INSERT INTO outbox
                (event_id, payload)
                VALUES (?, ?)
                """,
                (
                    event["event_id"],
                    json.dumps(event, ensure_ascii=False)
                )
            )

        return ticket

    def get(self, ticket_id: str) -> Ticket:
        with self._connect() as db:
            row = db.execute(
                "SELECT payload FROM tickets WHERE id = ?",
                (ticket_id,)
            ).fetchone()

        if row is None:
            raise KeyError(ticket_id)

        return Ticket.from_dict(json.loads(row[0]))

    def pending_events(self):
        # Отправитель событий может повторить выборку после сбоя процесса:
        # неопубликованные записи остаются в outbox до подтверждения публикации.
        with self._connect() as db:
            rows = db.execute("""
                SELECT payload
                FROM outbox
                WHERE published_at IS NULL
                ORDER BY rowid
            """).fetchall()

        return [json.loads(row[0]) for row in rows]

    def mark_published(self, event_id: str):
        # Вызывать после подтверждения брокера. Если процесс завершится после
        # публикации, но до этой отметки, событие может быть отправлено повторно.
        with self._connect() as db:
            db.execute(
                """
                UPDATE outbox
                SET published_at = ?
                WHERE event_id = ?
                  AND published_at IS NULL
                """,
                (now(), event_id)
            )
            
    def update_status(
        self,
        ticket_id: str,
        new_status: str,
        user_id: str
    ) -> Ticket:
        with self._connect() as db:
            row = db.execute(
                "SELECT payload FROM tickets WHERE id = ?",
                (ticket_id,)
            ).fetchone()

            if row is None:
                raise KeyError(ticket_id)

            ticket = Ticket.from_dict(json.loads(row[0]))

            if ticket.status.value != new_status:
                ticket.change_status(new_status, user_id)

                db.execute(
                    """
                    UPDATE tickets
                    SET payload = ?
                    WHERE id = ?
                    """,
                    (
                        json.dumps(
                            asdict(ticket),
                            ensure_ascii=False
                        ),
                        ticket_id
                    )
                )

        return ticket