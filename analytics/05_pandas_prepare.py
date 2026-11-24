from pathlib import Path
import pandas as pd


root = Path(__file__).resolve().parents[1]
source = root / "data" / "api_metrics.csv"
output = root / "data" / "api_metrics_clean.csv"

if not source.exists():
    raise SystemExit("Сначала создайте файл api_metrics.csv")

data = pd.read_csv(source)

print("Исходная таблица:")
print(data.head())

print("\nРазмер таблицы:", data.shape)
print("\nТипы столбцов:")
print(data.dtypes)

# Преобразование типов

data["timestamp_utc"] = pd.to_datetime(
    data["timestamp_utc"],
    utc=True,
    errors="coerce"
)

data["status_code"] = pd.to_numeric(
    data["status_code"],
    errors="coerce"
)

data["duration_ms"] = pd.to_numeric(
    data["duration_ms"],
    errors="coerce"
)

# Подготовка данных

before = len(data)

data = data.dropna(
    subset=[
        "timestamp_utc",
        "route",
        "status_code",
        "duration_ms"
    ]
)

data = data[
    (data["duration_ms"] >= 0)
    & (data["status_code"].between(100, 599))
]

data["status_code"] = data["status_code"].astype(int)

data = data.sort_values("timestamp_utc")
data = data.reset_index(drop=True)

if data.empty:
    raise SystemExit("После проверки не осталось данных")

data.to_csv(output, index=False)

print("\nПодготовлено строк:", len(data))
print("Исключено строк:", before - len(data))
print("Файл:", output)