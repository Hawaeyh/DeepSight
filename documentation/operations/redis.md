# Redis

Redis carries Celery jobs and production rate-limit counters. Start local Redis with `.\scripts\start-redis.ps1`. When Redis is absent in development, video jobs may use the explicitly labelled single-worker background executor. Staging and production do not silently use that fallback.
