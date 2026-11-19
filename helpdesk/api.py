"""HTTP API HelpDesk.

Предоставляет маршруты для создания заявок, получения заявки по идентификатору
и изменения её статуса.
"""

from .domain import TicketStatus
from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .application import TicketService
from .outbox_repository import SqliteTicketRepository


app = FastAPI(title="HelpDesk")

repository = SqliteTicketRepository()
service = TicketService(repository)


class NewTicket(BaseModel):
    """Данные для создания новой заявки."""

    title: str = Field(min_length=1)
    description: str
    creator_id: str
    category_id: str


@app.post("/tickets", status_code=201)
def create_ticket(data: NewTicket):
    """Создаёт новую заявку.

    Принимает название, описание, идентификатор автора и категории.
    Возвращает созданную заявку в виде словаря со статусом HTTP 201.
    """
    ticket = service.create_ticket(
        **data.model_dump()
    )
    return asdict(ticket)


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    """Возвращает заявку по идентификатору.

    Вызывает исключение HTTP 404, если заявка не найдена.
    """
    try:
        return asdict(service.get_ticket(ticket_id))
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )


class TicketStatusPatch(BaseModel):
    """Новые данные статуса заявки."""

    status: TicketStatus
    user_id: str = Field(min_length=1)


@app.patch("/tickets/{ticket_id}")
def patch_ticket(
    ticket_id: str,
    data: TicketStatusPatch
):
    """Изменяет статус заявки.

    Принимает новый статус и идентификатор пользователя, который выполняет
    изменение. Возвращает обновлённую заявку или HTTP 404 для неизвестного
    идентификатора заявки.
    """
    try:
        ticket = service.change_status(
            ticket_id=ticket_id,
            new_status=data.status.value,
            user_id=data.user_id
        )

        return asdict(ticket)

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )