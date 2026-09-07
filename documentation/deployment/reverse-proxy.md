# Reverse proxy

Terminate HTTPS at a maintained reverse proxy, serve the built frontend, proxy `/api/` to FastAPI, preserve request IDs, set an upload limit matching DeepSight configuration, cache only fingerprinted public assets, and never map upload/report directories publicly. No WebSocket route is currently required.
