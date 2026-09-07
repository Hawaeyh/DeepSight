# Worker setup

After Redis and PostgreSQL are ready, run `.\scripts\start-worker.ps1`, or launch web and worker together with `python run_web.py --with-worker`. Windows uses Celery's solo pool. Docker users can run `docker compose up --build redis backend worker frontend`.
