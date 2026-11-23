DO $$
DECLARE
    v_created BIGINT;
    v_closed BIGINT;
    v_avg NUMERIC;
BEGIN
    CALL public.sa52_period_metrics(
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP - INTERVAL '1 day',
        v_created,
        v_closed,
        v_avg
    );

EXCEPTION
    WHEN SQLSTATE '22023' THEN
        RAISE NOTICE
            'Проверка сработала: %',
            SQLERRM;
END;
$$;