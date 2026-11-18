import pika

from .messaging import publish_event
from .outbox_repository import SqliteTicketRepository


def main():
    repository = SqliteTicketRepository()
    events = repository.pending_events()

    print(f"Ожидают публикации: {len(events)}")

    for event in events:
        try:
            publish_event(event)

        except (pika.exceptions.AMQPError, OSError) as error:
            print(
                f"Ошибка публикации {event['event_id']}: "
                f"{type(error).__name__}"
            )
            return

        repository.mark_published(
            event["event_id"]
        )

        print(f"Опубликовано: {event['event_id']}")


if __name__ == "__main__":
    main()