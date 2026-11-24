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

times = successful["duration_ms"].to_numpy()

if len(times) == 0:
    raise SystemExit("Нет успешных запросов")

# Основные статистические показатели

average = np.mean(times)
median = np.median(times)
minimum = np.min(times)
maximum = np.max(times)

p90 = np.percentile(times, 90)
p95 = np.percentile(times, 95)

std = np.std(times)

# Количество медленных запросов

slow_requests = np.sum(times > 200)

# Доля серверных ошибок

server_errors = data[
    data["status_code"].between(500, 599)
]

error_percent = len(server_errors) / len(data) * 100

print("Среднее время:", round(average, 2), "мс")
print("Медиана:", round(median, 2), "мс")
print("Минимум:", round(minimum, 2), "мс")
print("Максимум:", round(maximum, 2), "мс")
print("P90:", round(p90, 2), "мс")
print("P95:", round(p95, 2), "мс")
print("Стандартное отклонение:", round(std, 2))
print("Запросов дольше 200 мс:", slow_requests)
print("Доля ответов 5xx:", round(error_percent, 2), "%")