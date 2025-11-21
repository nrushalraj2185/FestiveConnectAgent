## Quick context

- This repo implements a Festive Connect web app with a FastAPI backend and a small static frontend. The backend exposes REST endpoints and an LLM-based agent (via google.adk) that calls server-side "tools" for CRUD and analytics.

## Big-picture architecture (what to know first)

- Entry: `backend/main.py` — creates the FastAPI app using `google.adk.cli.fast_api.get_fast_api_app(...)`, includes routers `/events` and `/organizers`, and runs Uvicorn on port 8080 by default.
- Agents: `backend/agent/agent.py`, `backend/agent/prompt.py`, `backend/agent/tools.py` — an `LlmAgent` (name from `backend/constants.py`) is registered with an instruction prompt and a list of async tools. Tools are the bridge between conversational intents and backend logic.
- HTTP API: `backend/routers/events.py` and `backend/routers/organizers.py` — thin layer that calls into `services/`.
- Business logic: `backend/services/*.py` (e.g., `service.py`, `organizer_service.py`) — orchestrates repo calls, raises FastAPI `HTTPException` on errors.
- Persistence: `backend/repos/*` (e.g., `repo.py`, `organizer_repo.py`) — uses `aiosqlite` and the DB name in `backend/constants.py` (`festiveconnect.db`). Repo classes call `init_db()` lazily in service methods.
- Data schemas: `backend/models/data_models.py` — Pydantic models (Event, Organizer) used across routers, services, and tools.
- Frontend: static HTML/JS under `frontend/` — `frontend/services/apiService.js` contains `API_CONFIG.baseURL` and a streaming helper `postWithStream` which expects newline-delimited JSON chunks (SSE-like). Update `baseURL` before running locally.

## Developer workflows & commands (project-specific)

- Install dependencies (from repo root):
  - Backend: `pip install -r backend/requirements.txt`
  - The README (root) also mentions creating a Google AI Studio API key and setting `GOOGLE_API_KEY` in your `.env`.
- Run backend locally (from repo root):
  - `python backend/main.py` (main calls `uvicorn.run(...)` on port `8080` by default). The `PORT` env var can override it.
- Dev notes: `main.py` sets `ALLOW_ORIGINS = ["*"]` and `SERVE_WEB_INTERFACE = True` — these are convenient defaults for development but should be tightened for production.
- Database: the SQLite file `festiveconnect.db` is created next to the backend when repos call `init_db()`; clearing that file will reset DB state.

## Project-specific patterns & conventions (do not break these)

- Agent tools are async functions that return structured Python dicts / lists (see `backend/agent/tools.py`). Tools raise exceptions for invalid input — callers assume exceptions propagate and are converted into agent or HTTP errors.
- Prompt guidance lives in `backend/agent/prompt.py` and contains concrete formatting examples (e.g., how lists and analytics sentences should look). Agents should follow this formatting — the prompt and tools are co-designed.
- Data flow: routers -> services -> repos. Services call `repo.init_db()` before DB operations to ensure schema exists. Prefer using service methods rather than calling repos directly from new endpoints.
- Date handling: the code treats dates as strings and uses substring matching for months (see `events_by_month` in `tools.py`). Keep that tolerant approach when adding new search/filter logic.
- Streaming responses from the agent/API assume newline-delimited JSON chunks; `frontend/services/apiService.js` strips a 6-character prefix before parsing (`chunk.slice(6)`), so the backend streaming format must match (e.g., `data: {...}\n`).

## Integration & external dependencies to pay attention to

- google.adk (agent runtime) — agents are discovered by `get_fast_api_app(agents_dir=...)`. If you add new agents, place them under `backend/agent` or ensure the `agents_dir` discovery path includes them.
- Model configured in `backend/constants.py` (AGENT_MODEL = `gemini-2.0-flash`). Update here to change the LLM target.
- SQLite via `aiosqlite` — repo implementations rely on SQL DDL strings in repo classes (see `organizer_repo.py`). Keep migrations simple (create-if-not-exists pattern used).

## Concrete examples to reference while coding

- Register tools for the agent (example): `backend/agent/agent.py` — tools list passed to `LlmAgent(...)`.
- Prompt examples & tone: `backend/agent/prompt.py` shows exact reply formats to keep conversational outputs consistent.
- Event model: `backend/models/data_models.py` — fields expected by routers/services/tools.
- Organizer analytics: `backend/repos/organizer_repo.py` and `backend/services/organizer_service.py` — show how analytics endpoints are implemented and exposed under `/organizers/analytics/*`.

## Quick troubleshooting tips

- 500 on DB calls: check `festiveconnect.db` exists and is writable; services call `init_db()` but file permissions can break creation.
- Agent discovery fails: ensure `agents_dir` passed to `get_fast_api_app` (in `backend/main.py`) points to the directory containing `agent.py`.
- Streaming parse errors in frontend: verify backend sends newline-separated `data: <json>` lines; the frontend parser expects that format.

## What I did / what I expect from you

- This file was created from repository inspection (no pre-existing `.github/copilot-instructions.md` found). I focused on discoverable, actionable patterns and commands — not aspirational advice.
- If there are additional developer steps (CI, tests, environment variables, or prod deployment notes) that are not in-code or README, tell me and I'll merge them into this file.

---
If any part of the architecture above is incomplete or you want examples extended (e.g., sample HTTP request/responses, or a short checklist for adding a new tool/agent), reply and I'll update this file.
