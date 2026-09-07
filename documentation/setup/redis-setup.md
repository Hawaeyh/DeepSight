# Redis setup

Run `.\scripts\start-redis.ps1`; it starts the Compose Redis service and waits for `PONG` on `127.0.0.1:6379`. Defaults use database 0 for Celery transport and database 1 for results. Override `REDIS_URL`, `CELERY_BROKER_URL`, and `CELERY_RESULT_BACKEND` for another trusted instance.
