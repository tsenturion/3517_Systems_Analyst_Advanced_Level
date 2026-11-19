"""HTTP API системы HelpDesk.

Маршруты модуля позволяют получать и создавать заявки, а также изменять
их статус.
"""

from dataclasses import asdict

from fastapi import FastAPI, HTTPException, Path, Query

from .application import TicketService
from .domain import TicketStatus
from .outbox_repository import SqliteTicketRepository
from .schemas import (
    ApiError,
    TicketCreate,
    TicketPage,
    TicketRead,
    TicketStatusPatch
)


app = FastAPI(
    title="HelpDesk API",
    version="1.0.0",
    description="API системы технической поддержки"
)

repository = SqliteTicketRepository()
service = TicketService(repository)


@app.get(
    "/tickets",
    response_model=TicketPage,
    tags=["Tickets"],
    summary="Получение списка заявок",
    operation_id="listTickets"
)
def list_tickets(
    status: TicketStatus | None = Query(
        default=None,
        description="Фильтр по статусу заявки"
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Размер страницы"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Смещение от начала списка"
    )
):
    """Возвращает постраничный список заявок.

    При указании статуса возвращаются только заявки с выбранным статусом.
    Параметры limit и offset задают размер страницы и смещение.
    """
    return service.list_tickets(
        status=status.value if status else None,
        limit=limit,
        offset=offset
    )


@app.post(
    "/tickets",
    response_model=TicketRead,
    status_code=201,
    tags=["Tickets"],
    summary="Создание заявки",
    operation_id="createTicket"
)
def create_ticket(data: TicketCreate):
    """Создаёт новую заявку.

    Принимает заголовок, описание, автора и категорию обращения.
    Возвращает созданную заявку со статусом HTTP 201.
    """
    ticket = service.create_ticket(
        **data.model_dump()
    )
    return asdict(ticket)


@app.get(
    "/tickets/{ticket_id}",
    response_model=TicketRead,
    tags=["Tickets"],
    summary="Получение заявки по идентификатору",
    operation_id="getTicketById",
    responses={
        404: {
            "model": ApiError,
            "description": "Заявка не найдена"
        }
    }
)
def get_ticket(
    ticket_id: str = Path(
        description="Уникальный идентификатор заявки"
    )
):
    """Возвращает заявку по идентификатору.

    Возвращает HTTP 404, если заявка с указанным идентификатором не найдена.
    """
    try:
        return asdict(service.get_ticket(ticket_id))
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Заявка не найдена"
        )


@app.patch(
    "/tickets/{ticket_id}",
    response_model=TicketRead,
    tags=["Tickets"],
    summary="Изменение статуса заявки",
    operation_id="updateTicketStatus",
    responses={
        404: {
            "model": ApiError,
            "description": "Заявка не найдена"
        }
    }
)
def patch_ticket(
    data: TicketStatusPatch,
    ticket_id: str = Path(
        description="Уникальный идентификатор заявки"
    )
):
    """Изменяет статус заявки.

    Принимает данные нового статуса и идентификатор пользователя,
    выполняющего изменение. Возвращает HTTP 404 для неизвестной заявки.
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