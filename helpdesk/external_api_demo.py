
import json

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


url = "https://api.github.com/repos/fastapi/fastapi"

request = Request(
    url,
    headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "HelpDesk-API-Lesson"
    }
)

try:
    with urlopen(request, timeout=10) as response:
        data = json.load(response)

        print("HTTP:", response.status)
        print("Репозиторий:", data["full_name"])
        print("Описание:", data.get("description"))
        print("Основная ветка:", data["default_branch"])
        print("Звёзды:", data["stargazers_count"])

        print(
            "Осталось запросов:",
            response.headers.get("X-RateLimit-Remaining")
        )

except HTTPError as error:
    print("Ошибка API:", error.code)

except URLError as error:
    print("Ошибка соединения:", error.reason)