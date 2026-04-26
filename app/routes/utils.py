"""Request logging utilities with database persistence."""

import json
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.models import Session, Request


def sanitize_headers(headers: dict) -> dict:
    """
    Remove sensitive header values before logging.
    
    Redacts Authorization, Cookie, X-API-Key, and similar sensitive headers.
    """
    sensitive_keys = {"authorization", "cookie", "x-api-key", "x-api-token", "x-secret", "proxy-authorization"}
    return {
        k: "***REDACTED***" if k.lower() in sensitive_keys else v
        for k, v in headers.items()
    }


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
) -> None:
    """
    Log an HTTP request to the database.
    
    Groups requests by IP address into sessions.
    Creates a new session if none exists for this IP, or updates the latest one.
    
    Args:
        ip: Client IP address
        method: HTTP method (GET, POST, etc.)
        path: Request path
        query_string: Query string (if present)
        headers: HTTP headers dict
        body: Request body (truncated if >10KB)
        status: HTTP response status code
        duration_ms: Request processing duration in milliseconds
        session: SQLAlchemy async session
    """
    try:
        # Find or create session by IP
        stmt = select(Session).where(
            Session.ip_address == ip
        ).order_by(Session.last_request_at.desc()).limit(1)
        
        result = await session.execute(stmt)
        sess = result.scalar_one_or_none()
        
        if not sess:
            # New session
            sess = Session(
                id=uuid4(),
                ip_address=ip,
                user_agent=headers.get("user-agent", "")[:500],
                request_count=1,
                first_request_at=datetime.utcnow(),
                last_request_at=datetime.utcnow(),
            )
            session.add(sess)
            await session.flush()  # Get the ID before creating request
        else:
            # Update existing session
            sess.request_count += 1
            sess.last_request_at = datetime.utcnow()
        
        # Create request record
        req = Request(
            id=uuid4(),
            session_id=sess.id,
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
    except Exception as e:
        # Log error but don't crash the request handler
        print(f"Error logging request: {e}")
        await session.rollback()
