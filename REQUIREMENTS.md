# Festive Connect Agent — Requirements

This file captures concise, code-driven functional and non-functional requirements derived from the repository source.

## Functional requirements

- **Event CRUD API:** Create, read, update, delete events via REST endpoints defined in `backend/routers/events.py`. Service implementations live in `backend/services/service.py` and persistence in `backend/repos/repo.py`.
- **Event data validation:** Incoming event payloads must validate against the Pydantic `Event` model in `backend/models/data_models.py` (fields: `id`, `title`, `date`, `location`, `performers`, `description`, `created_at`, `updated_at`).
- **Organizer CRUD & analytics:** Create/list/get/update/delete organizers and expose analytics endpoints (`/organizers/analytics/*`) implemented by `backend/routers/organizers.py`, `backend/services/organizer_service.py`, and `backend/repos/organizer_repo.py`.
- **Agent tools:** Async tools in `backend/agent/tools.py` callable by the ADK agent. Tools must return JSON-serializable dicts/lists (see `_event_to_dict()` and `_organizer_to_dict()`).
- **Agent registration & prompt:** Agent is registered in `backend/agent/agent.py` and instructed by `backend/agent/prompt.py`; tools must align with the prompt's expected output formats.
- **Analytics & auditing endpoints:** Provide totals, this-month events, top city/performer, most recent event, recent events (last N days), and top historical locations (`backend/services/service.py` + routers).
- **DB initialization & migration:** `init_db()` in repos creates tables and `_ensure_column()` migrates `created_at`/`updated_at` when needed (file: `backend/repos/repo.py`).
- **Frontend API client:** `frontend/services/apiService.js` must be configured with `API_CONFIG.baseURL` pointing to the backend. Streaming client `postWithStream` expects newline-delimited `data: <json>\n` frames.
- **Timestamps & IDs:** `create_event` sets `id` (uuid4) and timestamps (`created_at`, `updated_at`) in ISO format (service layer behavior: `backend/services/service.py`).

## Non-functional requirements

- **Runtime:** Python 3.11+ locally; Dockerfile uses Python 3.13 (`backend/Dockerfile`). All backend dependencies listed in `backend/requirements.txt` (notably `google-adk`, `fastapi`, `uvicorn`, `aiosqlite`).
- **Port & host:** Backend listens on `0.0.0.0:8080` by default; `PORT` env var can override (see `backend/main.py`).
- **Configuration & secrets:** `GOOGLE_API_KEY` must be provided as an environment variable for ADK access.
- **Performance / scale:** SQLite + in-memory analytics are acceptable for small datasets; for larger scale, migrate to a server DB and add indexes or caching.
- **Security:** No auth in current code — production must add authentication, tighten CORS (remove `"*"`), and secure API keys.
- **Compatibility:** Frontend requires modern browsers supporting ES modules and ReadableStream APIs (used by `postWithStream`).
- **Observability:** FastAPI OpenAPI UI available at `/docs`; add logging/metrics for production readiness.

## Acceptance criteria (quick checks)

- Backend starts and exposes OpenAPI at `http://localhost:8080/docs` when `GOOGLE_API_KEY` is set.
- `GET /events/` returns 200 and a JSON array (empty or event objects).
- `POST /events/` with valid payload returns 201 and event contains `id`, `created_at`, `updated_at`.
- Agent tools return JSON-serializable dicts and analytics outputs conform to formats described in `backend/agent/prompt.py`.
- Frontend chat streaming receives newline-delimited `data: <json>\n` chunks without parse errors.
- Organizer endpoints under `/organizers` respond per route definitions and analytics endpoints return expected JSON shapes.

## Notes and pointers

- When adding features follow the layering pattern: `router -> service -> repo` and register agent tools in `backend/agent/tools.py` + `backend/agent/agent.py`.
- When returning streamed agent output, ensure server emits `data: <json>\n` framed lines so `frontend/services/apiService.js::postWithStream` can parse them.
- Persist `festiveconnect.db` with correct file permissions or mount a volume when running in Docker.

If you want, I can convert these acceptance criteria into a runnable Python test script or add `run-dev.ps1` automation. Reply which you'd prefer.

*** End Patch