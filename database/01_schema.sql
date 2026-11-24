BEGIN;

CREATE SCHEMA IF NOT EXISTS helpdesk;

SET search_path TO helpdesk;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    full_name TEXT,
    role TEXT CHECK (
        role IN ('employee', 'support', 'manager')
    )
);

CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,

    creator_id TEXT NOT NULL REFERENCES users(id),
    assignee_id TEXT REFERENCES users(id),
    category_id TEXT NOT NULL REFERENCES categories(id),

    title TEXT NOT NULL,
    description TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'NEW' CHECK (
        status IN (
            'NEW',
            'IN_PROGRESS',
            'RESOLVED',
            'CLOSED'
        )
    ),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,

    CHECK (
        closed_at IS NULL
        OR closed_at >= created_at
    )
);

CREATE TABLE IF NOT EXISTS ticket_comments (
    id TEXT PRIMARY KEY,

    ticket_id TEXT NOT NULL REFERENCES tickets(id),
    author_id TEXT NOT NULL REFERENCES users(id),

    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    position INTEGER NOT NULL CHECK (position > 0),

    UNIQUE (ticket_id, position)
);

CREATE TABLE IF NOT EXISTS ticket_status_changes (
    id TEXT PRIMARY KEY,

    ticket_id TEXT NOT NULL REFERENCES tickets(id),
    user_id TEXT NOT NULL REFERENCES users(id),

    previous_status TEXT NOT NULL CHECK (
        previous_status IN (
            'NEW', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'
        )
    ),

    new_status TEXT NOT NULL CHECK (
        new_status IN (
            'NEW', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'
        )
    ),

    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    position INTEGER NOT NULL CHECK (position > 0),

    UNIQUE (ticket_id, position)
);

COMMIT;