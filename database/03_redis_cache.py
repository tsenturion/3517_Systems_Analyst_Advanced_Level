import json
import time
import redis

from urllib.request import urlopen
from urllib.error import URLError


cache = redis.Redis(
    host="127.0.0.1",
    port=56379,
    password="helpdesk_dev_only",
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1
)

API_URL = (
    "http://127.0.0.1:8000"
    "/tickets?limit=5&offset=0"
)

CACHE_KEY = "helpdesk:api:v1:tickets:all:limit=5:offset=0"
CACHE_TTL = 60


def get_tickets():

    # Проверяем наличие данных в Redis

    try:
        cached = cache.get(CACHE_KEY)

        if cached is not None:
            return json.loads(cached), "CACHE HIT"

    except (redis.RedisError, json.JSONDecodeError):
        print("Кеш недоступен или содержит некорректные данные")


    # Получаем данные из HelpDesk API

    try:
        with urlopen(API_URL, timeout=10) as response:
            data = json.load(response)

    except (URLError, OSError) as error:
        raise SystemExit(f"Ошибка обращения к API: {error}")


    # Сохраняем результат в Redis

    try:
        cache.set(
            CACHE_KEY,
            json.dumps(data, ensure_ascii=False),
            ex=CACHE_TTL
        )

    except redis.RedisError:
        print("Не удалось сохранить данные в кеш")

    return data, "API"


# Выполняем три одинаковых обращения

for number in range(1, 4):

    started = time.perf_counter()

    data, source = get_tickets()

    duration = (
        time.perf_counter() - started
    ) * 1000

    print(
        f"Запрос {number}: "
        f"{source}, "
        f"{duration:.2f} мс, "
        f"заявок в ответе: {len(data['items'])}"
    )