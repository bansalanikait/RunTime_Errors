"""Spider trap definitions and utilities."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.models import Trap, Request

async def register_spider_trap(db_session: AsyncSession, path_pattern: str, description: str = None) -> Trap:
    """
    Registers a new spider trap.
    """
    stmt = select(Trap).where(Trap.path_pattern == path_pattern)
    result = await db_session.execute(stmt)
    trap = result.scalar_one_or_none()
    
    if not trap:
        trap = Trap(path_pattern=path_pattern, description=description or "Auto-registered spider trap")
        db_session.add(trap)
        await db_session.commit()
        await db_session.refresh(trap)
        
    return trap

async def record_spider_hit(db_session: AsyncSession, request_id: str) -> bool:
    """
    Records that a specific request hit a spider trap.
    """
    stmt = select(Request).where(Request.id == request_id)
    result = await db_session.execute(stmt)
    req = result.scalar_one_or_none()
    
    if req:
        req.is_trap_hit = True
        await db_session.commit()
        return True
    return False

async def get_all_traps(db_session: AsyncSession) -> list[Trap]:
    """
    Retrieves all registered spider traps.
    """
    stmt = select(Trap)
    result = await db_session.execute(stmt)
    return result.scalars().all()
