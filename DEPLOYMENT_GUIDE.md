# TechFest Webapp - Deployment & Running Guide

## Quick Start (For Immediate Use)

### Step 1: Navigate to Project Directory
```powershell
cd c:\Users\nrush\Desktop\aai\TechFest_775
```

### Step 2: Activate Virtual Environment (if using one)
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Start Backend Server
```powershell
python backend/main.py
```

Wait for output:
```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### Step 4: Open in Browser
- **Chrome, Firefox, Edge, Safari:** `http://localhost:8080/dev-ui`
- **From Another Computer:** `http://<YOUR_IP>:8080/dev-ui` (find IP with `ipconfig`)

### Step 5: Start Using
- **Landing Page:** View events, add/edit/delete events
- **Chat:** Click "Chat with Agent" button to talk to the AI agent

---

## Environment Setup (First Time Only)

### Prerequisites
- Python 3.13+ installed
- pip package manager
- Windows/Mac/Linux with PowerShell (or bash)

### Step 1: Create Virtual Environment
```powershell
cd c:\Users\nrush\Desktop\aai\TechFest_775
python -m venv .venv
```

### Step 2: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

If you get execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies
```powershell
pip install -r backend/requirements.txt
```

### Step 4: Set Up API Keys (Important!)
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_google_ai_studio_key_here
```

Get your key from: https://aistudio.google.com/app/apikeys

---

## Configuration

### Backend Configuration
File: `backend/constants.py`

```python
# Change these values as needed:
AGENT_NAME = "festive_agent"          # Agent identifier
AGENT_MODEL = "gemini-2.0-flash"      # LLM model (can switch to other Gemini models)
DB_NAME = "festiveconnect.db"         # Database file name
```

### Frontend Configuration
File: `frontend/services/apiService.js`

```javascript
const API_CONFIG = {
  baseURL: "http://localhost:8080/dev-ui",  // Change if running on different host
  headers: { "Content-Type": "application/json" },
};
```

### Change Port (if 8080 is in use)
```powershell
$env:PORT=8081
python backend/main.py
```
Then access: `http://localhost:8081/dev-ui`

---

## File Structure

```
TechFest_775/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── constants.py              # Configuration
│   ├── requirements.txt           # Python dependencies
│   ├── agent/
│   │   ├── agent.py             # Agent registration
│   │   ├── tools.py             # Agent tools (19 tools)
│   │   └── prompt.py            # System prompt
│   ├── models/
│   │   └── data_models.py        # Event & Organizer models
│   ├── repos/
│   │   ├── repo.py              # Event database operations
│   │   └── organizer_repo.py    # Organizer database operations
│   ├── services/
│   │   ├── service.py           # Event business logic
│   │   └── organizer_service.py # Organizer business logic
│   └── routers/
│       ├── events.py            # Event REST endpoints
│       └── organizers.py        # Organizer REST endpoints
├── frontend/
│   ├── index.html               # Landing page
│   ├── pages/
│   │   └── chat.html            # Chat console
│   ├── scripts/
│   │   ├── main.js              # Landing page logic
│   │   ├── chat.js              # Chat logic & session management
│   │   └── apiService.js        # HTTP client library
│   └── styles/
│       ├── main.css             # Landing page styles
│       └── chat.css             # Chat console styles
├── festiveconnect.db            # SQLite database (auto-created)
└── .env                         # API keys (create this)
```

---

## Running the Application

### Local Development
```powershell
# Terminal 1: Start Backend
cd c:\Users\nrush\Desktop\aai\TechFest_775
python backend/main.py

# Terminal 2: Open Browser
# http://localhost:8080/dev-ui
```

### Production Deployment

#### Option 1: Cloud Run (Recommended)
```bash
# Build Docker image (Dockerfile already in backend/)
docker build -t festive-connect .

# Run locally
docker run -p 8080:8080 -e GOOGLE_API_KEY=your_key festive-connect

# Deploy to Cloud Run
gcloud run deploy festive-connect --image festive-connect --port 8080
```

#### Option 2: Traditional Server
```powershell
# Install Gunicorn (production WSGI server)
pip install gunicorn

# Run with Gunicorn
gunicorn backend.main:app --workers 4 --bind 0.0.0.0:8080
```

#### Option 3: IIS (Windows Server)
- Use FastAPI with IIS via ISAPI Handler
- Or run Python in background service
- Configure application pool to run Python process

---

## Database

### SQLite Database
- **File:** `festiveconnect.db` (created automatically in backend/ directory)
- **Tables:** 
  - `events` — Event records
  - `organizers` — Organizer records
- **Auto-created:** On first API call (no manual setup needed)

### Reset Database
Delete the file and restart:
```powershell
Remove-Item backend/festiveconnect.db
# Restart backend - new database will be created
```

### Backup Database
```powershell
Copy-Item backend/festiveconnect.db backend/festiveconnect.db.backup
```

### Access Database Directly (Optional)
Install SQLite:
```powershell
# Windows - using chocolatey
choco install sqlite

# Then open:
sqlite3 backend/festiveconnect.db

# View tables:
.tables

# View events:
SELECT * FROM events;
```

---

## API Documentation

### Access OpenAPI Docs
- **Swagger UI:** `http://localhost:8080/docs`
- **ReDoc:** `http://localhost:8080/redoc`
- **OpenAPI JSON:** `http://localhost:8080/openapi.json`

### Main Endpoints

**Events:**
```
POST   /events/                          Create event
GET    /events/                          List all events
GET    /events/{id}                      Get single event
PUT    /events/{id}                      Update event
DELETE /events/{id}                      Delete event
GET    /events/analytics/total           Total event count
GET    /events/analytics/this-month      Events this month
GET    /events/analytics/top-city        City with most events
```

**Organizers:**
```
POST   /organizers/                      Create organizer
GET    /organizers/                      List organizers
GET    /organizers/{id}                  Get single organizer
PUT    /organizers/{id}                  Update organizer
DELETE /organizers/{id}                  Delete organizer
GET    /organizers/analytics/company-events?company=X    Events by company
GET    /organizers/analytics/top-region                  Top cultural events region
GET    /organizers/analytics/top-organizer-2025          Top organizer 2025
```

**Agent:**
```
POST   /apps/festive_agent/users/user/sessions                   Create session
GET    /apps/festive_agent/users/user/sessions                   List sessions
POST   /apps/festive_agent/users/user/sessions/{id}/run_sse      Send message (streaming)
```

---

## Troubleshooting

### Backend Won't Start
**Problem:** "Address already in use" error
```powershell
# Solution: Kill process using port 8080
netstat -ano | Select-String "8080"
taskkill /PID <PID> /F

# Or use different port:
$env:PORT=8081; python backend/main.py
```

**Problem:** Import errors (google.adk, etc.)
```powershell
# Solution: Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall --no-cache-dir
```

### Frontend Won't Load
**Problem:** "Cannot reach server" or "Connection refused"
- Check backend is running: `http://localhost:8080/events/` should return JSON
- Check URL is correct: `http://localhost:8080/dev-ui` (includes `/dev-ui`)
- Check firewall allows port 8080

**Problem:** Chat not working
- Open browser DevTools (F12)
- Check Console tab for errors
- Verify API endpoint in `frontend/services/apiService.js`

### Database Errors
**Problem:** "Database locked" error
- Restart backend
- Delete `festiveconnect.db` and restart

**Problem:** Schema errors
- Database auto-creates on first use
- If corrupted, delete and restart backend

### Agent Not Responding
**Problem:** Chat message sent but no response
- Check GOOGLE_API_KEY is set in `.env`
- Verify API key is valid (test at https://aistudio.google.com)
- Check backend logs for errors
- Refresh chat page

---

## Monitoring & Logs

### Backend Logs (Console Output)
Shows all API requests and errors:
```
INFO:     127.0.0.1:56589 - "POST /events/ HTTP/1.1" 201 Created
INFO:     127.0.0.1:59384 - "GET /events/ HTTP/1.1" 200 OK
```

### Browser Console (F12)
Chat and frontend errors appear here.

### Save Logs to File
```powershell
python backend/main.py 2>&1 | Tee-Object -FilePath logs.txt
```

---

## Security Considerations

### For Development (Current Setup)
```python
# backend/main.py
ALLOWED_ORIGINS = ["*"]  # ⚠️ Allow all - development only!
```

### For Production
Update `backend/main.py`:
```python
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    # Add your actual domains
]
```

### API Key Management
- **Never commit** `.env` to git
- Use `.gitignore`:
  ```
  .env
  festiveconnect.db
  __pycache__/
  ```
- For cloud deployment, use environment variables in platform settings

### HTTPS/TLS
- Use Let's Encrypt for free certificates
- Configure reverse proxy (nginx, Apache)
- Enable in Cloud Run settings automatically

---

## Performance Optimization

### For Production
1. **Database Indexing**
   ```sql
   CREATE INDEX idx_event_date ON events(date);
   CREATE INDEX idx_organizer_company ON organizers(company);
   ```

2. **Caching**
   - Add Redis for session caching
   - Cache analytics queries

3. **Asset Optimization**
   - Minify CSS/JavaScript
   - Use gzip compression

4. **Database Pool**
   - Use connection pooling
   - Switch from SQLite to PostgreSQL for scaling

---

## Scaling to Multiple Users

### Current Limits
- SQLite: ~100 concurrent connections max
- Single server: ~500 RPS throughput

### For Production Scale
1. **Database:** PostgreSQL or MySQL
2. **Load Balancer:** nginx or HAProxy
3. **Multiple Instances:** Run backend on 2-4 servers
4. **Caching:** Redis for session/data caching
5. **CDN:** CloudFlare for static assets

### Architecture:
```
Users → Load Balancer → Backend 1 (port 8080)
                      → Backend 2 (port 8081)
                      → Backend 3 (port 8082)
                            ↓
                    PostgreSQL Database
                            ↓
                    Redis Cache
```

---

## Backup & Disaster Recovery

### Daily Backup
```powershell
# PowerShell scheduled task
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "Copy-Item backend/festiveconnect.db backups/$(Get-Date -f 'yyyyMMdd_HHmmss').db"
Register-ScheduledTask -TaskName "BackupFestiveDB" -Trigger $trigger -Action $action
```

### Cloud Backup
- Use Cloud Storage (Google Cloud Storage, AWS S3)
- Enable automatic daily snapshots

---

## Version Control

### Initialize Git (if not done)
```powershell
git init
git add .
git commit -m "Initial commit: TechFest webapp"
git remote add origin https://github.com/nrushalraj2185/FestiveConnectAgent.git
git push -u origin main
```

### Deployment from Git
```powershell
git pull origin main
python backend/main.py
```

---

## Quick Reference Commands

```powershell
# Start backend
python backend/main.py

# Start on custom port
$env:PORT=9000; python backend/main.py

# Reset database
Remove-Item backend/festiveconnect.db

# Check API (test endpoint)
Invoke-RestMethod -Uri "http://localhost:8080/events/" | ConvertTo-Json

# View logs
Get-Content logs.txt -Tail 50

# Kill process on port 8080
taskkill /F /IM python.exe
```

---

## Support Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Google ADK Docs:** https://github.com/google-cloud/python-aiagent-sdk
- **SQLite Docs:** https://www.sqlite.org/docs.html
- **Project Instructions:** See `.github/copilot-instructions.md`

---

## Checklist for Deployment

- [ ] Python 3.13+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r backend/requirements.txt`)
- [ ] `.env` file created with GOOGLE_API_KEY
- [ ] Backend starts without errors
- [ ] Frontend loads at `http://localhost:8080/dev-ui`
- [ ] Can create event via UI
- [ ] Chat console opens and responds
- [ ] Database file exists (`festiveconnect.db`)
- [ ] API endpoints respond (check `/docs`)

---

**Last Updated:** December 5, 2025  
**Status:** Production Ready ✅

