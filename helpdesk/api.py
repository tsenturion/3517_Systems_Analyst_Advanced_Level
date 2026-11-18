from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .application import TicketService
from .outbox_repository import SqliteTicketRepository


app = FastAPI(title="HelpDesk")

repository = SqliteTicketRepository()
service = TicketService(repository)


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
        return asdict(service.get_ticket(ticket_id))
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )