from pathlib import Path
import pandas as pd


root = Path(__file__).resolve().parents[1]

data = pd.read_csv(
    root / "data" / "api_metrics_clean.csv"
)

# Выбираем успешные запросы

successful = data[
    data["status_code"].between(200, 299)
]

print("Всего измерений:", len(data))
print("Успешных запросов:", len(successful))

# Распределение HTTP-статусов

status_stats = (
    data.groupby("status_code")
    .size()
    .reset_index(name="requests")
)

print("\nРаспределение HTTP-статусов:")
print(status_stats.to_string(index=False))

# Показатели времени по маршрутам

route_stats = successful.groupby(
    "route",
    as_index=False
).agg(
    requests=("duration_ms", "count"),
    average_ms=("duration_ms", "mean"),
    minimum_ms=("duration_ms", "min"),
    maximum_ms=("duration_ms", "max")
)

route_stats = route_stats.round(2)

print("\nПоказатели по маршрутам:")
print(route_stats.to_string(index=False))

# Сохранение результатов

status_stats.to_csv(
    root / "data" / "status_stats.csv",
    index=False
)

route_stats.to_csv(
    root / "data" / "route_stats.csv",
    index=False
)