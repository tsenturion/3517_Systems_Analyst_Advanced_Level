import json
import pika


QUEUE = "helpdesk.notifications"


def connect():
    credentials = pika.PlainCredentials(
        "helpdesk",
        "helpdesk_dev_only"
    )

    return pika.BlockingConnection(
        pika.ConnectionParameters(
            "localhost",
            credentials=credentials
        )
    )


def declare_queue(channel):
    channel.queue_declare(
        queue=QUEUE,
        durable=True,
        arguments={"x-queue-type": "quorum"}
    )


def publish_ticket_created(ticket):
    connection = connect()

    try:
        channel = connection.channel()
        declare_queue(channel)
        channel.confirm_delivery()

        message = {
            "type": "ticket.created",
            "ticket_id": ticket.id,
            "title": ticket.title
        }

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE,
            body=json.dumps(
                message,
                ensure_ascii=False
            ).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent
            ),
            mandatory=True
        )
    finally:
        connection.close()