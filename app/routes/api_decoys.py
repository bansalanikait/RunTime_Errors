"""API routes for dashboard and AI layer: session retrieval and decoy management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_session
from app.core.models import Session, DecoyAsset
from app.core.base import (
    AttacksListResponse,
    AttackDetailResponse,
    DecoyAssetCreateResponse,
    DecoyAssetSchema,
    SessionSummarySchema,
    RequestInfoSchema,
)

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Always returns 200 OK.
    """
    return {"status": "ok", "version": "1.0.0"}


@router.get("/attacks")
async def list_attacks(
    session: AsyncSession = Depends(get_session),
    limit: int = 100,
    offset: int = 0,
) -> AttacksListResponse:
    """
    List all honeypot sessions.
    
    Returns paginated list of attacker sessions with summary fields.
    Ordered by most recent activity first.
    
    **FROZEN CONTRACT**: Do not change response shape.
    
    Query Parameters:
    - limit: Max results (default 100)
    - offset: Pagination offset (default 0)
    
    Response: AttacksListResponse
    """
    # Get total count
    count_stmt = select(func.count(Session.id))
    count_result = await session.execute(count_stmt)
    total = count_result.scalar() or 0
    
    # Get paginated results
    stmt = (
        select(Session)
        .order_by(Session.last_request_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    sessions = result.scalars().all()
    
    attacks = [SessionSummarySchema.from_orm(s) for s in sessions]
    
    return AttacksListResponse(
        attacks=attacks,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/attacks/{session_id}")
async def get_attack_detail(
    session_id: str,
    session: AsyncSession = Depends(get_session),
) -> AttackDetailResponse:
    """
    Get full request chain for a session.
    
    Returns session metadata + all HTTP requests in that session.
    
    **FROZEN CONTRACT**: Do not change response shape.
    
    Path Parameters:
    - session_id: UUID string of session
    
    Response: AttackDetailResponse
    """
    # Query by string ID (DB stores as String(36), not UUID)
    stmt = select(Session).where(Session.id == session_id)
    result = await session.execute(stmt)
    sess = result.scalar_one_or_none()
    
    if not sess:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    sess_summary = SessionSummarySchema.from_orm(sess)
    requests = [RequestInfoSchema.from_orm(r) for r in sess.requests]
    
    return AttackDetailResponse(session=sess_summary, requests=requests)


@router.post("/decoys")
async def create_decoy(
    payload: DecoyAssetSchema,
    session: AsyncSession = Depends(get_session),
) -> DecoyAssetCreateResponse:
    """
    Create or update a decoy asset.
    
    Used by AI layer to define new decoy endpoints/files.
    If decoy with same name exists, it is updated.
    
    **FROZEN CONTRACT**: Do not change response shape.
    
    Request Body: DecoyAssetSchema
    
    Response: DecoyAssetCreateResponse
    """
    # Check if decoy already exists
    existing_stmt = select(DecoyAsset).where(DecoyAsset.name == payload.name)
    existing_result = await session.execute(existing_stmt)
    existing_decoy = existing_result.scalar_one_or_none()
    
    if existing_decoy:
        # Update existing
        for key, value in payload.dict(exclude_unset=True).items():
            if hasattr(existing_decoy, key):
                setattr(existing_decoy, key, value)
        decoy = existing_decoy
    else:
        # Create new
        decoy = DecoyAsset(**payload.dict())
        session.add(decoy)
    
    await session.commit()
    
    return DecoyAssetCreateResponse(
        id=decoy.id,
        name=decoy.name,
        asset_type=decoy.asset_type,
        path=decoy.path,
        is_active=decoy.is_active,
    )


@router.get("/decoys")
async def list_decoys(
    session: AsyncSession = Depends(get_session),
    active_only: bool = True,
) -> list[DecoyAssetSchema]:
    """
    List all decoy assets.
    
    Query Parameters:
    - active_only: Only return active decoys (default True)
    
    Response: List of DecoyAssetSchema
    """
    if active_only:
        stmt = select(DecoyAsset).where(DecoyAsset.is_active == True)
    else:
        stmt = select(DecoyAsset)
    
    result = await session.execute(stmt)
    decoys = result.scalars().all()
    
    return [DecoyAssetSchema.from_orm(d) for d in decoys]


@router.get("/decoys/{decoy_id}")
async def get_decoy(
    decoy_id: str,
    session: AsyncSession = Depends(get_session),
) -> DecoyAssetSchema:
    """
    Get a single decoy asset by ID.
    
    Path Parameters:
    - decoy_id: UUID of decoy
    
    Response: DecoyAssetSchema
    """
    try:
        decoy_uuid = UUID(decoy_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid decoy_id format")
    
    stmt = select(DecoyAsset).where(DecoyAsset.id == decoy_uuid)
    result = await session.execute(stmt)
    decoy = result.scalar_one_or_none()
    
    if not decoy:
        raise HTTPException(status_code=404, detail=f"Decoy {decoy_id} not found")
    
    return DecoyAssetSchema.from_orm(decoy)
