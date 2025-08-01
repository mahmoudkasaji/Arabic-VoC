"""
Consolidated Database Utilities
Combines functionality from database.py and database_arabic.py
"""

import os
import logging
from contextlib import asynccontextmanager
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Unified database management with Arabic optimization"""
    
    def __init__(self):
        self.database_url = self._prepare_database_url()
        self.engine = None
        self.session_factory = None
    
    def _prepare_database_url(self) -> str:
        """Prepare database URL for async operations"""
        url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/voc_db")
        
        # Convert to async URL if needed
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Clean SSL parameters that asyncpg doesn't support
        import re
        ssl_params = ['sslmode', 'sslcert', 'sslkey', 'sslrootcert']
        for param in ssl_params:
            url = re.sub(rf'[?&]{param}=[^&]*', '', url)
        
        # Clean up trailing separators
        url = re.sub(r'[?&]$', '', url)
        return url
    
    async def initialize(self):
        """Initialize database with optimizations"""
        self.engine = create_async_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=os.getenv("DEBUG", "false").lower() == "true"
        )
        
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        await self._setup_optimizations()
    
    async def _setup_optimizations(self):
        """Setup database optimizations including Arabic support"""
        async with self.engine.begin() as conn:
            try:
                # Create indexes for better performance
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_feedback_created_at_channel ON feedback(created_at, channel);",
                    "CREATE INDEX IF NOT EXISTS idx_feedback_sentiment_status ON feedback(sentiment_score, status);",
                    "CREATE INDEX IF NOT EXISTS idx_feedback_customer_email ON feedback(customer_email) WHERE customer_email IS NOT NULL;",
                    "CREATE INDEX IF NOT EXISTS idx_feedback_content_gin ON feedback USING gin(to_tsvector('arabic', content));"
                ]
                
                for index_sql in indexes:
                    await conn.execute(text(index_sql))
                
                # Create Arabic text search configuration
                await conn.execute(text("""
                    CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS arabic_config (COPY = simple);
                """))
                
                logger.info("Database optimizations applied successfully")
                
            except Exception as e:
                logger.error(f"Error setting up database optimizations: {e}")
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with proper cleanup"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

# Singleton instance
database_manager = DatabaseManager()