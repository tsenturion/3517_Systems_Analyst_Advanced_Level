from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


# Вспомогательная функция для безопасной генерации метки времени
# в UTC. Используется при создании тикетов и журналировании событий.
def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# Список допустимых состояний тикета.
# Enum позволяет хранить состояние в виде строки и удобно сравнивать его.
class TicketStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


# Пользователь системы: сотрудник, клиент или администратор.
@dataclass
class User:
    id: str
    full_name: str
    role: str


# Категория тикета нужна для группировки обращений по типу проблемы.
@dataclass
class TicketCategory:
    id: str
    name: str


# Комментарий к тикету хранит автора, текст и время создания.
@dataclass
class TicketComment:
    id: str
    author_id: str
    text: str
    created_at: str = field(default_factory=now)


# История смены статуса позволяет понять, кто и когда перевёл тикет.
@dataclass
class TicketStatusChange:
    id: str
    user_id: str
    previous_status: str
    new_status: str
    changed_at: str = field(default_factory=now)


# Основная сущность системы: обращение пользователя в службу поддержки.
# Внутри тикета хранятся комментарии, история статусов и данные назначенного ответственного.
@dataclass
class Ticket:
    id: str
    creator_id: str
    category_id: str
    title: str
    description: str

    status: TicketStatus = TicketStatus.NEW
    assignee_id: str | None = None
    created_at: str = field(default_factory=now)
    closed_at: str | None = None

    comments: list[TicketComment] = field(default_factory=list)
    changes: list[TicketStatusChange] = field(default_factory=list)

    # Назначение ответственного сотрудника для обработки обращения.
    def assign_to(self, user_id: str):
        self.assignee_id = user_id

    # Добавление комментария сохраняет связь между тикетом и его автором.
    def add_comment(self, author_id: str, text: str):
        self.comments.append(
            TicketComment(str(uuid4()), author_id, text)
        )

    # Перевод тикета в новый статус с фиксацией предыдущего значения.
    # Если статус стал CLOSED, фиксируется момент закрытия обращения.
    def change_status(self, new_status: TicketStatus, user_id: str):
        new_status = TicketStatus(new_status)
        previous = self.status
        self.status = new_status

        self.changes.append(
            TicketStatusChange(
                str(uuid4()),
                user_id,
                previous.value,
                new_status.value
            )
        )

        self.closed_at = (
            now() if new_status == TicketStatus.CLOSED else None
        )

    # Конвертация словаря из JSON в объект Ticket.
    # Важно привести строковый статус к Enum и восстановить вложенные модели.
    @classmethod
    def from_dict(cls, data: dict):
        data = dict(data)
        data["status"] = TicketStatus(data["status"])

        data["comments"] = [
            TicketComment(**item)
            for item in data.get("comments", [])
        ]

        data["changes"] = [
            TicketStatusChange(**item)
            for item in data.get("changes", [])
        ]

        return cls(**data)