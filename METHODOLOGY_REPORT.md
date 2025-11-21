
# Festive Connect Agent — Code-Driven Methodology Report

Last updated: 2025-11-20

This document is a factual, code-first walkthrough of the Festive Connect Agent repository. It maps architecture, runtime commands, implementation decisions, and extension points directly to the source files so a developer (or AI) can be productive immediately.

Executive summary
- Purpose: a small FastAPI + static frontend app with an LLM-driven agent (Google ADK) that exposes event CRUD, analytics, auditing, and organizer management.
- Key runtime: backend is a Uvicorn/FastAPI app started from `backend/main.py`; the agent is registered and discovered using `google.adk.cli.fast_api.get_fast_api_app(...)`.

Repository layout (important files)
- `backend/constants.py` — central config (DB filename, agent name, model).
- `backend/main.py` — application entry, ADK integration, router registration, uvicorn runner.
- `backend/agent/agent.py` — registers `LlmAgent` and tool list.
- `backend/agent/prompt.py` — agent instruction prompt and expected reply formats.
- `backend/agent/tools.py` — async tools callable by the agent; convert domain objects to dicts and delegate to services.
- `backend/models/data_models.py` — Pydantic models: `Event`, `Organizer`.
- `backend/repos/repo.py` — primary data access for events (aiosqlite), migration helpers, normalization helpers.
- `backend/repos/organizer_repo.py` — organizers repo with analytics SQL queries.
- `backend/services/service.py` — event business logic, analytics & auditing helpers.
- `backend/services/organizer_service.py` — organizer business logic.
- `backend/routers/events.py` and `backend/routers/organizers.py` — HTTP endpoints mapped to service methods.
- `frontend/` — static UI: `index.html`, `pages/chat.html`, `scripts/main.js`, `services/apiService.js`.
- `backend/requirements.txt` and `backend/Dockerfile` — dependencies and container runtime.

How to run (developer-first)
1) Local dev (recommended)
  - Create venv, activate and install:
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r backend/requirements.txt
    ```
  - Set API key env:
    ```powershell
    $env:GOOGLE_API_KEY = "YOUR_KEY"
    ```
  - (optional) update `frontend/services/apiService.js` `API_CONFIG.baseURL` to `http://localhost:8080` for the browser frontend.
  - Run backend:
    ```powershell
    python backend/main.py
    ```
  - Serve frontend (static) or use VS Code Live Server:
    ```powershell
    Push-Location frontend
    python -m http.server 5500
    Pop-Location
    ```

2) Docker
  - Build and run (from repo root):
    ```powershell
    docker build -t festive-backend .\backend
    docker run -p 8080:8080 -e GOOGLE_API_KEY="YOUR_KEY" festive-backend
    ```
  - To persist DB, mount a volume for `festiveconnect.db`.

Top-to-bottom code walkthrough (files ordered by flow)

1. `backend/constants.py`
  - Small file that defines `AGENT_NAME`, `AGENT_DESCRIPTION`, `AGENT_MODEL` (default `gemini-2.0-flash`), `DB_NAME='festiveconnect.db'`, `TABLE_NAME='events'`, `ORGANIZER_TABLE_NAME='organizers'`.
  - Single source of truth for these values — change here to affect the app globally.

2. `backend/main.py`
  - Constructs `Repo(DB_NAME)` and `Service(repo)` for warm wiring (the repo/service are used by tools).
  - Determines `AGENT_DIR = os.path.dirname(__file__)` and calls `get_fast_api_app(agents_dir=AGENT_DIR, allow_origins=ALLOWED_ORIGINS, web=SERVE_WEB_INTERFACE)` from `google.adk.cli.fast_api`.
  - Registers FastAPI routers: `app.include_router(events.router, prefix='/events')`, `app.include_router(organizers.router, prefix='/organizers')`.
  - When run as script, launches `uvicorn` on `0.0.0.0:PORT` (default 8080).

3. `backend/agent/agent.py`
  - Imports tools and the `ROOT_AGENT_PROMPT` then creates `root_agent = LlmAgent(...)` passing `tools=[...]` and `instruction=ROOT_AGENT_PROMPT`.
  - The ADK runtime discovers this agent because `get_fast_api_app` looks in `agents_dir`.

4. `backend/agent/prompt.py`
  - Contains `ROOT_AGENT_PROMPT` string: role, tool overview, examples of outputs, and strict formatting guidance.
  - Useful to consult when adding or modifying tools — the agent's replies are expected to match the examples.

5. `backend/agent/tools.py`
  - Contains asynchronous functions that the agent can call. Each tool:
    - Accepts plain arguments (primitives or dicts),
    - Delegates to `service` or `organizer_service`,
    - Normalizes return types into dictionaries or lists via `_event_to_dict()` and `_organizer_to_dict()`.
  - Tools implement tolerant matching (e.g., `events_by_month` accepts textual or numeric months and does substring matching on date strings).
  - Error handling: tools raise `ValueError` or `LookupError` for invalid input — ADK will surface errors to the agent flow.

6. `backend/models/data_models.py`
  - `Event` model: fields `id`, `title`, `date`, `location`, `performers`, `description`, `created_at`, `updated_at`.
  - `Organizer` model: fields `organizer_id`, `name`, `company`, `region`, `experience`, `managed_events`, `cultural_events`, `events_2025`.
  - Pydantic models are used for request validation in routers and for constructing domain objects.

7. `backend/repos/repo.py` (events repo)
  - Connects to SQLite using `aiosqlite`.
  - `init_db()` creates `events` table if missing and calls `_ensure_column()` to support migrations for `created_at`/`updated_at`.
  - `_normalize_event()` converts `Event` or dicts to normalized dict and ensures `performers` is a list.
  - Stores performers in DB as a comma-separated string; converts back to list when reading.
  - Basic CRUD: `insert`, `list`, `get`, `update`, `delete`.

8. `backend/repos/organizer_repo.py` (organizer repo)
  - Similar pattern: `init_db()` creates `organizers` table.
  - Includes SQL aggregation queries used by organizer analytics: `events_managed_by_company`, `region_with_max_cultural_events`, `top_organizer_2025`.

9. `backend/services/service.py` (events service)
  - Wraps repo calls and implements business rules:
    - `create_event` sets `id` (uuid4) and timestamps, prevents duplicate IDs.
    - `get_all_events`, `get_event`, `update_event`, `delete_event` map to repo and raise `HTTPException` when appropriate.
  - Analytics & auditing functions:
    - `get_total_events()` uses repo.list();
    - `get_events_this_month()` parses date strings using `_parse_datetime()` tolerant to ISO and basic formats;
    - `get_city_with_most_events()` and `get_top_performer()` aggregate using Python `Counter`;
    - `get_most_recent_event()` finds event with latest parsed timestamp (tries `created_at`, `date`);
    - `get_recent_events_15_days()` and `get_location_with_most_past_events()` implement time-window filtering and comparisons.
  - Parsing helpers provide graceful fallbacks for malformed date strings.

10. `backend/services/organizer_service.py`
  - Uses `OrganizerRepo` and exposes organizer CRUD and analytics; explicit `init_db()` call before repo operations.
  - Validates uniqueness of `organizer_id` at creation; raises `HTTPException` on conflicts or not-found cases.

11. `backend/routers/events.py` and `backend/routers/organizers.py`
  - Thin HTTP layer: FastAPI routers call service methods and declare response models.
  - Analytics endpoints are exposed under `/events/analytics/*` and auditing under `/events/audit/*`. Organizer analytics are under `/organizers/analytics/*`.

12. `frontend/services/apiService.js`
  - Exports `API_CONFIG` with `baseURL` and helper `ApiService` class for `get`, `post`, `put`, `patch`, `delete`, and `postWithStream`.
  - `postWithStream` expects newline-delimited chunks and uses `chunk.slice(6)` to strip a `data: ` prefix — backend agent streams must emit `data: <json>\n` lines to match this parsing.

13. `frontend/scripts/main.js`
  - Fetches events, renders UI, handles add/edit/delete via `ApiService`.
  - Uses standard DOM-based patterns and simple client-side validation.

Implementation patterns and conventions (practical notes)
- Layering: `routers -> services -> repos`. Services always call `repo.init_db()` before DB ops to ensure schema exists.
- Date fields are strings and parsing is tolerant. Prefer adding normalized date formats if introducing complex date features.
- Repos store performers as a CSV string; services/tools convert to/from lists. Keep this behavior in mind when changing storage.
- Agent tools must return plain Python dicts/lists (see `tools.py` helpers). Tools should raise exceptions for invalid input rather than returning error dicts — the ADK runtime expects exceptions to propagate.
- Streaming format: frontend expects lines prefixed by `data: ` and newline separated. When adding streaming responses, follow this format.

Database & migration notes
- `Repo.init_db()` and `OrganizerRepo.init_db()` create tables if missing. `_ensure_column()` in `repo.py` is used to add `created_at`/`updated_at` if absent.
- The repository uses `aiosqlite` and stores the DB file `festiveconnect.db` in the backend working directory.

Testing & verification
- Manual smoke checks:
  - Start backend and visit `http://localhost:8080/docs` (FastAPI OpenAPI).
  - `GET /events/` should return a list (empty initially).
  - Use UI at `frontend/index.html` (serve statically) and navigate to `pages/chat.html` to test agent streaming.
- Unit/integration tests are not included in repo; create lightweight tests that call Service methods and repos using an in-memory or ephemeral SQLite file.

Deployment notes
- Dockerfile uses `python:3.13-slim`, copies the backend into the container and runs `uvicorn main:app --host 0.0.0.0 --port 8080`.
- The ADK requires network access and the `GOOGLE_API_KEY` env var; pass it to the container with `-e GOOGLE_API_KEY="..."`.

Troubleshooting (common issues & fixes)
- `Unexpected token ':'` in PowerShell: caused by trying to run a browser JS file in PowerShell — the frontend JS is meant to run in the browser, not in the shell.
- Streaming parse errors in frontend: ensure server emits `data: <json>\n` lines; the client strips first 6 chars before JSON parse.
- DB permission errors: ensure `festiveconnect.db` can be created/written by the process or mount a volume for persistence in Docker.
- Missing package errors: activate venv and run `pip install -r backend/requirements.txt`.

Extension & contribution guide (how to add features cleanly)
1. New data model: add Pydantic model in `backend/models/data_models.py`.
2. Repo layer: add new repo with `init_db()` (use `aiosqlite` and follow `organizer_repo.py` style). Always implement `init_db()` + migration helper if adding columns.
3. Service layer: add business logic and defensive parsing/helpers in `backend/services/`.
4. Router: add a thin FastAPI router in `backend/routers/` that delegates to service and uses response_model.
5. Agent tool (if agent integration desired): add an async tool in `backend/agent/tools.py` and register it in `backend/agent/agent.py`, and update `backend/agent/prompt.py` if you need new agent instructions/format.

Appendix: Quick checklist before PR
- Run backend and confirm OpenAPI at `/docs`.
- Add unit tests for new service methods and repo migrations.
- If adding streaming output, confirm `data: ` prefix lines for frontend compatibility.
- Update `backend/constants.py` if changing agent model or DB filename.

If you want, I will:
- generate a `run-dev.ps1` script to automate venv creation, install, env load and backend start, and
- add a `docker-compose.yml` to run backend + static frontend with volume-backed DB.

End of report.

