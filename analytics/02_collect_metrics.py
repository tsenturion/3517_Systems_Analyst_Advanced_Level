import csv
import time

from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import os

os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1"

BASE_URL = "http://127.0.0.1:8000"

scenarios = [
    ("GET /tickets", "/tickets?limit=5&offset=0")
] * 8 + [
    ("GET /tickets/{ticket_id}", "/tickets/unknown-demo-ticket"),
    ("GET /tickets", "/tickets?limit=0")
]

measurements = []

for route, path in scenarios:
    started = time.perf_counter()

    try:
        with urlopen(BASE_URL + path, timeout=5) as response:
            status = response.status
            response.read()

    except HTTPError as error:
        status = error.code
        error.read()

    except (URLError, TimeoutError, OSError) as error:
        raise SystemExit(
            "Нет соединения с HelpDesk. Проверьте запуск Uvicorn. "
            f"Подробности: {error}"
        )

    duration_ms = round(
        (time.perf_counter() - started) * 1000,
        2
    )

    measurements.append({
        "timestamp_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "route": route,
        "status_code": status,
        "duration_ms": duration_ms
    })

output = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "api_metrics.csv"
)

output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "timestamp_utc",
            "route",
            "status_code",
            "duration_ms"
        ]
    )

    writer.writeheader()
    writer.writerows(measurements)

print(f"Сохранено измерений: {len(measurements)}")
print(f"Файл: {output}")

for row in measurements:
    print(
        row["route"],
        row["status_code"],
        row["duration_ms"],
        "мс"
    )