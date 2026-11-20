import csv
from pathlib import Path


root = Path(__file__).resolve().parents[1]
source = root / "data" / "api_metrics.csv"

if not source.exists():
    raise SystemExit("Сначала запустите 02_collect_metrics.py")

with source.open("r", encoding="utf-8", newline="") as file:
    measurements = list(csv.DictReader(file))

if not measurements:
    raise SystemExit("Файл измерений пуст")


# Подготовка переменных

requests_count = len(measurements)

successful = 0
client_errors = 0
server_errors = 0

successful_durations = []
groups = {}


# Анализ измерений

for row in measurements:
    status = int(row["status_code"])
    duration = float(row["duration_ms"])

    if 200 <= status < 300:
        successful += 1
        successful_durations.append(duration)

    elif 400 <= status < 500:
        client_errors += 1

    elif 500 <= status < 600:
        server_errors += 1

    key = row["route"] + " / HTTP " + str(status)

    if key not in groups:
        groups[key] = []

    groups[key].append(duration)


# Расчёт показателей

if not successful_durations:
    raise SystemExit("Нет успешных запросов для анализа времени")

average_ms = round(
    sum(successful_durations) / len(successful_durations),
    2
)

maximum_ms = max(successful_durations)

error_percent = round(
    server_errors / requests_count * 100,
    2
)


# Вывод результатов

print("Всего запросов:", requests_count)
print("Успешных 2xx:", successful)
print("Ошибок клиента 4xx:", client_errors)
print("Ошибок сервера 5xx:", server_errors)

print("Среднее время 2xx:", average_ms, "мс")
print("Максимальное время 2xx:", maximum_ms, "мс")
print("Доля ответов 5xx:", error_percent, "%")


# Формирование отчёта

lines = [
    "# Анализ технологических метрик HelpDesk",
    "",
    f"Период (UTC): {measurements[0]['timestamp_utc']} — "
    f"{measurements[-1]['timestamp_utc']}.",
    "",
    f"Количество запросов: **{requests_count}**.",
    f"Успешных ответов 2xx: **{successful}**.",
    f"Ответов 4xx: **{client_errors}**.",
    f"Ответов 5xx: **{server_errors}**.",
    f"Среднее время успешных запросов: **{average_ms} мс**.",
    f"Максимальное время успешных запросов: **{maximum_ms} мс**.",
    f"Доля ответов 5xx: **{error_percent}%**.",
    "",
    "## Время ответа по группам",
    "",
    "| Маршрут и статус | Запросов | Среднее время, мс |",
    "|---|---:|---:|"
]

for key, durations in groups.items():
    group_average = round(
        sum(durations) / len(durations),
        2
    )

    lines.append(
        f"| {key} | {len(durations)} | {group_average} |"
    )


# Проверка учебных порогов

lines.append("")
lines.append("## Предварительная оценка")
lines.append("Учебные ориентиры: 200 мс и 1% ответов 5xx.")

if average_ms > 200 or error_percent > 1:
    lines.append(
        "Обнаружено превышение учебных ориентиров. "
        "Требуется дополнительное исследование."
    )
else:
    lines.append(
        "В учебной выборке пороговые значения не превышены."
    )

lines.append("")
lines.append(
    "Ответы 404 и 422 вызваны специально для проверки API. "
    "Среднее время рассчитывается только по успешным запросам."
)
lines.append(
    "Измерено время полного запроса со стороны Python-клиента."
)
lines.append(
    "Выборка слишком мала для оценки соблюдения "
    "эксплуатационного SLO."
)


# Сохранение Markdown-отчёта

report = root / "docs" / "analytics" / "18-api-metrics-report.md"

report.parent.mkdir(parents=True, exist_ok=True)

report.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8"
)

print("Отчёт сохранён:", report)