# Audit logs

Sensitive administrator mutations and Stripe checkout creation write structured audit events containing actor, action, target, outcome, and non-secret details. `/admin/audit-events` is administrator-only. Tokens, passwords, private URLs, and raw media must never be placed in event details.
