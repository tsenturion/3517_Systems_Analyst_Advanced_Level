from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


root = Path(__file__).resolve().parents[1]

data = pd.read_csv(
    root / "data" / "api_metrics_clean.csv"
)

output = root / "docs" / "analytics" / "charts"
output.mkdir(parents=True, exist_ok=True)

successful = data[
    data["status_code"].between(200, 299)
]

times = successful["duration_ms"]

if times.empty:
    raise SystemExit("Нет успешных запросов")


# График 1. Время ответа

plt.figure(figsize=(10, 5))

plt.plot(
    range(1, len(times) + 1),
    times,
    marker="o",
    label="Время ответа"
)

plt.axhline(
    y=200,
    linestyle="--",
    label="Учебный порог 200 мс"
)

plt.title("Время ответа API HelpDesk")
plt.xlabel("Номер успешного запроса")
plt.ylabel("Время ответа, мс")

plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(output / "response_times.png", dpi=150)
plt.close()


# График 2. Распределение HTTP-статусов

status_counts = data["status_code"].value_counts()
status_counts = status_counts.sort_index()

plt.figure(figsize=(8, 5))

plt.bar(
    status_counts.index.astype(str),
    status_counts.values
)

plt.title("Распределение HTTP-статусов")
plt.xlabel("HTTP-статус")
plt.ylabel("Количество запросов")

plt.tight_layout()

plt.savefig(output / "http_statuses.png", dpi=150)
plt.close()


# График 3. Распределение времени ответа

plt.figure(figsize=(9, 5))

plt.hist(
    times,
    bins=min(5, len(times)),
    edgecolor="black"
)

plt.title("Распределение времени ответа")
plt.xlabel("Время ответа, мс")
plt.ylabel("Количество запросов")

plt.tight_layout()

plt.savefig(output / "response_histogram.png", dpi=150)
plt.close()


print("Графики сохранены в:", output)