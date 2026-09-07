# Video jobs

Create jobs with `POST /api/v1/videos`; poll `/videos/{id}/status` and fetch `frames`, `tracks`, or `segments`. Cancellation is cooperative between frames. Deletion is owner scoped and allowed only after completion, failure, or cancellation. Limits default to 100 MB, 120 seconds, 3840x2160, and 5-120 FPS.
