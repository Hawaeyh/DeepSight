# Analysis ownership

Authenticated analyses store `owner_user_id`; guest analyses store `guest_session_id`. The database check constraint prevents both from being populated. Ownership is derived only from a verified JWT or server guest cookie and is never accepted from request bodies, query parameters, `X-Guest-ID`, React state, or extension payloads.

Normal history, dashboard, detail, verification, deletion, feedback, report, and media operations query by both analysis ID and trusted owner. A cross-user or legacy-unowned lookup returns 404 to avoid confirming that the record exists.

Canonical routes include `GET /api/v1/me/analyses`, `GET/DELETE /api/v1/analyses/{id}`, and owner-restricted feedback/report routes. Older `/history`, `/analysis/{id}`, `/reports/{id}`, and `/feedback` routes remain temporarily for frontend compatibility but enforce the same ownership rules.

Administrators do not automatically bypass media ownership on normal user routes. Aggregate admin endpoints require the database-backed admin role.
