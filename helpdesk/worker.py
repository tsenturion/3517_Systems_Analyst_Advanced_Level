import json

from .messaging import QUEUE, connect, declare_queue


def handle(channel, method, properties, body):
    event = json.loads(body.decode("utf-8"))

    print(
        f"Уведомление: создана заявка "
        f"{event['ticket_id']} — {event['title']}",
        flush=True
    )

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
            on_message_callback=handle
        )

        print(
            "Ожидание событий... Ctrl+C для остановки",
            flush=True
        )

        channel.start_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()