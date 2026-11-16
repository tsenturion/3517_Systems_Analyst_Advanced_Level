# Информационная модель HelpDesk

## Предметная область

Система предназначена для регистрации
и обработки заявок технической поддержки.

## Основные сущности

### User

Пользователь системы. Может выступать сотрудником,
специалистом поддержки или руководителем.

### Ticket

Заявка на техническую поддержку.
Содержит описание проблемы и сведения
о текущем состоянии обработки.

### TicketComment

Комментарий к заявке.
Используется для фиксации сообщений,
связанных с обработкой обращения.

## Исходное проектное правило

В соответствии с DEC-001 заявка может
существовать без назначенного исполнителя.

## Структура классов

```mermaid
classDiagram
    class User {
        +UUID id
        +String fullName
        +String role
    }

    class Ticket {
        +UUID id
        +String title
        +String description
        +String status
        +DateTime createdAt
    }

    class TicketComment {
        +UUID id
        +String text
        +DateTime createdAt
    }

    User "1" -- "0..*" Ticket : creates
    User "0..1" -- "0..*" Ticket : handles
    Ticket "1" -- "0..*" TicketComment : contains
    User "1" -- "0..*" TicketComment : writes
```
