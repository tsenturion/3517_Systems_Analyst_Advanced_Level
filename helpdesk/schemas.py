from datetime import datetime

from pydantic import BaseModel, Field

from .domain import TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(
        min_length=1,
        description="Заголовок обращения"
    )
    description: str = Field(
        description="Описание проблемы"
    )
    creator_id: str = Field(
        description="Идентификатор автора"
    )
    category_id: str = Field(
        description="Идентификатор категории"
    )


class TicketStatusPatch(BaseModel):
    status: TicketStatus
    user_id: str = Field(
        min_length=1,
        description="Пользователь, изменяющий статус"
    )


class TicketCommentRead(BaseModel):
    id: str
    author_id: str
    text: str
    created_at: datetime


class TicketStatusChangeRead(BaseModel):
    id: str
    user_id: str
    previous_status: str
    new_status: str
    changed_at: datetime


class TicketRead(BaseModel):
    id: str
    title: str
    description: str
    creator_id: str
    category_id: str

    status: TicketStatus
    assignee_id: str | None = None

    created_at: datetime
    closed_at: datetime | None = None

    comments: list[TicketCommentRead] = Field(
        default_factory=list
    )

    changes: list[TicketStatusChangeRead] = Field(
        default_factory=list
    )


class TicketPage(BaseModel):
    items: list[TicketRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class ApiError(BaseModel):
    detail: str