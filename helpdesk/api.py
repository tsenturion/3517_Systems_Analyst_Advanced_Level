from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .application import TicketService
from .adapters import (
    JsonTicketRepository,
    RabbitEventPublisher
)


app = FastAPI(title="HelpDesk")

repository = JsonTicketRepository()
publisher = RabbitEventPublisher()

service = TicketService(
    repository=repository,
    publisher=publisher
)


class NewTicket(BaseModel):
    title: str = Field(min_length=1)
    description: str
    creator_id: str
    category_id: str


@app.post("/tickets", status_code=201)
def create_ticket(data: NewTicket):
    ticket = service.create_ticket(
        **data.model_dump()
    )

    return asdict(ticket)


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    try:
        ticket = service.get_ticket(ticket_id)
        return asdict(ticket)

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )