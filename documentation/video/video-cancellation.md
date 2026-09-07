# Video cancellation

Queued jobs are cancelled immediately. Processing jobs use `cancel_requested` and stop between sampled frames. Temporary frames are removed and the usage reservation is released. Celery revocation never forcibly terminates a running inference process.
