# DECEPTRA Backend - Quick Start Guide

Get the honeypot server running in 5 minutes.

---

## 1️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (async web framework)
- SQLAlchemy (ORM)
- Uvicorn (ASGI server)
- Pydantic (validation)
- aiosqlite (async SQLite)

---

## 2️⃣ Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env if you want to customize settings
```

Default settings work out-of-the-box (SQLite database, DEBUG mode).

---

## 3️⃣ Run the Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## 4️⃣ Test the Server

### Health Check
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{"status": "ok", "version": "1.0.0"}
```

---

## 5️⃣ Try Honeypot Endpoints

### Admin Panel
```bash
curl http://localhost:8000/admin
```
Returns HTML login form.

### Fake Login (Captured!)
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "hacker", "password": "secret123"}'
```

Status: **401 Unauthorized** (always fails)

### Leaked .env File
```bash
curl http://localhost:8000/.env
```

Returns fake environment variables with fake credentials.

### Fake User API
```bash
curl http://localhost:8000/api/v1/users
```

Returns JSON list of fake users.

### Error Page
```bash
curl http://localhost:8000/debug/errors
```

Returns HTML with fake Python traceback.

---

## 6️⃣ Query Captured Requests

### List All Sessions
```bash
curl http://localhost:8000/api/attacks
```

**Response:**
```json
{
  "attacks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "ip_address": "127.0.0.1",
      "first_request_at": "2026-04-26T10:00:00",
      "last_request_at": "2026-04-26T10:00:05",
      "request_count": 3,
      "is_automated": false,
      "tags": null
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

### Get Session Details
```bash
# Replace with your session ID
curl http://localhost:8000/api/attacks/550e8400-e29b-41d4-a716-446655440000
```

**Response shows:**
- Session metadata (IP, timestamps, request count)
- Full request chain (all HTTP requests from this session)

---

## 7️⃣ Create Decoy Assets

### Define a New Honeypot Endpoint
```bash
curl -X POST http://localhost:8000/api/decoys \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "endpoint",
    "name": "fake_admin",
    "path": "/admin",
    "description": "Admin login panel",
    "mimics": "admin_panel",
    "is_active": true
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "fake_admin",
  "asset_type": "endpoint",
  "path": "/admin",
  "is_active": true
}
```

### List All Decoy Assets
```bash
curl http://localhost:8000/api/decoys
```

### Get Specific Decoy
```bash
curl http://localhost:8000/api/decoys/550e8400-e29b-41d4-a716-446655440001
```

---

## 🔍 View Interactive API Docs

Open your browser:

```
http://localhost:8000/docs
```

**Features:**
- Try endpoints directly in the browser
- See request/response schemas
- Auto-generated from code

---

## 📊 Database

SQLite database file: `deceptra.db`

### Query Database Directly (Optional)

```bash
sqlite3 deceptra.db

# See all sessions
sqlite> SELECT ip_address, request_count FROM sessions;

# See all requests
sqlite> SELECT method, path, response_status FROM requests;

# Exit
sqlite> .quit
```

---

## 🧪 Run Tests

```bash
pip install pytest pytest-asyncio httpx

# Run all tests
pytest test_backend.py -v

# Run specific test class
pytest test_backend.py::TestHoneypotEndpoints -v

# Run with output
pytest test_backend.py -v -s
```

---

## 📝 Common Workflows

### Simulate an Attack
```bash
# 1. Hit honeypot endpoints
curl http://localhost:8000/admin
curl http://localhost:8000/login
curl http://localhost:8000/.env

# 2. View captured session
curl http://localhost:8000/api/attacks
# -> Copy session ID

# 3. Get full attack chain
curl http://localhost:8000/api/attacks/{session_id}
```

### Add New Decoy
```bash
# Create a new decoy asset
curl -X POST http://localhost:8000/api/decoys \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "endpoint",
    "name": "fake_backup",
    "path": "/backup.sql",
    "description": "Fake SQL backup file",
    "mimics": "database_backup",
    "is_active": true
  }'

# The endpoint automatically appears in honeypot routes
# (requires app restart or route registration)
```

### Monitor Live Activity
```bash
# In terminal 1: Run server
python -m uvicorn app.main:app --reload

# In terminal 2: Poll for new sessions
while true; do
  curl http://localhost:8000/api/attacks
  sleep 5
done
```

---

## 🛑 Stop the Server

Press `Ctrl+C` in the terminal running the server.

```
Shutdown complete
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
python -m uvicorn app.main:app --port 8001
```

### Database Errors
```bash
# Delete database to start fresh
rm deceptra.db

# Restart server
python -m uvicorn app.main:app --reload
```

### Permission Denied (Linux/Mac)
```bash
chmod +x app/main.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Next Steps

1. **Read [API_CONTRACTS.md](API_CONTRACTS.md)** — Full API documentation with frozen schemas
2. **Read [README_BACKEND.md](README_BACKEND.md)** — Architecture and database schema
3. **Read [BACKEND_CORE_PLAN.md](../BACKEND_CORE_PLAN.md)** — Implementation details
4. **Explore [app/routes/honeypots.py](app/routes/honeypots.py)** — All fake endpoints
5. **Explore [app/routes/api_decoys.py](app/routes/api_decoys.py)** — Dashboard API

---

## 🚀 Deployment

For production:

1. Set `DEBUG=False` in `.env`
2. Use a production database (PostgreSQL recommended)
3. Run with Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```
4. Use reverse proxy (nginx) for SSL/TLS
5. Monitor logs: `tail -f app/logs/deceptra.log`

---

## 💡 Tips

- **Auto-reload**: The `--reload` flag restarts on code changes
- **Debug mode**: Set `DEBUG=True` in `.env` to see SQL statements
- **Pagination**: Use `?limit=50&offset=50` for large result sets
- **Timestamps**: All dates are ISO 8601 format (UTC)

---

**Happy honeypot hunting! 🍯**

For questions, see [README_BACKEND.md](README_BACKEND.md) or [API_CONTRACTS.md](API_CONTRACTS.md).
