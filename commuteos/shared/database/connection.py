"""
Async database connection management using SQLAlchemy.
"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from typing import AsyncGenerator
from ..config.settings import get_settings
from ..utils.logger import get_logger


logger = get_logger(__name__)
Base = declarative_base()


class DatabaseManager:
    """Manage async database connections with connection pooling."""
    
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker | None = None
        self.settings = get_settings()
    
    async def connect(self):
        """Initialize database connection with connection pooling."""
        if self.engine is not None:
            logger.info("Database already connected")
            return
        
        logger.info("Initializing database connection", 
                   host=self.settings.DB_HOST, 
                   database=self.settings.DB_NAME)
        
        self.engine = create_async_engine(
            self.settings.database_url,
            echo=self.settings.DEBUG,
            poolclass=QueuePool,
            pool_size=self.settings.DB_POOL_SIZE,
            max_overflow=self.settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
        )
        
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        logger.info("Database connection initialized successfully")
    
    async def disconnect(self):
        """Close database connection."""
        if self.engine is not None:
            logger.info("Closing database connection")
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        if self.session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error("Database session error", error=str(e))
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all tables in the database."""
        if self.engine is None:
            raise RuntimeError("Database not connected")
        
        logger.info("Creating database tables")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions in FastAPI."""
    async for session in db_manager.get_session():
        yield session
