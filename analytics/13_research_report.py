from pathlib import Path

import pandas as pd


root = Path(__file__).resolve().parents[1]

summary = pd.read_csv(
    root / "data" / "load_comparison.csv"
).set_index("mode")

runs = pd.read_csv(
    root / "data" / "load_run_statistics.csv"
)

baseline = summary.loc["baseline"]
parallel = summary.loc["parallel"]


# Расчёт относительного изменения

def calculate_change(old, new):

    if pd.isna(old) or pd.isna(new) or old == 0:
        return "Недостаточно данных"

    change = (new - old) / old * 100

    return f"{change:+.2f}%"


latency_change = calculate_change(
    baseline["p95_ms"],
    parallel["p95_ms"]
)

throughput_change = calculate_change(
    baseline["throughput"],
    parallel["throughput"]
)


# Сопоставление результатов раундов

paired = runs.pivot(
    index="round",
    columns="mode",
    values="p95_ms"
).dropna()

increased = (
    paired["parallel"] > paired["baseline"]
).sum()

decreased = (
    paired["parallel"] < paired["baseline"]
).sum()


# Проверка гипотезы

if len(paired) < 3:
    hypothesis = (
        "Недостаточно успешных измерений "
        "для сопоставления всех раундов."
    )

elif increased == 3:
    hypothesis = (
        "Наблюдения поддерживают гипотезу H-001: "
        "P95 увеличился во всех трёх раундах."
    )

elif decreased == 3:
    hypothesis = (
        "Наблюдается противоположная закономерность: "
        "P95 уменьшился во всех трёх раундах."
    )

else:
    hypothesis = (
        "Устойчивая закономерность увеличения "
        "времени ответа не выявлена."
    )


# Формирование рекомендации

if parallel["error_percent"] > 1:

    recommendation = (
        "Исследовать причины ошибок API "
        "при параллельной обработке."
    )

elif pd.isna(parallel["p95_ms"]):

    recommendation = (
        "Восстановить работоспособность API "
        "и повторить эксперимент."
    )

elif parallel["p95_ms"] > 400:

    recommendation = (
        "Исследовать производительность серверной "
        "логики и операций получения данных."
    )

else:

    recommendation = (
        "Продолжить исследование при большей "
        "нагрузке и более длительном наблюдении."
    )


# Подготовка аналитического отчёта

report = f"""# Исследование производительности HelpDesk

## 1. Цель исследования

Определить влияние параллельных HTTP-запросов
на производительность API.

## 2. Условия эксперимента

Операция: GET /tickets?limit=20&offset=0.

Последовательный режим: один клиентский поток.

Параллельный режим: до пяти клиентских потоков.

Каждый режим выполнялся три раза.

## 3. Результаты

| Показатель | Последовательно | Параллельно |
|---|---:|---:|
| Запросов | {baseline["requests"]:.0f} | {parallel["requests"]:.0f} |
| Успешных запросов | {baseline["successful"]:.0f} | {parallel["successful"]:.0f} |
| Среднее время, мс | {baseline["average_ms"]:.2f} | {parallel["average_ms"]:.2f} |
| Медиана, мс | {baseline["median_ms"]:.2f} | {parallel["median_ms"]:.2f} |
| P95, мс | {baseline["p95_ms"]:.2f} | {parallel["p95_ms"]:.2f} |
| Успешных запросов в секунду | {baseline["throughput"]:.2f} | {parallel["throughput"]:.2f} |
| Доля неуспешных попыток, % | {baseline["error_percent"]:.2f} | {parallel["error_percent"]:.2f} |
| Успешных за 400 мс, % от всех попыток | {baseline["within_400_percent"]:.2f} | {parallel["within_400_percent"]:.2f} |

## 4. Изменение показателей

Изменение P95: **{latency_change}**.

Изменение пропускной способности: **{throughput_change}**.

## 5. Визуализация результатов

![Сравнение времени ответа](charts/load_comparison.png)

![Пропускная способность](charts/throughput_comparison.png)

## 6. Проверка гипотезы

{hypothesis}

Раундов с доступными результатами P95: {len(paired)}.

Раундов с увеличением P95: {increased}.

Раундов с уменьшением P95: {decreased}.

## 7. Рекомендации

{recommendation}

## 8. Ограничения исследования

Эксперимент проведён в локальном окружении.

Использовались короткие серии запросов.

Исследовалась одна операция API.

Результаты характеризуют конкретные условия эксперимента.
Проверка гипотезы носит описательный характер.

Для оценки эксплуатационной производительности
необходимы дополнительные измерения.
"""

output = (
    root
    / "docs"
    / "analytics"
    / "22-performance-research-report.md"
)

output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(report, encoding="utf-8")

print("Изменение P95:", latency_change)
print("Изменение пропускной способности:", throughput_change)
print("Результат:", hypothesis)
print("Рекомендация:", recommendation)
print("Отчёт сохранён:", output)