"""FastAPI application initialization and middleware setup."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import time
import json

from app.core.settings import settings
from app.core.database import init_db, close_db
from app.routes.utils import log_request_to_db
from app.routes import honeypots, api_decoys
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

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Capture request body (only for POST/PUT/PATCH)
        request_body = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                request_body = body_bytes.decode("utf-8", errors="ignore")
            except Exception:
                pass

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
            # Get a session for logging
            from app.core.database import async_session_maker

            async with async_session_maker() as session:
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
                )
        except Exception as e:
            print(f"Error in request logging middleware: {e}")

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
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}...")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    print("🛑 Shutting down...")
    await close_db()
    print("✅ Database closed")


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

# Register routers
app.include_router(honeypots.router)
app.include_router(api_decoys.router)
app.include_router(dashboard_routes.router)

# Mount static files (CSS, JS, assets)
app.mount("/static", StaticFiles(directory=str(settings.base_path / "static")), name="static")


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
