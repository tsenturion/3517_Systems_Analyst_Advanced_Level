BEGIN;

CALL public.sa52_change_status(
    (
        SELECT ticket_id
        FROM pg_temp.sa52_work_tickets
        ORDER BY ticket_id
        LIMIT 1
    ),
    (
        SELECT CASE
            WHEN status = 'CLOSED'
                THEN 'NEW'
            ELSE 'CLOSED'
        END
        FROM pg_temp.sa52_work_tickets
        ORDER BY ticket_id
        LIMIT 1
    ),
    NULL::INTEGER
);

SELECT *
FROM pg_temp.sa52_work_tickets
ORDER BY ticket_id
LIMIT 5;

ROLLBACK;

SELECT *
FROM pg_temp.sa52_work_tickets
ORDER BY ticket_id
LIMIT 5;