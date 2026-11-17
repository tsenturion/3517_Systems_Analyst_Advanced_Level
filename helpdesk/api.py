from dataclasses import asdict
from .messaging import publish_ticket_created
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .core import HelpDesk


app = FastAPI(title="HelpDesk Integration Demo")

system = HelpDesk()


class NewTicket(BaseModel):
    title: str = Field(min_length=1)
    description: str
    creator_id: str
    category_id: str


@app.post("/tickets", status_code=201)
def create_ticket(data: NewTicket):
    ticket = system.create(**data.model_dump())
    publish_ticket_created(ticket)
    return asdict(ticket)


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    try:
        return asdict(system.get(ticket_id))
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )