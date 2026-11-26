SELECT
    id,
    title,
    status,
    created_at

FROM helpdesk_perf.tickets

WHERE status = 'NEW'

ORDER BY created_at DESC, id DESC

LIMIT 20;