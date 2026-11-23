CREATE OR REPLACE PROCEDURE public.sa52_count_tickets(
    IN p_status TEXT,
    INOUT p_total BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT COUNT(*)
    INTO p_total
    FROM public.tickets
    WHERE p_status IS NULL
       OR status::text = p_status;
END;
$$;