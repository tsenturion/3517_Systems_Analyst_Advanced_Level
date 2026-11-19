import json

from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"


def request_api(method, path, payload=None):
    body = None

    if payload is not None:
        body = json.dumps(
            payload,
            ensure_ascii=False
        ).encode("utf-8")

    request = Request(
        BASE_URL + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.load(response)

    except HTTPError as error:
        return error.code, json.load(error)


# Создание заявки

status, ticket = request_api(
    "POST",
    "/tickets",
    {
        "title": "Не работает VPN",
        "description": "Ошибка подключения",
        "creator_id": "user-anna",
        "category_id": "network"
    }
)

assert status == 201
ticket_id = ticket["id"]
print("Создание заявки:", status, ticket_id)


# Получение заявки

status, data = request_api(
    "GET",
    f"/tickets/{ticket_id}"
)

assert status == 200
assert data["id"] == ticket_id
print("Получение заявки:", status)


# Изменение статуса

status, data = request_api(
    "PATCH",
    f"/tickets/{ticket_id}",
    {
        "status": "IN_PROGRESS",
        "user_id": "user-oleg"
    }
)

assert status == 200
assert data["status"] == "IN_PROGRESS"
print("Изменение статуса:", status)


# Получение отфильтрованной коллекции

status, data = request_api(
    "GET",
    "/tickets?status=IN_PROGRESS&limit=5&offset=0"
)

assert status == 200
assert "items" in data
assert "total" in data
print("Список заявок:", status, data["total"])


# Обращение к отсутствующей заявке

status, data = request_api(
    "GET",
    "/tickets/unknown-id"
)

assert status == 404
print("Отсутствующая заявка:", status)


# Проверка недопустимого параметра

status, data = request_api(
    "GET",
    "/tickets?limit=0"
)

assert status == 422
print("Ошибка валидации:", status)