import json
import sqlite3

from pathlib import Path
from datetime import datetime
from contextlib import closing
from pymongo import MongoClient


root = Path(__file__).resolve().parents[1]

source = root / "data" / "helpdesk.sqlite3"

if not source.exists():
    raise SystemExit("База HelpDesk не найдена")


# Получаем события из SQLite

with closing(sqlite3.connect(source)) as connection:

    rows = connection.execute("""
        SELECT event_id, payload, published_at
        FROM outbox
        ORDER BY rowid
    """).fetchall()

if not rows:
    raise SystemExit("В Outbox отсутствуют события")


# Подключаемся к MongoDB

MONGO_URL = (
    "mongodb://helpdesk:helpdesk_dev_only"
    "@127.0.0.1:57017/"
    "?authSource=admin"
)


def parse_date(value):

    if value is None:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


inserted = 0
updated = 0

with MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
) as client:

    database = client["helpdesk_events"]
    collection = database["outbox_events"]

    # Создание индексов

    collection.create_index([
        ("event_type", 1),
        ("occurred_at", -1)
    ])

    collection.create_index("data.ticket_id")


    # Перенос событий

    for event_id, payload, published_at in rows:

        event = json.loads(payload)

        document = {
            "_id": event_id,
            "event_type": event["event_type"],
            "version": event["version"],
            "occurred_at": parse_date(
                event["occurred_at"]
            ),
            "published_at": parse_date(
                published_at
            ),
            "data": event["data"],
            "source": "helpdesk-outbox"
        }

        result = collection.replace_one(
            {"_id": event_id},
            document,
            upsert=True
        )

        if result.upserted_id is not None:
            inserted += 1

        elif result.modified_count > 0:
            updated += 1


    print("Обработано событий:", len(rows))
    print("Добавлено документов:", inserted)
    print("Обновлено документов:", updated)

    print(
        "Всего документов:",
        collection.count_documents({})
    )