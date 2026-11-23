CREATE TEMP TABLE sa52_work_tickets AS
SELECT
    id::text AS ticket_id,
    status::text AS status
FROM public.tickets
ORDER BY created_at DESC
LIMIT 20;


CREATE OR REPLACE PROCEDURE public.sa52_change_status(
    IN p_ticket_id TEXT,
    IN p_new_status TEXT,
    INOUT p_changed INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_new_status IS NULL
       OR p_new_status NOT IN (
           'NEW',
           'IN_PROGRESS',
           'RESOLVED',
           'CLOSED'
       ) THEN

        RAISE EXCEPTION 'Недопустимый статус: %', p_new_status
            USING ERRCODE = '22023';
    END IF;

    UPDATE pg_temp.sa52_work_tickets
    SET status = p_new_status
    WHERE ticket_id = p_ticket_id
      AND status IS DISTINCT FROM p_new_status;

    GET DIAGNOSTICS p_changed = ROW_COUNT;
END;
$$;