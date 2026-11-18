import json
import sqlite3

from .messaging import publish_event
from .outbox_repository import SqliteTicketRepository


repository = SqliteTicketRepository()

with sqlite3.connect(repository.path) as db:
    row = db.execute("""
        SELECT payload
        FROM outbox
        ORDER BY rowid DESC
        LIMIT 1
    """).fetchone()

if row is None:
    raise RuntimeError("Нет сохранённых событий")

event = json.loads(row[0])

publish_event(event)
publish_event(event)

print("Дважды отправлено событие:", event["event_id"])