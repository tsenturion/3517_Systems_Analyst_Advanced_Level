import json
from pathlib import Path

from .api import app


def main():
    specification = app.openapi()

    output = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "api"
        / "openapi.json"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output.write_text(
        json.dumps(
            specification,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("Спецификация:", output)
    print("OpenAPI:", specification["openapi"])
    print("Версия API:", specification["info"]["version"])
    print("Ресурсы:", list(specification["paths"]))


if __name__ == "__main__":
    main()