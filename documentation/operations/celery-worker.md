# Celery worker

Run `.\scripts\start-worker.ps1` after Redis. Windows uses `--pool=solo`. Models load lazily and remain cached per worker. Worker tasks use soft and hard limits, persist safe failure codes, release usage reservations, and create completion/failure notifications.
