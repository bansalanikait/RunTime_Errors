# DECEPTRA - Backend Core Implementation

Complete FastAPI honeypot framework for DECEPTRA attack detection and analysis.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (optional)
```

### 3. Run the Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server runs at: `http://localhost:8000`

API Docs: `http://localhost:8000/docs` (Swagger UI)

---

## Architecture

```
app/
├── core/
│   ├── settings.py       # Configuration from .env
│   ├── database.py       # SQLAlchemy async engine and sessions
│   ├── models.py         # ORM models (Session, Request, Trap, DecoyAsset)
│   └── base.py           # Pydantic schemas and API contracts
├── routes/
│   ├── honeypots.py      # Fake endpoints (/admin, /login, /.env, etc.)
│   ├── api_decoys.py     # API for dashboard and AI layer
│   └── utils.py          # Request logging and DB persistence
├── decoys/
│   └── asset_manager.py  # Decoy registry and lookup
└── main.py               # FastAPI app initialization
```

---

## Honeypot Endpoints (Fake)

All endpoints are logged to the database.

| Path | Type | Mimics |
|------|------|--------|
| `/` | GET | Homepage |
| `/admin` | GET | Admin login panel |
| `/login` | GET/POST | Login form/handler |
| `/.env` | GET | Leaked environment file |
| `/api/v1/users` | GET | User API list |
| `/api/v1/users/{id}` | GET | User detail |
| `/debug/errors` | GET | Error/stacktrace page |
| `/config.php` | GET | PHP config file |
| `/robots.txt` | GET | Robots file |
| `/.git/config` | GET | Git config |
| `/xmlrpc.php` | GET | WordPress XML-RPC |
| `/api/login` | POST | API login |

---

## API Endpoints (Real)

### GET /api/health
Health check. Always returns 200 OK.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### GET /api/attacks
List all honeypot sessions.

**Query Parameters:**
- `limit` (int): Max results (default 100)
- `offset` (int): Pagination offset (default 0)

**Response:**
```json
{
  "attacks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "ip_address": "192.168.1.100",
      "first_request_at": "2026-04-26T10:00:00",
      "last_request_at": "2026-04-26T10:05:30",
      "request_count": 5,
      "is_automated": true,
      "tags": "scanner,web-crawler"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

---

### GET /api/attacks/{session_id}
Get full request chain for a session.

**Response:**
```json
{
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "ip_address": "192.168.1.100",
    "first_request_at": "2026-04-26T10:00:00",
    "last_request_at": "2026-04-26T10:05:30",
    "request_count": 5,
    "is_automated": true,
    "tags": "scanner,web-crawler"
  },
  "requests": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "method": "GET",
      "path": "/admin",
      "query_string": null,
      "timestamp": "2026-04-26T10:00:01",
      "response_status": 200,
      "duration_ms": 15,
      "is_trap_hit": false
    }
  ]
}
```

---

### POST /api/decoys
Create or update a decoy asset.

**Request Body:**
```json
{
  "asset_type": "endpoint",
  "name": "fake_admin_panel",
  "path": "/admin",
  "description": "Fake admin login panel",
  "mimics": "admin_panel",
  "is_active": true
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "fake_admin_panel",
  "asset_type": "endpoint",
  "path": "/admin",
  "is_active": true
}
```

---

### GET /api/decoys
List all decoy assets.

**Query Parameters:**
- `active_only` (bool): Only return active decoys (default true)

---

### GET /api/decoys/{decoy_id}
Get a single decoy asset by ID.

---

## Database Schema

### Sessions Table
Groups requests by IP address within a time window.

```python
Session
├── id (UUID, primary key)
├── ip_address (String, indexed)
├── first_request_at (DateTime)
├── last_request_at (DateTime)
├── user_agent (String)
├── request_count (Integer)
├── is_automated (Boolean)
├── tags (String, comma-separated)
└── created_at (DateTime)
```

### Requests Table
Every HTTP request to any honeypot endpoint.

```python
Request
├── id (UUID, primary key)
├── session_id (UUID, foreign key)
├── method (String)
├── path (String, indexed)
├── query_string (String)
├── headers_json (Text, sanitized)
├── body (Text, truncated)
├── response_status (Integer)
├── response_body (Text)
├── is_trap_hit (Boolean)
├── timestamp (DateTime, indexed)
└── duration_ms (Integer)
```

### Traps Table
Spider trap definitions (URLs that should never be accessed).

```python
Trap
├── id (UUID, primary key)
├── path_pattern (String, unique)
├── description (String)
├── response_status (Integer)
└── created_at (DateTime)
```

### DecoyAsset Table
Metadata about decoy endpoints and files.

```python
DecoyAsset
├── id (UUID, primary key)
├── asset_type (String)
├── name (String, unique, indexed)
├── path (String)
├── description (String)
├── mimics (String)
├── response_template (Text)
├── is_active (Boolean)
├── created_at (DateTime)
└── updated_at (DateTime)
```

---

## Request Logging Middleware

Every HTTP request is automatically logged to the database:

- **Client IP**: From request.client.host
- **Method/Path**: HTTP method and path
- **Headers**: Sanitized (Authorization, Cookie, X-API-Key redacted)
- **Body**: Truncated if > 10KB
- **Status**: Response HTTP status code
- **Duration**: Processing time in milliseconds

Logging happens in middleware before route handlers execute, so it captures all requests including errors.

---

## Testing

### Test Health Check
```bash
curl http://localhost:8000/api/health
```

### Test Honeypot
```bash
curl http://localhost:8000/admin
```

### Test Login (Will be logged)
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "attacker", "password": "test"}'
```

### Retrieve Logged Sessions
```bash
curl http://localhost:8000/api/attacks
```

---

## Development

### Structure
- **app/core/** — Database and models (do not edit without coordination)
- **app/routes/** — HTTP endpoints
- **app/decoys/** — Decoy asset management
- **templates/** — Jinja2 HTML templates
- **app/main.py** — FastAPI app and middleware

### Code Style
- Async/await for all I/O
- Pydantic for validation
- SQLAlchemy ORM for database
- Dependency injection via FastAPI Depends()

### Adding New Endpoints
1. Create function in appropriate router file
2. Use `@router.get()` or `@router.post()` decorator
3. Add `include_in_schema=False` for honeypot endpoints
4. Add dependency: `session: AsyncSession = Depends(get_session)`
5. Log will happen automatically via middleware

---

## Constraints

✅ No microservices  
✅ No new top-level folders  
✅ No edits to app/ai/  
✅ No edits to app/analyzer/ business logic (only call functions)  
✅ SQLite + SQLAlchemy async  
✅ Idiomatic FastAPI/Pydantic  
✅ All requests logged to DB  

---

## Future Enhancements

- Bot detection heuristics
- Rate limiting / DDoS protection
- WebSocket live feeds
- Advanced threat scoring
- Integration with analyzer and AI layers

---

## Support

For issues or questions:
- Check /docs endpoint for interactive API documentation
- Review BACKEND_CORE_PLAN.md for architecture details
- See Global.txt for project constraints

---

**Version**: 1.0.0  
**Last Updated**: 2026-04-26
