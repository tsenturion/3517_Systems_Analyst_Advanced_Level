import csv
import time
import psycopg

from statistics import mean, median
from pathlib import Path


root = Path(__file__).resolve().parents[1]

connection = psycopg.connect(
    host="127.0.0.1",
    port=55432,
    dbname="helpdesk",
    user="helpdesk",
    password="helpdesk_dev_only",
    autocommit=True,
    prepare_threshold=None
)


# Исследуемый запрос

query = """
    SELECT
        id,
        title,
        status,
        created_at

    FROM helpdesk_perf.tickets

    WHERE status = 'NEW'

    ORDER BY created_at DESC, id DESC

    LIMIT 20
"""


# Запрос с OFFSET

offset_query = """
    SELECT id, title, status
    FROM helpdesk_perf.tickets
    ORDER BY id DESC
    LIMIT 20 OFFSET 80000
"""


# Запрос с курсорной пагинацией

cursor_query = """
    SELECT id, title, status
    FROM helpdesk_perf.tickets
    WHERE id < 20001
    ORDER BY id DESC
    LIMIT 20
"""


# Функция измерения производительности

def measure(cursor, name, sql):

    # Прогрев

    for _ in range(3):
        cursor.execute(sql)
        cursor.fetchall()

    durations = []

    # Основные измерения

    for _ in range(20):

        start = time.perf_counter()

        cursor.execute(sql)
        rows = cursor.fetchall()

        duration = (
            time.perf_counter() - start
        ) * 1000

        durations.append(duration)

    return {
        "scenario": name,
        "measurements": len(durations),
        "returned_rows": len(rows),
        "average_ms": round(mean(durations), 3),
        "median_ms": round(median(durations), 3),
        "minimum_ms": round(min(durations), 3),
        "maximum_ms": round(max(durations), 3)
    }


results = []


with connection:

    with connection.cursor() as cursor:

        # Эксперимент без составного индекса

        cursor.execute("""
            DROP INDEX IF EXISTS
                helpdesk_perf.idx_tickets_status_created
        """)

        cursor.execute("""
            ANALYZE helpdesk_perf.tickets
        """)

        before_rows = cursor.execute(query).fetchall()

        results.append(
            measure(cursor, "without_index", query)
        )


        # Эксперимент с индексом

        cursor.execute("""
            CREATE INDEX idx_tickets_status_created
            ON helpdesk_perf.tickets (
                status,
                created_at DESC,
                id DESC
            )
        """)

        cursor.execute("""
            ANALYZE helpdesk_perf.tickets
        """)

        after_rows = cursor.execute(query).fetchall()

        assert before_rows == after_rows

        results.append(
            measure(cursor, "with_index", query)
        )


        # Проверка эквивалентности пагинации

        offset_rows = cursor.execute(
            offset_query
        ).fetchall()

        cursor_rows = cursor.execute(
            cursor_query
        ).fetchall()

        assert offset_rows == cursor_rows


        # Сравнение способов пагинации

        results.append(
            measure(cursor, "offset", offset_query)
        )

        results.append(
            measure(cursor, "keyset", cursor_query)
        )


# Сохранение результатов

output = root / "data" / "database_benchmark.csv"

output.parent.mkdir(
    parents=True,
    exist_ok=True
)

with output.open(
    "w",
    encoding="utf-8",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=list(results[0].keys())
    )

    writer.writeheader()
    writer.writerows(results)


# Вывод результатов

for result in results:

    print("\nСценарий:", result["scenario"])

    print(
        "Среднее время:",
        result["average_ms"],
        "мс"
    )

    print(
        "Медиана:",
        result["median_ms"],
        "мс"
    )

    print(
        "Максимальное время:",
        result["maximum_ms"],
        "мс"
    )


print("\nРезультаты сохранены:", output)