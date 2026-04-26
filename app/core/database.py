"""Database initialization and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.settings import settings
from app.core.models import Base

# Convert sqlite:/// to sqlite+aiosqlite:/// for async support
DATABASE_URL = settings.database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,  # Log SQL statements in debug mode
    pool_pre_ping=True,   # Verify connection before use
    connect_args={"check_same_thread": False},  # SQLite limitation
    poolclass=StaticPool,  # Use StaticPool for SQLite
)

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db():
    """
    Initialize database: create all tables from SQLAlchemy models.
    
    Call this during application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    """
    Dependency for FastAPI routes: provides AsyncSession.
    
    Usage in routes:
        async def my_route(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db():
    """
    Close database engine and connection pool.
    
    Call this during application shutdown.
    """
    await engine.dispose()
