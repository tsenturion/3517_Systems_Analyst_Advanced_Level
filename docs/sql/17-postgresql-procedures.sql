CREATE OR REPLACE PROCEDURE public.sa52_period_metrics(
    IN p_from TIMESTAMPTZ,
    IN p_to TIMESTAMPTZ,
    INOUT p_created BIGINT,
    INOUT p_closed BIGINT,
    INOUT p_avg_resolution_hours NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_from IS NULL
       OR p_to IS NULL
       OR p_from >= p_to THEN

        RAISE EXCEPTION 'Некорректный период'
            USING ERRCODE = '22023';
    END IF;

    SELECT
        COUNT(*),

        COUNT(*) FILTER (
            WHERE t.status::text = 'CLOSED'
        ),

        ROUND(
            (
                AVG(
                    EXTRACT(
                        EPOCH FROM (
                            t.closed_at::timestamptz
                            - t.created_at::timestamptz
                        )
                    ) / 3600.0
                ) FILTER (
                    WHERE t.status::text = 'CLOSED'
                      AND t.closed_at IS NOT NULL
                )
            )::NUMERIC,
            2
        )

    INTO
        p_created,
        p_closed,
        p_avg_resolution_hours

    FROM public.tickets t
    WHERE t.created_at::timestamptz >= p_from
      AND t.created_at::timestamptz < p_to;
END;
$$;