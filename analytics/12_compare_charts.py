from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


root = Path(__file__).resolve().parents[1]

data = pd.read_csv(
    root / "data" / "load_experiment.csv"
)

output = root / "docs" / "analytics" / "charts"
output.mkdir(parents=True, exist_ok=True)


# Выбираем успешные запросы

baseline = data[
    (data["mode"] == "baseline")
    & (data["status_code"] == 200)
]["duration_ms"]

parallel = data[
    (data["mode"] == "parallel")
    & (data["status_code"] == 200)
]["duration_ms"]


# Диаграмма размаха

plt.figure(figsize=(10, 6))

if not baseline.empty and not parallel.empty:
    plt.boxplot([baseline, parallel])

    plt.xticks(
        [1, 2],
        ["Последовательно", "Параллельно"]
    )

    plt.axhline(
        y=400,
        linestyle="--",
        label="Учебный ориентир 400 мс"
    )

    plt.legend()

else:
    plt.text(
        0.5, 0.5,
        "Недостаточно успешных запросов",
        ha="center",
        transform=plt.gca().transAxes
    )

plt.title("Сравнение времени ответа HelpDesk")
plt.ylabel("Время ответа, мс")
plt.grid(axis="y")
plt.tight_layout()

plt.savefig(
    output / "load_comparison.png",
    dpi=150
)

plt.close()