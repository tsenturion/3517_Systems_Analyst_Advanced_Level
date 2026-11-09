"""Учебный стенд для проверки подтверждения заявок на аудиторию."""

import argparse
import json
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit


def at(time):
    return datetime.fromisoformat(f"2026-10-06T{time}:00+05:00")


REQUEST_INTERVALS = {
    "REQ-900": (at("10:00"), at("11:00")),
    "REQ-101": (at("13:00"), at("14:00")),
    "REQ-102": (at("10:30"), at("11:30")),
    "REQ-103": (at("11:00"), at("12:00")),
}
BOOKED_REQUESTS = {"REQ-900"}


def interval_details(request_id):
    starts_at, ends_at = REQUEST_INTERVALS[request_id]
    return {
        "requestId": request_id,
        "roomId": "A-203",
        "startsAt": starts_at.isoformat(),
        "endsAt": ends_at.isoformat(),
    }


class BookingHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload, location=None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if location is not None:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        request_match = re.fullmatch(r"/booking-requests/REQ-([0-9]+)", path)
        if request_match:
            number = request_match[1]
            request_id = f"REQ-{number}"
            if request_id in REQUEST_INTERVALS:
                confirmed = request_id in BOOKED_REQUESTS
                self.send_json(200, {
                    **interval_details(request_id),
                    "status": "CONFIRMED" if confirmed else "PENDING",
                    "bookingId": f"BKG-{number}" if confirmed else None,
                })
                return

        booking_match = re.fullmatch(r"/bookings/BKG-([0-9]+)", path)
        if booking_match:
            number = booking_match[1]
            request_id = f"REQ-{number}"
            if request_id in BOOKED_REQUESTS:
                self.send_json(200, {
                    **interval_details(request_id),
                    "bookingId": f"BKG-{number}",
                })
                return

        self.send_json(404, {"code": "NOT_FOUND"})

    def do_POST(self):
        path = urlsplit(self.path).path
        match = re.fullmatch(r"/booking-requests/REQ-([0-9]+)/bookings", path)
        if not match:
            self.send_json(404, {"code": "NOT_FOUND"})
            return

        number = match[1]
        request_id = f"REQ-{number}"
        if request_id not in REQUEST_INTERVALS:
            self.send_json(404, {"code": "NOT_FOUND"})
            return
        if request_id in BOOKED_REQUESTS:
            self.send_json(409, {"code": "REQUEST_ALREADY_CONFIRMED"})
            return

        starts_at, ends_at = REQUEST_INTERVALS[request_id]
        for confirmed_id in BOOKED_REQUESTS:
            booked_start, booked_end = REQUEST_INTERVALS[confirmed_id]
            # Все учебные интервалы относятся к одной аудитории.
            if starts_at < booked_end and booked_start < ends_at:
                self.send_json(409, {"code": "BOOKING_CONFLICT"})
                return

        BOOKED_REQUESTS.add(request_id)
        booking_id = f"BKG-{number}"
        self.send_json(
            201,
            {**interval_details(request_id), "bookingId": booking_id},
            location=f"/bookings/{booking_id}",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Учебный стенд API бронирования")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    with HTTPServer(("127.0.0.1", args.port), BookingHandler) as server:
        print(f"Стенд запущен на http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nСтенд остановлен.")
