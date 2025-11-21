# Festive Connect Agent — Testing Plan & Test Cases

Last updated: 2025-11-21

This document is a complete, production-quality testing section you can drop into a project report. It maps testing strategy and concrete test cases to the repository source so QA or engineers can implement tests quickly.

Contents
- 1 Design of Testing
  - 1.1 Unit Testing
  - 1.2 Integration Testing
  - 1.3 Validation Testing
- 2 System Testing
  - 2.1 Code Testing
  - 2.2 Specification Testing
- 3 Acceptance Testing
- 4 Test Plan
  - 4.1 Unit test plan
- 5 Test Cases
  - Example test cases mapped to files and functions

---

1 Design of Testing

This project uses layered testing to achieve fast feedback and high confidence:

- Unit tests: isolate and test single functions or classes. Focus areas include business logic in `backend/services/service.py`, data normalization in `backend/repos/repo.py`, and tool helpers in `backend/agent/tools.py`.
- Integration tests: execute the HTTP API end-to-end (FastAPI routers → services → repos). Use FastAPI TestClient or `httpx.AsyncClient` against the app configured with a temporary SQLite database.
- Validation tests: exercise Pydantic input validation (router-level 422 cases) and tool input validation (tools raising `ValueError` when required fields are missing).

1.1 Unit Testing

Scope and targets:

- `backend/repos/repo.py`:
  - `_normalize_event()`, `_performers_str()` — ensure consistent conversion between CSV performers and list.
  - CRUD parameter construction — confirm `insert`/`update` map event data to SQL parameters correctly.
- `backend/services/service.py`:
  - `create_event()` — id generation (uuid4), timestamp assignment, conflict handling (409).
  - `get_events_this_month()`, `get_recent_events_15_days()`, `get_most_recent_event()` — date parsing and filtering.
  - `get_city_with_most_events()`, `get_top_performer()` — aggregation using `Counter`.
- `backend/agent/tools.py`:
  - `_event_to_dict()` and `_organizer_to_dict()` — consistent output shapes.
  - `events_by_month()` — string and numeric month parsing.

Best practices:

- Use pytest and pytest-asyncio for async functions.
- Use temporary SQLite files (pytest tmp_path fixture) for repo tests; do not use global `:memory:` unless a single shared connection is used.
- Keep unit tests deterministic by mocking network/ADK calls and by seeding deterministic timestamps where needed (monkeypatch datetime.now).

1.2 Integration Testing

Scope and targets:

- HTTP endpoint flows defined in `backend/routers/events.py` and `backend/routers/organizers.py`.
- Analytics and audit endpoints in `backend/routers/events.py` (`/analytics/*`, `/audit/*`).

Approach:

- Use FastAPI's TestClient or `httpx.AsyncClient` with app created via the same factory used by `backend/main.py` (prefer an app factory accepting a DB path). If an app factory is not present, tests can patch `constants.DB_NAME` before importing the app and create a temp DB file.
- Each test should initialize `repo.init_db()` and run in an isolated temporary directory.

Example integration scenarios:

- Create → Read → Update → Delete flow for `/events/` (verify status codes and payloads).
- Seed several events for `/events/analytics/top-city` and assert returned city and count.
- Organizer endpoints: create organizer and query `/organizers/analytics/company-events`.

1.3 Validation Testing

Scope:

- Pydantic model validation in `backend/models/data_models.py` (missing required fields lead to HTTP 422).
- Tool-level validation: `create_event_tool()` should raise `ValueError` when required fields are missing.

Key checks:

- POST `/events/` without `title` or `date` returns 422.
- `create_event_tool({})` raises `ValueError("Missing required fields: title, date, location")` or equivalent.

---

2 System Testing

System testing validates the whole application stack including runtime, agent interactions, and frontend streaming.

2.1 Code Testing

Include automated checks:

- Linting: `ruff` or `flake8`.
- Formatting: `black` with configured project settings.
- Type checking: `mypy` (optional but recommended for service layer and model contracts).

2.2 Specification Testing

Verify the system meets business-level specifications in `REQUIREMENTS.md`:

- Endpoints exist and conform to the documented shapes.
- Agent prompts and tools produce outputs that the frontend can parse and display.

System test scenarios:

- Full UI flow: launch backend (dev env), serve `frontend/` statically, use a browser automation (Playwright) to create an event and confirm it appears in the event list.
- Streaming: test that the chat page receives `data: <json>\n` frames and the `postWithStream` callback receives parsed JSON objects.

---

3 Acceptance Testing

Acceptance tests should be written from the user/business perspective and map to requirements. Sample acceptance scenarios:

- A festival manager can create an event via the UI and later update its location; the event timestamps exist, and the audit endpoints reflect the change.
- The analytics endpoints report the top city and top performer correctly after seeding representative data.
- The organizer analytics endpoints return the correct aggregated counts for a given company and region.

Pass/fail criteria

- All acceptance tests must pass in the staging environment for a release candidate to be accepted.

---

4 Test Plan

Structure the `tests/` directory as follows:

- `tests/unit/` — unit tests for services, repos, tools.
- `tests/integration/` — API endpoint tests using TestClient/httpx.
- `tests/system/` — optional end-to-end Playwright/Selenium tests.

4.1 Unit Test Plan

Fixture ideas:

- `tmp_db` (pytest fixture): creates a temporary sqlite file path and yields it. After test cleanup remove file.
- `repo` (pytest-asyncio fixture): instantiate `Repo(db_path=tmp_db)` and call `await repo.init_db()`.
- `service` (pytest-asyncio fixture): create `Service(repo)` with the repo fixture.
- `client` (fastapi TestClient fixture): create TestClient with app configured to use tmp_db.

CI integration

- Add a GitHub Actions workflow `ci.yml` that installs Python, sets up venv, installs `-r backend/requirements.txt` plus `pytest` and runs `pytest -q`.

---

5 Test Cases (representative and ready-to-implement)

Unit tests (pytests)

1. test_normalize_event_csv_performers
- File: `tests/unit/test_repo.py`
- Target: `Repo._normalize_event`
- Input: dict with `performers` = "DJ Riz, Singer A, Band B"
- Expect: `performers` list `['DJ Riz','Singer A','Band B']`

2. test_create_event_generates_id_timestamps
- File: `tests/unit/test_service.py`
- Target: `Service.create_event`
- Input: Event without `id` and timestamps
- Expect: returned Event has `id` (uuid4 string), `created_at` and `updated_at` in ISO format; repo contains the event.

3. test_create_event_duplicate_raises
- Target: `Service.create_event`
- Setup: pre-insert an event with same `id`
- Expect: `HTTPException` with status 409

4. test_get_events_this_month_various_formats
- Target: `Service.get_events_this_month`
- Setup: insert events with date formats: ISO `YYYY-MM-DD`, `YYYY-MM-DDTHH:MM:SS`, and textual `November 21, 2025`
- Expect: only those that parse to current month returned.

5. test_event_to_dict_consistent_shape
- Target: `tools._event_to_dict`
- Input: Event object and event dict
- Expect: same output keys: `id,title,date,location,performers,description,created_at,updated_at`

Integration tests (pytests using TestClient/httpx)

6. test_event_crud_flow
- File: `tests/integration/test_events_api.py`
- Steps:
  - POST `/events/` create event -> assert 201 and JSON contains id
  - GET `/events/{id}` -> assert fields match
  - PUT `/events/{id}` update location -> assert 200 and updated field
  - DELETE `/events/{id}` -> assert 204 and subsequent GET returns 404

7. test_analytics_total_and_top_city
- Seed multiple events across cities and dates
- GET `/events/analytics/total` -> assert count
- GET `/events/analytics/top-city` -> assert expected city and count

8. test_organizer_analytics
- Create several organizers with managed_events values
- GET `/organizers/analytics/company-events?company=Acme` -> assert managed_events total

Validation tests

9. test_post_event_missing_fields_returns_422
- POST `/events/` without `title` -> assert 422 and error message includes field name

10. test_create_event_tool_missing_fields_raises
- Call `create_event_tool({})` directly and assert `ValueError` with missing fields list

System tests (optional automation)

11. test_chat_streaming_frames_parsed
- Start a test server endpoint that yields `data: {"role":"assistant","content":"hi"}\n` repeated
- Use `frontend/services/apiService.js::postWithStream` (instrumented or simulated) to assert parsed results

Traceability matrix (short)

- Requirement: Event CRUD API -> Tests: test_event_crud_flow
- Requirement: Analytics endpoints -> Tests: test_analytics_total_and_top_city
- Requirement: Organizer analytics -> Tests: test_organizer_analytics
- Requirement: Streaming format -> Tests: test_chat_streaming_frames_parsed

---

Execution & tooling

Install test deps (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install pytest pytest-asyncio httpx
```

Run tests:

```powershell
# run all tests
pytest -q

# run a single test module
pytest tests/unit/test_service.py -q
```

Playwright (UI/system tests)

```powershell
pip install playwright
playwright install
pytest tests/system -q
```

CI recommendations

- Run `pytest -q` on PRs. Add caching for pip packages. Optionally run Playwright UI tests on nightly builds or gated staging deploys.

---

Appendix: Test scaffolding snippets (pytest fixtures)

```python
# conftest.py (example)
import os
import tempfile
import pytest
from backend.repos.repo import Repo

@pytest.fixture
def tmp_db(tmp_path):
    p = tmp_path / "test_festive.db"
    return str(p)

@pytest.fixture
async def repo(tmp_db):
    r = Repo(db_path=tmp_db)
    await r.init_db()
    return r

@pytest.fixture
def anyio_backend():
    return "asyncio"

```

If you want, I can scaffold the `tests/` tree with the representative tests above and add a GitHub Actions `ci.yml` that runs pytest. Which would you like me to create now?
