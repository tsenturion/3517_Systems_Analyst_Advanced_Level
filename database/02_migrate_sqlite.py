import json
import sqlite3
import psycopg

from pathlib import Path
from contextlib import closing


root = Path(__file__).resolve().parents[1]

source = root / "data" / "helpdesk.sqlite3"

if not source.exists():
    raise SystemExit("Исходная база SQLite не найдена")


# Получение существующих заявок

with closing(sqlite3.connect(source)) as sqlite:
    rows = sqlite.execute(
        "SELECT payload FROM tickets"
    ).fetchall()

tickets = []

for row in rows:
    tickets.append(json.loads(row[0]))

if not tickets:
    raise SystemExit("В SQLite отсутствуют заявки")


# Известные пользователи и категории

users = {
    "user-anna": ("Анна", "employee"),
    "user-oleg": ("Олег", "support")
}

categories = {
    "hardware": "Оборудование",
    "software": "Программное обеспечение",
    "network": "Сеть"
}


# Подключение к PostgreSQL

connection = psycopg.connect(
    host="127.0.0.1",
    port=55432,
    dbname="helpdesk",
    user="helpdesk",
    password="helpdesk_dev_only"
)

comments_count = 0
changes_count = 0


def ensure_user(cursor, user_id):
    if user_id is None:
        return

    name, role = users.get(user_id, (None, None))

    cursor.execute("""
        INSERT INTO helpdesk.users
        (id, full_name, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, (user_id, name, role))


# Перенос данных в одной транзакции

with connection:
    with connection.cursor() as cursor:

        # Обновляем только учебную копию в PostgreSQL

        cursor.execute("""
            TRUNCATE
                helpdesk.ticket_status_changes,
                helpdesk.ticket_comments,
                helpdesk.tickets,
                helpdesk.categories,
                helpdesk.users
        """)

        for ticket in tickets:

            ensure_user(cursor, ticket["creator_id"])
            ensure_user(cursor, ticket.get("assignee_id"))

            category_id = ticket["category_id"]

            category_name = categories.get(
                category_id,
                f"Категория {category_id}"
            )

            cursor.execute("""
                INSERT INTO helpdesk.categories
                (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (category_id, category_name))

            cursor.execute("""
                INSERT INTO helpdesk.tickets (
                    id,
                    creator_id,
                    assignee_id,
                    category_id,
                    title,
                    description,
                    status,
                    created_at,
                    closed_at
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
            """, (
                ticket["id"],
                ticket["creator_id"],
                ticket.get("assignee_id"),
                category_id,
                ticket["title"],
                ticket["description"],
                ticket["status"],
                ticket["created_at"],
                ticket.get("closed_at")
            ))

            for position, comment in enumerate(
                ticket.get("comments", []),
                start=1
            ):
                ensure_user(cursor, comment["author_id"])

                cursor.execute("""
                    INSERT INTO helpdesk.ticket_comments (
                        id, ticket_id, author_id,
                        text, created_at, position
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    comment["id"],
                    ticket["id"],
                    comment["author_id"],
                    comment["text"],
                    comment["created_at"],
                    position
                ))

                comments_count += 1

            for position, change in enumerate(
                ticket.get("changes", []),
                start=1
            ):
                ensure_user(cursor, change["user_id"])

                cursor.execute("""
                    INSERT INTO helpdesk.ticket_status_changes (
                        id, ticket_id, user_id,
                        previous_status, new_status,
                        changed_at, position
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    change["id"],
                    ticket["id"],
                    change["user_id"],
                    change["previous_status"],
                    change["new_status"],
                    change["changed_at"],
                    position
                ))

                changes_count += 1


print("Перенос завершён")
print("Заявок:", len(tickets))
print("Комментариев:", comments_count)
print("Изменений статусов:", changes_count)