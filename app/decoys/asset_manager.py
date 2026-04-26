"""Decoy asset management and registry."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.models import DecoyAsset


class DecoyAssetManager:
    """
    Registry and lookup for decoy assets.
    
    Used by honeypot routes to retrieve decoy definitions and generate responses.
    """

    def __init__(self, session: AsyncSession):
        """Initialize manager with database session."""
        self.session = session

    async def get_asset(self, name: str) -> DecoyAsset:
        """
        Retrieve a decoy asset by name.
        
        Args:
            name: Unique decoy name
            
        Returns:
            DecoyAsset or None if not found
        """
        stmt = select(DecoyAsset).where(DecoyAsset.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(self) -> list[DecoyAsset]:
        """
        List all active decoy assets.
        
        Returns:
            List of active DecoyAsset objects
        """
        stmt = select(DecoyAsset).where(DecoyAsset.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_type(self, asset_type: str) -> list[DecoyAsset]:
        """
        List decoy assets by type.
        
        Args:
            asset_type: Asset type (endpoint, file, credential, api)
            
        Returns:
            List of DecoyAsset objects
        """
        stmt = select(DecoyAsset).where(DecoyAsset.asset_type == asset_type)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def register_asset(self, **kwargs) -> DecoyAsset:
        """
        Create a new decoy asset.
        
        Args:
            **kwargs: DecoyAsset field values
            
        Returns:
            Created DecoyAsset object
        """
        asset = DecoyAsset(**kwargs)
        self.session.add(asset)
        await self.session.commit()
        return asset

    async def deactivate_asset(self, name: str) -> bool:
        """
        Deactivate a decoy asset by name.
        
        Args:
            name: Decoy name
            
        Returns:
            True if found and deactivated, False if not found
        """
        asset = await self.get_asset(name)
        if asset:
            asset.is_active = False
            await self.session.commit()
            return True
        return False
