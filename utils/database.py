"""
Database utilities and connection management for Arabic VoC platform
"""

import os
import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/voc_db")

# Convert to async URL if needed
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with proper configuration
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(FeedbackBase.metadata.create_all)
            await conn.run_sync(AnalyticsBase.metadata.create_all)
            
            # Create indexes for better performance
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_feedback_created_at_channel 
                ON feedback(created_at, channel);
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_feedback_sentiment_status 
                ON feedback(sentiment_score, status);
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_feedback_customer_email 
                ON feedback(customer_email) WHERE customer_email IS NOT NULL;
            """))
            
            # Create full-text search index for Arabic content
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_feedback_content_gin 
                ON feedback USING gin(to_tsvector('arabic', content));
            """))
            
            logger.info("Database tables and indexes created successfully")
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

@asynccontextmanager
async def get_db_session():
    """Get database session with proper cleanup"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()

async def execute_raw_query(query: str, params: dict = None):
    """Execute raw SQL query"""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text(query), params or {})
            await session.commit()
            return result
        except Exception as e:
            await session.rollback()
            logger.error(f"Error executing raw query: {str(e)}")
            raise

async def check_db_health():
    """Check database connection health"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

async def get_table_stats():
    """Get statistics about database tables"""
    try:
        async with AsyncSessionLocal() as session:
            # Get feedback table stats
            feedback_stats = await session.execute(text("""
                SELECT 
                    COUNT(*) as total_feedback,
                    COUNT(CASE WHEN status = 'PROCESSED' THEN 1 END) as processed,
                    COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending,
                    AVG(sentiment_score) as avg_sentiment
                FROM feedback
            """))
            
            # Get channel distribution
            channel_stats = await session.execute(text("""
                SELECT channel, COUNT(*) as count
                FROM feedback
                GROUP BY channel
                ORDER BY count DESC
            """))
            
            stats = feedback_stats.fetchone()
            channels = channel_stats.fetchall()
            
            return {
                "feedback": {
                    "total": stats[0] or 0,
                    "processed": stats[1] or 0,
                    "pending": stats[2] or 0,
                    "average_sentiment": float(stats[3] or 0)
                },
                "channels": [{"name": ch[0], "count": ch[1]} for ch in channels]
            }
            
    except Exception as e:
        logger.error(f"Error getting table stats: {str(e)}")
        return {"error": str(e)}

async def cleanup_old_data(days_old: int = 365):
    """Clean up old feedback data"""
    try:
        async with AsyncSessionLocal() as session:
            # Delete feedback older than specified days
            result = await session.execute(text("""
                DELETE FROM feedback 
                WHERE created_at < NOW() - INTERVAL ':days days'
                AND status = 'ARCHIVED'
            """), {"days": days_old})
            
            deleted_count = result.rowcount
            await session.commit()
            
            logger.info(f"Cleaned up {deleted_count} old feedback records")
            return {"deleted_records": deleted_count}
            
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")
        await session.rollback()
        raise

# Database dependency for FastAPI
async def get_db():
    """FastAPI dependency for database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database dependency error: {str(e)}")
            raise
        finally:
            await session.close()

# Alternative dependency using context manager  
def get_db_session_dep():
    """Alternative database session dependency"""
    return get_db()
