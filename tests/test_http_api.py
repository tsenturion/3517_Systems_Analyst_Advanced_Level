import pytest
import requests


BASE_URL = "http://127.0.0.1:8000"


def test_create_and_get_ticket():

    response = requests.post(
        f"{BASE_URL}/tickets",
        json={
            "title": "API test",
            "description": "Automated testing",
            "creator_id": "user-anna",
            "category_id": "software"
        },
        timeout=5
    )

    assert response.status_code == 201

    ticket = response.json()

    assert ticket["status"] == "NEW"

    ticket_id = ticket["id"]

    response = requests.get(
        f"{BASE_URL}/tickets/{ticket_id}",
        timeout=5
    )

    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


def test_unknown_ticket():

    response = requests.get(
        f"{BASE_URL}/tickets/unknown-ticket",
        timeout=5
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "limit, expected_status",
    [
        (0, 422),
        (1, 200),
        (20, 200),
        (100, 200),
        (101, 422)
    ]
)
def test_pagination(limit, expected_status):

    response = requests.get(
        f"{BASE_URL}/tickets",
        params={"limit": limit},
        timeout=5
    )

    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()

        assert data["limit"] == limit
        assert len(data["items"]) <= limit


def test_status_filter():

    response = requests.get(
        f"{BASE_URL}/tickets",
        params={"status": "NEW"},
        timeout=5
    )

    assert response.status_code == 200

    for ticket in response.json()["items"]:
        assert ticket["status"] == "NEW"