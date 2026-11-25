# Исходные параметры

users = 1000
requests_per_user = 24
working_hours = 8

peak_users = 200
requests_per_minute = 6

sql_per_request = 3
reserve = 1.5

average_response_seconds = 0.2


# Средняя нагрузка

daily_requests = users * requests_per_user

working_seconds = working_hours * 60 * 60

average_rps = daily_requests / working_seconds


# Пиковая нагрузка

peak_rps = peak_users * requests_per_minute / 60


# Нагрузка с учётом запаса

target_rps = peak_rps * reserve

target_qps = target_rps * sql_per_request


# Среднее количество запросов в обработке

concurrent_requests = (
    target_rps * average_response_seconds
)


# Результаты

print("Запросов за рабочий день:", daily_requests)

print("Средний RPS:", round(average_rps, 2))
print("Пиковый RPS:", round(peak_rps, 2))

print("Целевой RPS:", round(target_rps, 2))
print("Целевой QPS:", round(target_qps, 2))

print(
    "Среднее количество запросов в обработке:",
    round(concurrent_requests, 2)
)