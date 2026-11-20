measurements = [
    {"status": 200, "duration_ms": 55},
    {"status": 200, "duration_ms": 80},
    {"status": 404, "duration_ms": 32},
    {"status": 200, "duration_ms": 105},
    {"status": 500, "duration_ms": 640},
    {"status": 200, "duration_ms": 75}
]

requests_count = len(measurements)
total_duration = 0
server_errors = 0

for measurement in measurements:
    total_duration += measurement["duration_ms"]

    if measurement["status"] >= 500:
        server_errors += 1

average_ms = round(total_duration / requests_count, 2)

error_percent = round(
    server_errors / requests_count * 100,
    2
)

print("Запросов:", requests_count)
print("Среднее время ответа:", average_ms, "мс")
print("Ответов 5xx:", server_errors)
print("Доля ответов 5xx:", error_percent, "%")