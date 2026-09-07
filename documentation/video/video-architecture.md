# Video architecture

Upload validation and job creation happen in FastAPI. Redis transports the durable Celery task; the worker samples frames, runs the approved image model, tracks faces, aggregates evidence, and commits frames, tracks, segments, progress, and the owned analysis. Raw paths never appear in API responses.
