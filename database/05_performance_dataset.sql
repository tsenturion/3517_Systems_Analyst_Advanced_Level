BEGIN;

CREATE SCHEMA IF NOT EXISTS helpdesk_perf;

CREATE TABLE IF NOT EXISTS helpdesk_perf.tickets (
    id BIGINT PRIMARY KEY,

    creator_id TEXT NOT NULL,
    category_id TEXT NOT NULL,

    title TEXT NOT NULL,
    description TEXT NOT NULL,

    status TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL
);

-- Очищаем только специальную тестовую таблицу

TRUNCATE TABLE helpdesk_perf.tickets;

-- Удаляем индексы предыдущего эксперимента

DROP INDEX IF EXISTS helpdesk_perf.idx_tickets_status_created;

-- Генерируем 100 000 заявок

INSERT INTO helpdesk_perf.tickets (
    id,
    creator_id,
    category_id,
    title,
    description,
    status,
    created_at
)

SELECT
    n,

    'user-' || (n % 1000 + 1),

    CASE n % 3
        WHEN 0 THEN 'hardware'
        WHEN 1 THEN 'software'
        ELSE 'network'
    END,

    'Заявка №' || n,

    REPEAT('Описание технической проблемы. ', 10),

    CASE
        WHEN n % 10 = 0 THEN 'NEW'
        WHEN n % 10 < 3 THEN 'IN_PROGRESS'
        WHEN n % 10 < 5 THEN 'RESOLVED'
        ELSE 'CLOSED'
    END,

    TIMESTAMPTZ '2026-01-01 00:00:00+00'
        + n * INTERVAL '1 minute'

FROM generate_series(1, 100000) AS series(n);

ANALYZE helpdesk_perf.tickets;

COMMIT;