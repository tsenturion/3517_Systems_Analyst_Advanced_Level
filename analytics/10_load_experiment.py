import time
import pandas as pd

from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor


URL = "http://127.0.0.1:8000/tickets?limit=20&offset=0"

REQUESTS = 30
ROUNDS = 3

root = Path(__file__).resolve().parents[1]

measurements = []
runs = []


def measure(request_number):
    start = time.perf_counter()

    error_name = ""

    try:
        with urlopen(URL, timeout=10) as response:
            status = response.status
            response.read()

    except HTTPError as error:
        status = error.code
        error_name = "HTTPError"
        error.close()

    except (URLError, OSError) as error:
        status = 0
        error_name = type(error).__name__

    duration = (time.perf_counter() - start) * 1000

    return {
        "request_number": request_number,
        "status_code": status,
        "duration_ms": round(duration, 3),
        "error": error_name
    }


# Предварительные запросы для прогрева приложения

for number in range(1, 4):
    result = measure(number)

    if result["status_code"] != 200:
        raise SystemExit(
            "API недоступен или возвращает ошибку. "
            "Проверьте запуск HelpDesk."
        )


# Основной эксперимент

for round_number in range(1, ROUNDS + 1):

    modes = [
        ("baseline", 1),
        ("parallel", 5)
    ]

    # Чередуем порядок режимов между раундами

    if round_number % 2 == 0:
        modes.reverse()

    for mode, workers in modes:

        run_id = f"{round_number}-{mode}"

        print("Запуск:", run_id)

        started = time.perf_counter()

        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(
                pool.map(measure, range(1, REQUESTS + 1))
            )

        elapsed = time.perf_counter() - started

        for result in results:
            result["run_id"] = run_id
            result["round"] = round_number
            result["mode"] = mode
            result["workers"] = workers

            measurements.append(result)

        runs.append({
            "run_id": run_id,
            "round": round_number,
            "mode": mode,
            "workers": workers,
            "requests": len(results),
            "elapsed_seconds": elapsed
        })

        print("Продолжительность:", round(elapsed, 2), "сек.")

        time.sleep(1)


# Сохранение результатов эксперимента

output = root / "data"
output.mkdir(parents=True, exist_ok=True)

pd.DataFrame(measurements).to_csv(
    output / "load_experiment.csv",
    index=False
)

pd.DataFrame(runs).to_csv(
    output / "load_runs.csv",
    index=False
)

print("Всего измерений:", len(measurements))
print("Всего запусков:", len(runs))