"""API routes for managing dynamic threat signatures."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
import re
import logging

from app.core.database import get_db
from app.core.models import ThreatSignature
from app.analyzer.rules import load_signatures_from_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/signatures", tags=["Threat Signatures"])

# Pydantic Schemas
class ThreatSignatureCreate(BaseModel):
    name: str
    pattern: str
    target: str = "payload" # payload, path, header
    threat_tag: str
    is_active: bool = True

class ThreatSignatureUpdate(BaseModel):
    name: Optional[str] = None
    pattern: Optional[str] = None
    target: Optional[str] = None
    threat_tag: Optional[str] = None
    is_active: Optional[bool] = None

class ThreatSignatureResponse(BaseModel):
    id: str
    name: str
    pattern: str
    target: str
    threat_tag: str
    is_active: bool

    class Config:
        from_attributes = True

async def refresh_analyzer_cache(db: AsyncSession):
    """Helper to reload active signatures into the analyzer's memory cache."""
    result = await db.execute(select(ThreatSignature).where(ThreatSignature.is_active == True))
    active_sigs = result.scalars().all()
    load_signatures_from_db(active_sigs)

@router.get("", response_model=List[ThreatSignatureResponse])
async def get_signatures(db: AsyncSession = Depends(get_db)):
    """Retrieve all dynamic threat signatures."""
    result = await db.execute(select(ThreatSignature))
    return result.scalars().all()

@router.post("", response_model=ThreatSignatureResponse, status_code=status.HTTP_201_CREATED)
async def create_signature(signature: ThreatSignatureCreate, db: AsyncSession = Depends(get_db)):
    """Create a new dynamic threat signature."""
    # Validate regex pattern
    try:
        re.compile(signature.pattern)
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Invalid regex pattern: {e}")

    # Check for existing name
    result = await db.execute(select(ThreatSignature).where(ThreatSignature.name == signature.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Signature with this name already exists")

    new_sig = ThreatSignature(
        name=signature.name,
        pattern=signature.pattern,
        target=signature.target,
        threat_tag=signature.threat_tag,
        is_active=signature.is_active
    )
    db.add(new_sig)
    await db.commit()
    await db.refresh(new_sig)

    # Refresh analyzer cache
    await refresh_analyzer_cache(db)

    return new_sig

@router.delete("/{sig_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_signature(sig_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a dynamic threat signature."""
    result = await db.execute(select(ThreatSignature).where(ThreatSignature.id == sig_id))
    sig = result.scalars().first()
    if not sig:
        raise HTTPException(status_code=404, detail="Signature not found")
    
    await db.delete(sig)
    await db.commit()

    # Refresh analyzer cache
    await refresh_analyzer_cache(db)
    
    return None
