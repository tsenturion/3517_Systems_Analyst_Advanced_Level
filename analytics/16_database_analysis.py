from pathlib import Path
import pandas as pd


root = Path(__file__).resolve().parents[1]

data = pd.read_csv(
    root / "data" / "database_benchmark.csv"
)

data = data.set_index("scenario")


# Эффект создания индекса

before = data.loc["without_index", "median_ms"]
after = data.loc["with_index", "median_ms"]

if before > 0 and after > 0:

    improvement = (
        (before - after) / before * 100
    )

    speedup = before / after

    print("Эффект индекса")

    print(
        "Изменение времени:",
        round(improvement, 2),
        "%"
    )

    print(
        "Коэффициент ускорения:",
        round(speedup, 2)
    )


# Эффект курсорной пагинации

offset = data.loc["offset", "median_ms"]
keyset = data.loc["keyset", "median_ms"]

if offset > 0 and keyset > 0:

    improvement = (
        (offset - keyset) / offset * 100
    )

    speedup = offset / keyset

    print("\nЭффект курсорной пагинации")

    print(
        "Изменение времени:",
        round(improvement, 2),
        "%"
    )

    print(
        "Коэффициент ускорения:",
        round(speedup, 2)
    )


print("\nИсходные результаты:")

print(data.to_string())