from pathlib import Path

import numpy as np
import pandas as pd


root = Path(__file__).resolve().parents[1]

data = pd.read_csv(
    root / "data" / "api_metrics_clean.csv"
)

successful = data[
    data["status_code"].between(200, 299)
]

if successful.empty:
    raise SystemExit("Нет успешных запросов")

times = successful["duration_ms"].to_numpy()

# Расчёт показателей

total = len(data)
success_count = len(successful)

client_errors = len(
    data[data["status_code"].between(400, 499)]
)

server_errors = len(
    data[data["status_code"].between(500, 599)]
)

average_ms = round(float(np.mean(times)), 2)
median_ms = round(float(np.median(times)), 2)
p95_ms = round(float(np.percentile(times, 95)), 2)

error_percent = round(
    server_errors / total * 100,
    2
)

# Предварительная оценка

if p95_ms <= 400:
    performance = "Учебный ориентир P95 соблюдён."
else:
    performance = "Учебный ориентир P95 превышен."

if error_percent <= 1:
    reliability = "Учебный ориентир по ошибкам соблюдён."
else:
    reliability = "Учебный ориентир по ошибкам превышен."

# Формирование отчёта

report = f"""# Анализ производительности HelpDesk

## Результаты измерений

| Показатель | Значение |
|---|---:|
| Всего запросов | {total} |
| Успешные запросы | {success_count} |
| Ответы 4xx | {client_errors} |
| Ответы 5xx | {server_errors} |
| Среднее время успешных запросов | {average_ms} мс |
| Медиана | {median_ms} мс |
| P95 | {p95_ms} мс |
| Доля серверных ошибок | {error_percent}% |

## Время ответа

![Время ответа](charts/response_times.png)

## Распределение HTTP-статусов

![HTTP-статусы](charts/http_statuses.png)

## Распределение продолжительности запросов

![Гистограмма](charts/response_histogram.png)

## Предварительные выводы

{performance}

{reliability}

Результаты относятся к собранной учебной выборке.
Для проверки эксплуатационных требований необходимо
использовать измерения за согласованный период.

Время ответа измерялось со стороны Python-клиента.
Преднамеренные ответы 404 и 422 учитывались
при анализе статусов, но исключались из
расчёта продолжительности успешных операций.
"""

# Сохранение результата

output = (
    root
    / "docs"
    / "analytics"
    / "20-visual-report.md"
)

output.write_text(report, encoding="utf-8")

print("Отчёт создан:", output)