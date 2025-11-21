# Festive Connect Agent — Hardware & Software Requirements

This document lists the recommended hardware and software needed to develop, run, and deploy the Festive Connect Agent codebase. It covers both development and small-production scenarios and includes verification commands.

## Software requirements

Development environment (recommended)
- OS: Windows 10/11, macOS 12+, or Linux (Ubuntu 20.04+)
- Python: 3.11 or 3.12+ (Dockerfile uses 3.13). Use the system or virtual environment for dependency isolation.
- pip: latest
- Node.js: optional (v18+) only if you want to run frontend tooling or test ESM modules in Node; not required to run the static frontend in a browser.
- Browser: modern Chromium/Firefox/Safari with ES module and ReadableStream support for `postWithStream`.

Runtime dependencies
- Backend Python packages: install via `pip install -r backend/requirements.txt`. Key packages include:
  - `fastapi`, `uvicorn[standard]` — HTTP server and ASGI runtime
  - `google-adk` — agent runtime (requires API key)
  - `aiosqlite` — SQLite async client
  - `python-dotenv`, `requests`, `aiohttp` — utilities

Optional tools
- Docker & Docker Compose: for containerized deployment and orchestration.
- VS Code (recommended) with Live Server extension for front-end rapid testing.

Environment variables
- `GOOGLE_API_KEY` — required for Google ADK agent functionality. Set in your shell or pass to Docker.

Examples (PowerShell)
```
# create venv and install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# set API key for current session
$env:GOOGLE_API_KEY = "YOUR_KEY"

# run backend
python backend/main.py
```

Docker (build & run)
```
docker build -t festive-backend .\backend
docker run -p 8080:8080 -e GOOGLE_API_KEY="YOUR_KEY" festive-backend
```

## Hardware requirements

Local development (minimum)
- CPU: 2 cores
- Memory: 4 GB RAM
- Storage: 5 GB free (project + venv + DB)
- Network: outbound internet access to reach Google ADK and any external APIs

Local development (recommended)
- CPU: 4 cores
- Memory: 8–16 GB RAM
- Storage: 20 GB free (room for Docker images and temporary artifacts)
- Network: reliable broadband connection

Small production (single-container) — expected small load (few requests/sec)
- CPU: 2 vCPU
- Memory: 4 GB RAM (8 GB recommended if running additional services)
- Storage: 10–20 GB persistent volume for `festiveconnect.db` and logs
- Network: public IP or load balancer; ensure outbound access to Google ADK endpoints

Medium production (higher throughput or multiple agents)
- CPU: 4+ vCPU
- Memory: 8–16 GB RAM
- Storage: SSD-backed persistent volume (30+ GB) and regular backups of SQLite (or migrate to managed DB)
- Recommend moving from SQLite to Postgres/MySQL for concurrency/scale

Notes on persistence and backups
- `festiveconnect.db` is SQLite persisted under backend working directory. For production, mount a host volume or cloud storage to that path and schedule regular backups. Consider migrating to an RDBMS for higher concurrency and reliability.

Security & secrets
- Keep `GOOGLE_API_KEY` and other secrets out of source control. Use environment variables, secret managers, or Docker secrets in production.
- Restrict CORS (`ALLOW_ORIGINS`) in `backend/main.py` before deploying to production.

Verification checklist
- Confirm Python version:
  - `python --version`
- Confirm packages installed:
  - `pip show fastapi uvicorn google-adk aiosqlite`
- Start backend and verify OpenAPI docs:
  - Open `http://localhost:8080/docs`
- Verify DB file created and writable:
  - Check for `backend/festiveconnect.db` after first API call

Scaling guidance
- For low traffic, the current SQLite + single container is sufficient.
- For higher concurrency or scale, migrate DB to a server RDBMS, add caching (Redis), and run multiple backend instances behind a load balancer.

If you'd like, I can generate a short `run-dev.ps1` and a `docker-compose.yml` tuned to these recommendations. Reply which automation you prefer.
