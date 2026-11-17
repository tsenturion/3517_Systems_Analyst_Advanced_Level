import json
from dataclasses import asdict

from .core import (
    HelpDesk,
    TicketCategory,
    TicketStatus,
    User
)


anna = User("user-anna", "Анна", "employee")
oleg = User("user-oleg", "Олег", "support")

category = TicketCategory("hardware", "Оборудование")

system = HelpDesk()

ticket = system.create(
    "Не включается ноутбук",
    "Экран остаётся чёрным",
    anna.id,
    category.id
)

ticket.assign_to(oleg.id)

ticket.add_comment(
    oleg.id,
    "Проверяю питание"
)

ticket.change_status(
    TicketStatus.IN_PROGRESS,
    oleg.id
)

system.save()

print(
    json.dumps(
        asdict(ticket),
        ensure_ascii=False,
        indent=2
    )
)