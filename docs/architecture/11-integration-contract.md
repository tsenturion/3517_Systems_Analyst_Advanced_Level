# Интеграционный контракт HelpDesk

## Событие создания заявки

Название: ticket.created
Версия: 1

```json
{
  "event_id": "evt-001",
  "event_type": "ticket.created",
  "version": 1,
  "occurred_at": "2026-11-18T12:00:00+00:00",
  "data": {
    "ticket_id": "ticket-001",
    "title": "Не работает принтер"
  }
}
```

## Участники взаимодействия

Источник: приложение HelpDesk.

Получатель: обработчик уведомлений.

Транспорт: RabbitMQ.

Очередь: helpdesk.notifications.

Формат: JSON в кодировке UTF-8.

## Последовательность взаимодействия

```mermaid
sequenceDiagram
    participant Client as Клиент
    participant API as HelpDesk API
    participant Storage as Хранилище
    participant Broker as RabbitMQ
    participant Worker as Обработчик

    Client->>API: Создать заявку
    API->>Storage: Сохранить заявку
    Storage-->>API: Подтверждение
    API->>Broker: ticket.created
    Broker-->>API: Подтверждение публикации
    API-->>Client: HTTP 201

    Broker->>Worker: Доставить событие
    Worker->>Worker: Обработать уведомление
    Worker-->>Broker: Подтверждение обработки
```
