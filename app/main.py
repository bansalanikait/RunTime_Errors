"""FastAPI application initialization and middleware setup."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import time
import json
import logging

logger = logging.getLogger(__name__)

from app.core.settings import settings
from app.core.database import init_db, close_db
from app.routes.utils import log_request_to_db
from app.routes import honeypots, api_decoys, api_signatures
from app.routes import dashboard as dashboard_routes


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every HTTP request/response to the database.
    
    Captures:
    - Client IP
    - HTTP method and path
    - Query string
    - Headers (sanitized)
    - Request body (truncated if >10KB)
    - Response status code
    - Processing duration
    
    Runs for all requests, including honeypot endpoints and API calls.
    """
    
    def __init__(self, app):
        super().__init__(app)
        print("\n[INFO] RequestLoggingMiddleware initialized!")

    async def dispatch(self, request: Request, call_next):
        print(f"\n[REQUEST] MIDDLEWARE CALLED: {request.method} {request.url.path}")
        start_time = time.time()
        logger.info(f"[MIDDLEWARE] Intercepting {request.method} {request.url.path}")

        # Capture request body (only for POST/PUT/PATCH)
        request_body = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                request_body = body_bytes.decode("utf-8", errors="ignore")
                logger.info(f"[MIDDLEWARE] Captured body: {len(request_body)} bytes")
            except Exception as e:
                logger.error(f"[MIDDLEWARE] Failed to read body: {e}", exc_info=True)

            # Create a new receive callable to allow body re-reading by handlers
            async def receive():
                return {"type": "http.request", "body": body_bytes}

            request._receive = receive

        # Call the route handler
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Log to database (non-blocking)
        try:
            logger.info(f"[MIDDLEWARE] Logging {request.method} {request.url.path} (status={response.status_code})")
            
            # Get a session for logging
            from app.core.database import async_session_maker

            async with async_session_maker() as session:
                is_trap_hit = getattr(request.state, "is_trap_hit", False)
                await log_request_to_db(
                    ip=request.client.host if request.client else "unknown",
                    method=request.method,
                    path=request.url.path,
                    query_string=str(request.url.query),
                    headers=dict(request.headers),
                    body=request_body,
                    status=response.status_code,
                    duration_ms=duration_ms,
                    session=session,
                    is_trap_hit=is_trap_hit,
                )
            logger.info(f"[MIDDLEWARE] Successfully logged request")
        except Exception as e:
            logger.error(f"[MIDDLEWARE] Error logging request: {e}", exc_info=True)

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: startup and shutdown.
    
    Startup:
    - Initialize database (create tables)
    
    Shutdown:
    - Close database connections
    """
    print(f"[*] Starting {settings.app_name} v{settings.app_version}...")
    await init_db()
    print("[OK] Database initialized")
    
    from app.core.database import async_session_maker
    from app.decoys.spider_traps import register_spider_trap
    from app.core.models import ThreatSignature
    from sqlalchemy.future import select
    from app.analyzer.rules import load_signatures_from_db
    
    async with async_session_maker() as session:
        await register_spider_trap(session, "/hidden/admin-portal", "Default admin portal trap")
        await register_spider_trap(session, "/robots-bait", "Default robots.txt bait trap")
        
        # Load dynamic threat signatures
        result = await session.execute(select(ThreatSignature).where(ThreatSignature.is_active == True))
        signatures = result.scalars().all()
        load_signatures_from_db(signatures)
        print(f"[OK] Loaded {len(signatures)} dynamic threat signatures")
        
    print("[OK] Default spider traps registered")
    
    yield
    
    print("[SHUTDOWN] Shutting down...")
    await close_db()
    print("[OK] Database closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Modular honeypot framework for attack detection and analysis",
    lifespan=lifespan,
)

# Add request logging middleware (runs for all requests)
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, assets)
app.mount("/static", StaticFiles(directory=str(settings.base_path / "static")), name="static")

# Register routers
app.include_router(api_decoys.router)
app.include_router(api_signatures.router)
app.include_router(dashboard_routes.router)
app.include_router(honeypots.router)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirects to OpenAPI docs."""
    return {"message": f"Welcome to {settings.app_name}. See /docs for API documentation."}


# OpenAPI configuration
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    """Return OpenAPI schema."""
    from fastapi.openapi.utils import get_openapi
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
