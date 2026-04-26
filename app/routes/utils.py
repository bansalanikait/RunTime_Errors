"""Request logging utilities with database persistence."""

import json
import logging
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.models import Session, Request

logger = logging.getLogger(__name__)


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
    is_trap_hit: bool = False,
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
        print(f"\n🟡 LOG_REQUEST called for {ip} {method} {path}")
        logger.info(f"[LOG_REQUEST] Starting log for {ip} {method} {path}")
        
        # Find or create session by IP
        stmt = select(Session).where(
            Session.ip_address == ip
        ).order_by(Session.last_request_at.desc()).limit(1)
        
        result = await session.execute(stmt)
        sess = result.scalar_one_or_none()
        logger.info(f"[LOG_REQUEST] Found existing session: {sess is not None}")
        
        if not sess:
            # New session
            logger.info(f"[LOG_REQUEST] Creating new session for IP {ip}")
            sess = Session(
                id=str(uuid4()),
                ip_address=ip,
                user_agent=headers.get("user-agent", "")[:500],
                request_count=1,
                first_request_at=datetime.utcnow(),
                last_request_at=datetime.utcnow(),
            )
            session.add(sess)
            await session.flush()  # Get the ID before creating request
            logger.info(f"[LOG_REQUEST] Created new session: {sess.id}")
        else:
            # Update existing session
            logger.info(f"[LOG_REQUEST] Updating existing session: {sess.id}")
            sess.request_count += 1
            sess.last_request_at = datetime.utcnow()
        
        # Create request record
        req = Request(
            id=str(uuid4()),
            session_id=sess.id,
            method=method,
            path=path,
            query_string=query_string[:1000] if query_string else None,
            headers_json=json.dumps(sanitize_headers(headers)),
            body=body[:10000] if body else None,
            response_status=status,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow(),
            is_trap_hit=is_trap_hit,
        )
        
        session.add(req)
        await session.flush()
        logger.info(f"[LOG_REQUEST] Created request record: {req.id}")
        
        # Analyze session to update risk score and tags
        stmt_reqs = select(Request).where(Request.session_id == sess.id)
        result_reqs = await session.execute(stmt_reqs)
        all_reqs = result_reqs.scalars().all()
        
        from app.analyzer.rules import analyze_session
        risk_score, tags, is_automated = analyze_session(all_reqs)
        
        sess.tags = ",".join(tags)[:200] if tags else None
        sess.is_automated = is_automated
        
        await session.commit()
        logger.info(f"[LOG_REQUEST] Committed to database successfully")
    except Exception as e:
        # Log error but don't crash the request handler
        logger.error(f"[LOG_REQUEST] Error logging request: {e}", exc_info=True)
        await session.rollback()
