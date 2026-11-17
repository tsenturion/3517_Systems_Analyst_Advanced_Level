# Архитектура приложения HelpDesk

## Архитектурный подход

Модульный монолит с разделением ответственности
по архитектурным слоям.

## Основные компоненты

- HTTP-интерфейс — приём запросов и выдача ответов.
- Прикладной слой — выполнение сценариев приложения.
- Предметная модель — объекты и правила их поведения.
- Инфраструктура — хранение данных и внешние интеграции.

## Схема компонентов

```mermaid
flowchart TD
    Client["Клиентское приложение"]

    subgraph Monolith["HelpDesk — модульный монолит"]
        API["HTTP-интерфейс"]
        Application["Прикладной слой"]
        Domain["Предметная модель"]

        API --> Application
        Application --> Domain
    end

    subgraph Infrastructure["Инфраструктурные адаптеры"]
        Repository["Адаптер хранения"]
        Publisher["Адаптер событий"]
    end

    Storage[("JSON-хранилище")]
    Broker["RabbitMQ"]

    Application -.->|"Контракт хранения"| Repository
    Application -.->|"Контракт публикации"| Publisher

    Repository --> Storage
    Publisher --> Broker

    Client --> API
```
