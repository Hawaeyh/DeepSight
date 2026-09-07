# Guest sessions

`POST /api/v1/guest/session` generates a cryptographically random token, stores only an HMAC-SHA256 hash, and sets the raw token in an HttpOnly SameSite=Lax cookie. Cookies become Secure in staging and production and expire after the configured duration. IP and user-agent values are stored only as keyed hashes.

Guest ownership uses the verified database session ID. Browser-generated `X-Guest-ID` values are ignored. Invalid, expired, or transferred sessions receive 401; one guest cannot retrieve another guest's results.

`POST /api/v1/guest/transfer` requires both a verified user JWT and verified guest cookie. It transfers only that session's analyses in one transaction, clears guest ownership, records the recipient/time, prevents session reuse, and deletes the browser cookie.

Automated expired-session/media cleanup is not part of this phase and remains required before production.
