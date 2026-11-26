import json

from urllib.request import Request, urlopen
from urllib.error import HTTPError


BASE_URL = "http://127.0.0.1:8000"


def request_api(method, path, data=None):

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")

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
        with error:
            return error.code, json.load(error)


# Подготовка данных для приёмки

ticket_ids = []

for number in range(1, 4):

    status, ticket = request_api(
        "POST",
        "/tickets",
        {
            "title": f"Приёмка HelpDesk №{number}",
            "description": "Учебная проверка API",
            "creator_id": "user-anna",
            "category_id": "software"
        }
    )

    assert status == 201

    ticket_ids.append(ticket["id"])


# Изменяем статус второй заявки

status, ticket = request_api(
    "PATCH",
    f"/tickets/{ticket_ids[1]}",
    {
        "status": "IN_PROGRESS",
        "user_id": "user-oleg"
    }
)

assert status == 200
assert ticket["status"] == "IN_PROGRESS"


# AC-001. Получение списка

status, data = request_api("GET", "/tickets")

assert status == 200
assert isinstance(data["items"], list)

print("AC-001: PASS")


# AC-002. Фильтрация

status, data = request_api(
    "GET",
    "/tickets?status=NEW&limit=2"
)

assert status == 200
assert len(data["items"]) == 2

for ticket in data["items"]:
    assert ticket["status"] == "NEW"

assert data["items"][0]["id"] == ticket_ids[2]
assert data["items"][1]["id"] == ticket_ids[0]

print("AC-002: PASS")


# AC-003. Ограничение количества

status, data = request_api(
    "GET",
    "/tickets?limit=2"
)

assert status == 200
assert len(data["items"]) == 2

print("AC-003: PASS")


# AC-004. Постраничная выдача

status1, page1 = request_api(
    "GET",
    "/tickets?limit=1&offset=0"
)

status2, page2 = request_api(
    "GET",
    "/tickets?limit=1&offset=1"
)

assert status1 == 200
assert status2 == 200

assert page1["items"][0]["id"] == ticket_ids[2]
assert page2["items"][0]["id"] == ticket_ids[1]

print("AC-004: PASS")


# AC-005. Пустой результат

total = page1["total"]

status, data = request_api(
    "GET",
    f"/tickets?limit=1&offset={total}"
)

assert status == 200
assert data["items"] == []
assert data["total"] == total

print("AC-005: PASS")


# AC-006. Некорректные параметры

invalid_requests = [
    "/tickets?limit=0",
    "/tickets?limit=101",
    "/tickets?offset=-1",
    "/tickets?status=UNKNOWN"
]

for path in invalid_requests:

    status, data = request_api("GET", path)

    assert status == 422

print("AC-006: PASS")

print("\nВсе шесть критериев API выполнены")