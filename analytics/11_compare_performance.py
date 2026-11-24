from pathlib import Path

import pandas as pd
import numpy as np


root = Path(__file__).resolve().parents[1]

data = pd.read_csv(
    root / "data" / "load_experiment.csv"
)

runs = pd.read_csv(
    root / "data" / "load_runs.csv"
)


# Подготовка аналитических признаков

data["success"] = data["status_code"] == 200

data["within_400"] = (
    data["success"] & (data["duration_ms"] <= 400)
)

data["server_error"] = data["status_code"].between(500, 599)

data["connection_error"] = data["status_code"] == 0


# Агрегирование результатов отдельных запусков

statistics = data.groupby(
    "run_id",
    as_index=False
).agg(
    attempts=("status_code", "count"),
    successful=("success", "sum"),
    within_400=("within_400", "sum"),
    server_errors=("server_error", "sum"),
    connection_errors=("connection_error", "sum")
)

successful = data[data["success"]]

percentiles = (
    successful.groupby("run_id")["duration_ms"]
    .quantile(0.95)
    .reset_index(name="p95_ms")
)


# Объединение таблиц

result = runs.merge(
    statistics,
    on="run_id",
    validate="one_to_one"
)

result = result.merge(
    percentiles,
    on="run_id",
    how="left"
)


# Расчёт производительности каждого запуска

result["throughput"] = (
    result["successful"] / result["elapsed_seconds"]
)

result["error_percent"] = (
    (result["attempts"] - result["successful"])
    / result["attempts"] * 100
)

result["within_400_percent"] = (
    result["within_400"] / result["attempts"] * 100
)

print("Результаты отдельных запусков:")

print(
    result[
        [
            "run_id",
            "workers",
            "p95_ms",
            "throughput",
            "error_percent"
        ]
    ].round(2).to_string(index=False)
)


# Сравнение двух режимов

summary = []

for mode in ["baseline", "parallel"]:

    group = data[data["mode"] == mode]
    group_runs = result[result["mode"] == mode]

    good = group[group["success"]]
    times = good["duration_ms"].to_numpy()

    if len(times) > 0:
        average = np.mean(times)
        median = np.median(times)
        p95 = np.percentile(times, 95)
    else:
        average = np.nan
        median = np.nan
        p95 = np.nan

    summary.append({
        "mode": mode,
        "requests": len(group),
        "successful": len(good),
        "average_ms": average,
        "median_ms": median,
        "p95_ms": p95,
        "throughput": (
            len(good) / group_runs["elapsed_seconds"].sum()
        ),
        "error_percent": (
            (len(group) - len(good)) / len(group) * 100
        ),
        "within_400_percent": (
            group["within_400"].mean() * 100
        )
    })


summary = pd.DataFrame(summary)

print("\nСравнение режимов:")
print(summary.round(2).to_string(index=False))


# Сохранение результатов

result.to_csv(
    root / "data" / "load_run_statistics.csv",
    index=False
)

summary.to_csv(
    root / "data" / "load_comparison.csv",
    index=False
)