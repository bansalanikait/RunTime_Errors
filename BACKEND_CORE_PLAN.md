# DECEPTRA Backend Core Implementation Plan - Role 1

**Target**: Complete FastAPI backend + honeypot framework for DECEPTRA
**Scope**: `app/core/`, `app/routes/`, `app/decoys/`, `app/analyzer/` (read-only calls), `templates/` (decoy HTML)
**Constraints**: No microservices, no AI layer edits, minimal schema, SQLite + SQLAlchemy
**Audience**: AI agent implementation + human review

---

## 1. Architecture Overview

### 1.1 Tech Stack
- **Framework**: FastAPI 0.95+
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: SQLite with WAL mode
- **Templates**: Jinja2
- **HTTP Client**: httpx (for potential external API calls)
- **Logging**: Python logging + request middleware persistence

### 1.2 Module Responsibilities

```
app/
├── core/
│   ├── settings.py      → Configuration & ENV vars
│   ├── database.py      → SQLAlchemy engine, session factory
│   ├── models.py        → SQLAlchemy ORM models
│   └── base.py          → Pydantic schemas & common types
├── routes/
│   ├── __init__.py      → Router registration
│   ├── health.py        → GET /api/health
│   ├── honeypots.py     → Decoy endpoints (/admin, /login, /.env, etc.)
│   ├── api_decoys.py    → GET/POST /api/attacks, /api/decoys
│   └── spider_traps.py  → Trap detection & logging (if needed)
├── decoys/
│   ├── asset_manager.py → Decoy asset registry & metadata
│   └── templates/       → Decoy HTML/CSS snippets
├── analyzer/
│   └── (pre-existing; we call its functions, don't modify)
├── ai/
│   └── (pre-existing; do not edit)
├── main.py              → FastAPI app initialization
templates/
├── admin.html           → Fake admin panel
├── login.html           → Fake login form
├── error.html           → Fake error/stack trace
└── (other decoy templates)
```

---

## 2. Database Schema

### 2.1 SQLAlchemy Models

**Purpose**: Store all honeypot activity for later analysis by AI layer.

#### `Session` Model
Represents a grouped attacker session (e.g., same IP within time window).

```python
class Session(Base):
    __tablename__ = "sessions"
    
    id: UUID = Column(UUID, primary_key=True, default=uuid4)
    ip_address: str = Column(String(45), index=True)
    first_request_at: datetime = Column(DateTime, default=datetime.utcnow, index=True)
    last_request_at: datetime = Column(DateTime, onupdate=datetime.utcnow)
    user_agent: str = Column(String(500), nullable=True)
    request_count: int = Column(Integer, default=0)
    is_automated: bool = Column(Boolean, default=False)  # heuristic: bot?
    tags: str = Column(String(200), nullable=True)  # comma-separated tags: "scanner", "crawler", etc.
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    requests = relationship("Request", back_populates="session", cascade="all, delete-orphan")
```

#### `Request` Model
Every HTTP hit to any honeypot endpoint.

```python
class Request(Base):
    __tablename__ = "requests"
    
    id: UUID = Column(UUID, primary_key=True, default=uuid4)
    session_id: UUID = Column(UUID, ForeignKey("sessions.id"), index=True)
    method: str = Column(String(10))  # GET, POST, etc.
    path: str = Column(String(500), index=True)
    query_string: str = Column(String(1000), nullable=True)
    headers_json: str = Column(Text, nullable=True)  # JSON blob (sanitized)
    body: str = Column(Text, nullable=True)  # Truncated if >10KB
    response_status: int = Column(Integer)
    response_body: str = Column(Text, nullable=True)  # Response sent back
    is_trap_hit: bool = Column(Boolean, default=False)
    timestamp: datetime = Column(DateTime, default=datetime.utcnow, index=True)
    duration_ms: int = Column(Integer, nullable=True)
    
    session = relationship("Session", back_populates="requests")
```

#### `Trap` Model
Spider trap definitions (e.g., URLs that should never exist).

```python
class Trap(Base):
    __tablename__ = "traps"
    
    id: UUID = Column(UUID, primary_key=True, default=uuid4)
    path_pattern: str = Column(String(500), unique=True)
    description: str = Column(String(500))
    response_status: int = Column(Integer, default=404)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
```

#### `DecoyAsset` Model
Metadata about decoy endpoints, templates, and their purpose.

```python
class DecoyAsset(Base):
    __tablename__ = "decoy_assets"
    
    id: UUID = Column(UUID, primary_key=True, default=uuid4)
    asset_type: str = Column(String(50))  # "endpoint", "file", "credential"
    name: str = Column(String(200), unique=True, index=True)
    path: str = Column(String(500), nullable=True)
    description: str = Column(String(1000))
    mimics: str = Column(String(200))  # What does it pretend to be? "admin_panel", "env_file"
    response_template: str = Column(Text, nullable=True)
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, onupdate=datetime.utcnow)
```

---

## 3. Core Modules

### 3.1 `app/core/settings.py`

**Responsibility**: Load configuration from environment or defaults.

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # App
    app_name: str = "DECEPTRA"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./deceptra.db"
    
    # Request logging
    max_body_log_size: int = 10000  # bytes
    log_headers_sanitize: bool = True
    log_level: str = "INFO"
    
    # Request timeout
    request_timeout_ms: int = 30000
    
    # CORS (if needed)
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 3.2 `app/core/database.py`

**Responsibility**: SQLAlchemy async engine, session factory, DB initialization.

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings
from app.core.models import Base

# Async SQLite URL
DATABASE_URL = settings.database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
)

async_session_maker = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    """Dependency for FastAPI routes."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 3.3 `app/core/models.py`

**Responsibility**: SQLAlchemy ORM definitions.

(See Schema section 2.1 above)

### 3.4 `app/core/base.py`

**Responsibility**: Shared Pydantic schemas for request/response validation.

```python
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, List

class RequestInfoSchema(BaseModel):
    id: UUID
    session_id: UUID
    method: str
    path: str
    query_string: Optional[str]
    timestamp: datetime
    response_status: int
    duration_ms: Optional[int]

class SessionSummarySchema(BaseModel):
    id: UUID
    ip_address: str
    first_request_at: datetime
    last_request_at: datetime
    request_count: int
    is_automated: bool
    tags: Optional[str]

class SessionDetailSchema(SessionSummarySchema):
    requests: List[RequestInfoSchema]

class DecoyAssetSchema(BaseModel):
    id: UUID
    name: str
    asset_type: str
    path: Optional[str]
    description: str
    mimics: str
    is_active: bool
    
    class Config:
        from_attributes = True
```

---

## 4. Honeypot Routes (`app/routes/honeypots.py`)

### 4.1 Design Principles
- **Every request is logged** via middleware before route handler.
- **Never perform destructive actions** (no actual DB writes except logs).
- **Return realistic responses** (HTML, JSON, status codes that mimic real systems).
- **Accept all input** (GET/POST/headers/body) without validation errors.

### 4.2 Endpoint List

| Path | Method | Mimics | Response | Notes |
|------|--------|--------|----------|-------|
| `/` | GET | Homepage | HTML (generic) | Real site homepage |
| `/admin` | GET | Admin panel | HTML login form | Classic honeypot |
| `/login` | GET | Login form | HTML form | Alternative /admin |
| `/login` | POST | Login handler | 302 redirect OR JSON error | Accept username/password |
| `/.env` | GET | Leaked env file | Plain text (fake vars) | Classic easy target |
| `/api/v1/users` | GET | User API | JSON array | Fake user records |
| `/api/v1/users/{id}` | GET | User detail | JSON object | Single fake user |
| `/debug/errors` | GET | Error log | HTML stack trace | Fake Python traceback |
| `/config.php` | GET | Config file | Plain text (fake) | PHP app mimic |
| `/robots.txt` | GET | Robots file | Plain text | Standard file |

### 4.3 Implementation Outline

```python
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.routes.utils import log_request_to_db

router = APIRouter(prefix="/", tags=["honeypots"])

@router.get("/")
async def homepage(request: Request, session: AsyncSession = Depends(get_session)):
    """Fake homepage."""
    # Log is handled by middleware
    return {
        "html": "<h1>Welcome to DECEPTRA</h1><p>A secure infrastructure platform.</p>"
    }

@router.get("/admin")
async def admin_panel(request: Request, session: AsyncSession = Depends(get_session)):
    """Fake admin login panel."""
    return {
        "html": "<form method='POST' action='/login'><input name='user'><input type='password' name='pass'></form>"
    }

@router.post("/login")
async def login_handler(request: Request, session: AsyncSession = Depends(get_session)):
    """Fake login POST handler."""
    body = await request.json() if request.headers.get("content-type") == "application/json" else await request.form()
    # Log captured credentials (sanitized)
    return {"status": "error", "message": "Invalid credentials"}, 401

@router.get("/.env")
async def leaked_env(request: Request, session: AsyncSession = Depends(get_session)):
    """Fake leaked environment file."""
    env_content = """
DATABASE_URL=postgres://admin:password123@db.internal:5432/prod
API_KEY=sk-1234567890abcdef
SECRET=my-super-secret-key
AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
"""
    return {"content": env_content}

@router.get("/api/v1/users")
async def fake_users(request: Request, session: AsyncSession = Depends(get_session)):
    """Fake user API list."""
    return {
        "users": [
            {"id": 1, "username": "admin", "email": "admin@internal.local", "role": "admin"},
            {"id": 2, "username": "developer", "email": "dev@internal.local", "role": "user"},
        ]
    }

@router.get("/debug/errors")
async def fake_errors(request: Request, session: AsyncSession = Depends(get_session)):
    """Fake error/stacktrace page."""
    traceback_html = """
    <html><body><pre>
Traceback (most recent call last):
  File "/app/main.py", line 42, in process_payment
    response = db.query(Order).filter(...).first()
  File "/sqlalchemy/orm/query.py", line 1234, in first
    return self.limit(1).all()[0]
KeyError: list index out of range
    </pre></body></html>
    """
    return {"html": traceback_html}

# Additional endpoints: /.config.php, /robots.txt, etc. (similar pattern)
```

---

## 5. Request Logging Middleware

### 5.1 `app/main.py` - Middleware Setup

**Responsibility**: Log every request/response.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
from app.routes.utils import log_request_to_db

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Read request body (if present)
        request_body = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                request_body = (await request.body()).decode()[:10000]
            except:
                pass
        
        # Call the route handler
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log to database (async)
        # This will be picked up by background task or immediate write
        await log_request_to_db(
            ip=request.client.host,
            method=request.method,
            path=request.url.path,
            query_string=str(request.url.query),
            headers=dict(request.headers),
            body=request_body,
            status=response.status_code,
            duration_ms=duration_ms,
            session=request.app.state.db_session
        )
        
        return response

async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    from app.core.database import init_db
    await init_db()
    yield

app = FastAPI(title="DECEPTRA", lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)

# Register routers
from app.routes.honeypots import router as honeypot_router
from app.routes.api_decoys import router as api_router
app.include_router(honeypot_router)
app.include_router(api_router, prefix="/api")

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0"}
```

---

## 6. API Routes (`app/routes/api_decoys.py`)

### 6.1 Purpose
Expose recorded honeypot data and decoy asset management to dashboard + AI layer.

### 6.2 Endpoints

#### GET `/api/attacks` - List Sessions

```python
@router.get("/attacks")
async def list_attacks(
    session: AsyncSession = Depends(get_session),
    limit: int = 100,
    offset: int = 0,
):
    """List all honeypot sessions with summary."""
    stmt = select(Session).order_by(Session.last_request_at.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    sessions = result.scalars().all()
    
    return {
        "attacks": [
            {
                "id": str(s.id),
                "ip_address": s.ip_address,
                "first_request_at": s.first_request_at.isoformat(),
                "request_count": s.request_count,
                "is_automated": s.is_automated,
                "tags": s.tags or "",
            }
            for s in sessions
        ]
    }
```

#### GET `/api/attacks/{session_id}` - Session Detail

```python
@router.get("/attacks/{session_id}")
async def get_attack_detail(
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get full request chain for a session."""
    stmt = select(Session).where(Session.id == UUID(session_id))
    result = await session.execute(stmt)
    sess = result.scalar_one_or_none()
    
    if not sess:
        return {"error": "Session not found"}, 404
    
    return {
        "session": {
            "id": str(sess.id),
            "ip_address": sess.ip_address,
            "first_request_at": sess.first_request_at.isoformat(),
            "last_request_at": sess.last_request_at.isoformat(),
            "request_count": sess.request_count,
        },
        "requests": [
            {
                "id": str(r.id),
                "method": r.method,
                "path": r.path,
                "status": r.response_status,
                "timestamp": r.timestamp.isoformat(),
                "is_trap_hit": r.is_trap_hit,
            }
            for r in sess.requests
        ]
    }
```

#### POST `/api/decoys` - Create/Update Decoy Asset

```python
@router.post("/decoys")
async def create_decoy(
    payload: DecoyAssetSchema,
    session: AsyncSession = Depends(get_session),
):
    """Create or update a decoy asset."""
    existing = await session.execute(
        select(DecoyAsset).where(DecoyAsset.name == payload.name)
    )
    decoy = existing.scalar_one_or_none()
    
    if not decoy:
        decoy = DecoyAsset(**payload.dict(exclude_unset=True))
        session.add(decoy)
    else:
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(decoy, key, value)
    
    await session.commit()
    return {"id": str(decoy.id), "name": decoy.name}
```

---

## 7. Decoy Asset Manager (`app/decoys/asset_manager.py`)

### 7.1 Purpose
Registry and lookup of decoy definitions; used by honeypot routes to generate responses.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.models import DecoyAsset

class DecoyAssetManager:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_asset(self, name: str) -> DecoyAsset:
        """Retrieve a decoy asset by name."""
        stmt = select(DecoyAsset).where(DecoyAsset.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_active(self) -> list[DecoyAsset]:
        """List all active decoy assets."""
        stmt = select(DecoyAsset).where(DecoyAsset.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def register_asset(self, name: str, asset_type: str, **kwargs) -> DecoyAsset:
        """Create a new decoy asset."""
        asset = DecoyAsset(name=name, asset_type=asset_type, **kwargs)
        self.session.add(asset)
        await self.session.commit()
        return asset
```

---

## 8. Jinja2 Templates (`templates/`)

### 8.1 Decoy HTML Templates

#### `admin.html` - Fake Admin Panel

```html
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - DECEPTRA</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .login-box { 
            width: 300px; margin: 100px auto; 
            background: white; padding: 20px; 
            border-radius: 5px; box-shadow: 0 0 10px #ccc;
        }
        input { width: 100%; padding: 8px; margin: 5px 0; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>Admin Login</h1>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
```

#### `error.html` - Fake Error Page

```html
<!DOCTYPE html>
<html>
<head>
    <title>Application Error</title>
    <style>
        body { font-family: monospace; background: #1e1e1e; color: #ff6b6b; padding: 20px; }
        .error-box { background: #2d2d2d; padding: 15px; border: 1px solid #ff6b6b; }
    </style>
</head>
<body>
    <div class="error-box">
        <h2>500 Internal Server Error</h2>
        <pre>
Traceback (most recent call last):
  File "/app/services/payment.py", line 89, in process_transaction
    db.commit()
  File "/sqlalchemy/engine.py", line 234, in commit
    raise DatabaseError("Connection lost to primary database")
DatabaseError: Connection lost to primary database
        </pre>
    </div>
</body>
</html>
```

---

## 9. Request/Response Logging Utils (`app/routes/utils.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.models import Session, Request
from datetime import datetime
import json
from uuid import uuid4

async def log_request_to_db(
    ip: str,
    method: str,
    path: str,
    query_string: str,
    headers: dict,
    body: str,
    status: int,
    duration_ms: int,
    session: AsyncSession,
):
    """Log an HTTP request to the database."""
    
    # Find or create session by IP
    stmt = select(Session).where(
        Session.ip_address == ip
    ).order_by(Session.last_request_at.desc()).limit(1)
    
    result = await session.execute(stmt)
    sess = result.scalar_one_or_none()
    
    if not sess:
        sess = Session(
            ip_address=ip,
            user_agent=headers.get("user-agent", ""),
            request_count=1,
        )
        session.add(sess)
    else:
        sess.request_count += 1
        sess.last_request_at = datetime.utcnow()
    
    # Create request record
    req = Request(
        session_id=sess.id if sess.id else uuid4(),
        method=method,
        path=path,
        query_string=query_string[:1000] if query_string else None,
        headers_json=json.dumps(sanitize_headers(headers)),
        body=body[:10000] if body else None,
        response_status=status,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow(),
    )
    
    session.add(req)
    await session.commit()

def sanitize_headers(headers: dict) -> dict:
    """Remove sensitive header values before logging."""
    sensitive_keys = {"authorization", "cookie", "x-api-key"}
    return {
        k: "***REDACTED***" if k.lower() in sensitive_keys else v
        for k, v in headers.items()
    }
```

---

## 10. Implementation Sequence

### Phase 1: Core Setup (Days 1-2)
1. Create `app/core/settings.py` → Load configuration
2. Create `app/core/database.py` → SQLAlchemy async setup
3. Create `app/core/models.py` → Define all ORM models
4. Create `app/core/base.py` → Pydantic schemas
5. Create `app/main.py` → FastAPI app + middleware

### Phase 2: Honeypot Routes (Days 3-5)
6. Create `app/routes/honeypots.py` → All decoy endpoints
7. Create `app/routes/utils.py` → Request logging utility
8. Test each honeypot endpoint locally

### Phase 3: API & Dashboard Routes (Days 6-7)
9. Create `app/routes/api_decoys.py` → GET /api/attacks, POST /api/decoys
10. Create `app/decoys/asset_manager.py` → Decoy registry

### Phase 4: Templates & Integration (Day 8)
11. Create Jinja2 templates in `templates/`
12. Wire templates into honeypot routes
13. End-to-end testing: request → log → API retrieval

### Phase 5: Testing & Documentation (Day 9)
14. Write minimal test suite (request logging, session creation)
15. Document all new endpoints
16. Verify no breaks to existing code

---

## 11. Testing Strategy

### 11.1 Minimal Test Suite

```python
# tests/test_backend.py

import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_admin_honeypot():
    """Test admin endpoint returns HTML form."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/admin")
        assert response.status_code == 200
        assert "form" in response.text

@pytest.mark.asyncio
async def test_login_post():
    """Test login POST accepts credentials."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/login", json={"username": "admin", "password": "test"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_request_logging():
    """Test that requests are logged to database."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.get("/admin")
        # Query DB to confirm request was logged
        # (requires DB setup in test fixture)
```

---

## 12. API Contract (Stable)

### 12.1 Session Summary Response

```json
{
  "attacks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "ip_address": "192.168.1.100",
      "first_request_at": "2026-04-26T10:00:00",
      "request_count": 5,
      "is_automated": true,
      "tags": "scanner,web-crawler"
    }
  ]
}
```

### 12.2 Session Detail Response

```json
{
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "ip_address": "192.168.1.100",
    "first_request_at": "2026-04-26T10:00:00",
    "request_count": 5
  },
  "requests": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "method": "GET",
      "path": "/admin",
      "status": 200,
      "timestamp": "2026-04-26T10:00:01",
      "is_trap_hit": false
    }
  ]
}
```

---

## 13. Dependencies

### `requirements.txt`
```
fastapi==0.95.0
uvicorn==0.21.0
sqlalchemy==2.0.0
aiosqlite==0.17.0
pydantic==2.0.0
pydantic-settings==2.0.0
jinja2==3.1.2
httpx==0.24.0
```

---

## 14. Notes for Implementation AI

### 14.1 Key Constraints
- **Never edit `app/ai/`** or `app/analyzer/` logic
- **Stick to async patterns** (FastAPI + SQLAlchemy async)
- **Log everything** but keep payloads < 10KB
- **Idiomatic FastAPI**: Pydantic for validation, dependency injection, structured responses

### 14.2 Integration Points
- AI layer will call `POST /api/decoys` to create new decoy assets
- AI layer will query `GET /api/attacks` + `GET /api/attacks/{session_id}` to analyze sessions
- Analyzer layer will be called for session scoring/tagging (not implemented here)

### 14.3 Future Enhancements (Out of Scope)
- Rate limiting / DDoS protection
- WebSocket live feeds for real-time honeypot activity
- Advanced bot detection (can add to `is_automated` heuristic)
- Multi-database support

---

## 15. Success Criteria

✅ All endpoints respond without errors  
✅ Every request is logged to DB  
✅ GET /api/attacks returns paginated session list  
✅ GET /api/attacks/{id} returns full request chain  
✅ POST /api/decoys creates/updates decoy assets  
✅ Honeypot routes return realistic responses  
✅ No destructive actions performed  
✅ Middleware logs request/response duration  
✅ All code follows Pydantic + FastAPI idioms  
✅ README updated with setup/run instructions  

---

## 16. Handoff Checklist

**For implementing AI agent**:
- [ ] Read Global.txt for architecture constraints
- [ ] Create `app/core/` modules (settings, database, models, base)
- [ ] Create `app/main.py` with middleware
- [ ] Create `app/routes/honeypots.py` with decoy endpoints
- [ ] Create `app/routes/utils.py` logging utility
- [ ] Create `app/routes/api_decoys.py` API endpoints
- [ ] Create `app/decoys/asset_manager.py` registry
- [ ] Create Jinja2 templates in `templates/`
- [ ] Write minimal test suite
- [ ] Test locally: request → logged → API retrieval
- [ ] Verify no conflicts with existing code
- [ ] Document new endpoints in README
- [ ] Commit with atomic messages per module

---

**Plan created**: 2026-04-26  
**Role**: Backend / Core Honeypot Engineer  
**Scope**: Role 1 Backend Only  
**Ready for**: AI Agent Implementation
