users = 1000

tickets_per_user_month = 4
comments_per_ticket = 5
changes_per_ticket = 3

months = 36

# Прогноз количества записей

tickets = users * tickets_per_user_month * months

comments = tickets * comments_per_ticket
changes = tickets * changes_per_ticket

total = tickets + comments + changes


# Предполагаемый размер одной записи в байтах

ticket_bytes = 2048
comment_bytes = 1024
change_bytes = 256


# Прогноз объёма данных

storage_bytes = (
    tickets * ticket_bytes
    + comments * comment_bytes
    + changes * change_bytes
)

storage_mb = storage_bytes / 1024 / 1024

# Учебный коэффициент запаса для хранения

storage_reserve = 2

print("Период прогнозирования:", months, "месяцев")

print("Заявок:", tickets)
print("Комментариев:", comments)
print("Изменений статусов:", changes)

print("Всего записей:", total)

print("Полезные данные:", round(storage_mb, 2), "МиБ")

print(
    "Ориентир с запасом:",
    round(storage_mb * storage_reserve, 2),
    "МиБ"
)