import json
import sqlite3

from pathlib import Path

from .messaging import QUEUE, connect, declare_queue


DB_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "notifications.sqlite3"
)


def save_notification(event):
    data = event.get("data", event)

    event_id = event.get("event_id")

    if event_id is None:
        event_id = f"legacy:{data['ticket_id']}"

    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                event_id TEXT PRIMARY KEY,
                ticket_id TEXT NOT NULL,
                title TEXT NOT NULL,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        result = db.execute(
            """
            INSERT OR IGNORE INTO notifications
            (event_id, ticket_id, title)
            VALUES (?, ?, ?)
            """,
            (
                event_id,
                data["ticket_id"],
                data["title"]
            )
        )

        inserted = result.rowcount == 1

    return event_id, inserted


def handle(channel, method, properties, body):
    event = json.loads(body.decode("utf-8"))

    event_id, inserted = save_notification(event)

    if inserted:
        print(f"Обработано событие: {event_id}", flush=True)
    else:
        print(f"Повторное событие: {event_id}", flush=True)

    channel.basic_ack(
        delivery_tag=method.delivery_tag
    )


def main():
    connection = connect()

    try:
        channel = connection.channel()
        declare_queue(channel)

        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(
            queue=QUEUE,
            on_message_callback=handle,
            auto_ack=False
        )

        print("Ожидание сообщений...", flush=True)
        channel.start_consuming()

    except KeyboardInterrupt:
        print("Обработчик остановлен")

    finally:
        connection.close()


if __name__ == "__main__":
    main()