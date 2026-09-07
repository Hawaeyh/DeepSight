# Docker deployment

Compose supplies PostgreSQL, Redis, backend, worker, and frontend with readiness checks and named database/storage/report volumes. Models are mounted read-only. Compose uses development defaults; supply environment-managed secrets and remove source bind mounts for staging or production.
