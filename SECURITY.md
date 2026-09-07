# DeepSight security

Report vulnerabilities privately to the repository owner. Do not include credentials, JWTs, service-account files, private media, or payment data in issues.

DeepSight derives roles and ownership from the database. Media and reports are served through authenticated endpoints. Guest identity uses an HTTP-only signed token. Uploads are decoded and signature checked before inference. Stripe plans change only after verified webhooks; Firebase roles are never trusted from token claims.

Production requires a 32+ character non-development secret, explicit CORS and trusted-host allowlists, HTTPS, PostgreSQL, Redis-backed rate limiting, external secret management, storage backups, and a deployment security review. Local development is not an internet-facing configuration.
