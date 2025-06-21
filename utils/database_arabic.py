"""
Arabic-optimized database utilities for PostgreSQL
Handles Arabic collation, full-text search, and UTF-8 optimization
"""

import asyncpg
import logging
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ArabicDatabaseManager:
    """Manager for Arabic-optimized PostgreSQL operations"""
    
    def __init__(self, database_url: str):
        # Convert psycopg2 URL to asyncpg for async support
        if database_url and "postgresql://" in database_url:
            self.database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            self.database_url = database_url
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database with Arabic optimization"""
        # Create async engine with Arabic-friendly settings
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            poolclass=NullPool,
            connect_args={
                "command_timeout": 60,
                "server_settings": {
                    "application_name": "arabic_voc_platform",
                    "timezone": "UTC",
                }
            }
        )
        
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        await self._setup_arabic_configuration()
    
    async def _setup_arabic_configuration(self):
        """Setup Arabic-specific database configuration"""
        async with self.engine.begin() as conn:
            try:
                # Create Arabic text search configuration
                await conn.execute(text("""
                    CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS arabic_config (COPY = simple);
                """))
                
                # Create function for Arabic text normalization
                await conn.execute(text("""
                    CREATE OR REPLACE FUNCTION normalize_arabic_text(input_text text)
                    RETURNS text AS $$
                    BEGIN
                        -- Remove diacritics and normalize Arabic text
                        RETURN regexp_replace(
                            regexp_replace(input_text, '[ًٌٍَُِّْ]', '', 'g'),
                            '[ٱآإأؤئةىي]', 
                            CASE 
                                WHEN substring(input_text from '[ٱآ]') IS NOT NULL THEN 'ا'
                                WHEN substring(input_text from '[إأ]') IS NOT NULL THEN 'ا'
                                WHEN substring(input_text from 'ؤ') IS NOT NULL THEN 'و'
                                WHEN substring(input_text from 'ئ') IS NOT NULL THEN 'ي'
                                WHEN substring(input_text from 'ة') IS NOT NULL THEN 'ه'
                                WHEN substring(input_text from 'ى') IS NOT NULL THEN 'ي'
                                ELSE input_text
                            END,
                            'g'
                        );
                    END;
                    $$ LANGUAGE plpgsql IMMUTABLE;
                """))
                
                # Create Arabic full-text search function
                await conn.execute(text("""
                    CREATE OR REPLACE FUNCTION arabic_to_tsvector(input_text text)
                    RETURNS tsvector AS $$
                    BEGIN
                        RETURN arabic_search_vector(input_text);
                    END;
                    $$ LANGUAGE plpgsql IMMUTABLE;
                """))
                
                # Create Arabic similarity function
                await conn.execute(text("""
                    CREATE OR REPLACE FUNCTION arabic_similarity(text1 text, text2 text)
                    RETURNS float AS $$
                    BEGIN
                        RETURN similarity(normalize_arabic_text(text1), normalize_arabic_text(text2));
                    END;
                    $$ LANGUAGE plpgsql IMMUTABLE;
                """))
                
                logger.info("Arabic database configuration completed successfully")
                
            except Exception as e:
                logger.error(f"Error setting up Arabic configuration: {e}")
                # Continue without Arabic-specific features if setup fails
    
    async def create_arabic_indexes(self):
        """Create optimized indexes for Arabic content"""
        async with self.engine.begin() as conn:
            try:
                # Full-text search indexes for Arabic content
                indexes = [
                    # Users table
                    "CREATE INDEX IF NOT EXISTS idx_users_arabic_names ON users USING gin(arabic_to_tsvector(coalesce(first_name_ar, '') || ' ' || coalesce(last_name_ar, '')))",
                    
                    # Organizations table
                    "CREATE INDEX IF NOT EXISTS idx_organizations_arabic_name ON organizations USING gin(arabic_to_tsvector(coalesce(name_ar, '')))",
                    
                    # Surveys table
                    "CREATE INDEX IF NOT EXISTS idx_surveys_arabic_content ON surveys USING gin(arabic_to_tsvector(coalesce(title_ar, '') || ' ' || coalesce(description_ar, '')))",
                    
                    # Questions table
                    "CREATE INDEX IF NOT EXISTS idx_questions_arabic_text ON questions USING gin(arabic_to_tsvector(coalesce(text_ar, '')))",
                    
                    # Responses table - JSONB indexes for Arabic content
                    "CREATE INDEX IF NOT EXISTS idx_responses_answers_gin ON responses USING gin(answers)",
                    "CREATE INDEX IF NOT EXISTS idx_responses_keywords_gin ON responses USING gin(keywords)",
                    
                    # Question responses
                    "CREATE INDEX IF NOT EXISTS idx_question_responses_arabic_text ON question_responses USING gin(arabic_to_tsvector(coalesce(answer_text, '')))",
                    
                    # Feedback table (from existing model)
                    "CREATE INDEX IF NOT EXISTS idx_feedback_arabic_content ON feedback USING gin(arabic_to_tsvector(content))",
                ]
                
                for index_sql in indexes:
                    await conn.execute(text(index_sql))
                
                logger.info("Arabic indexes created successfully")
                
            except Exception as e:
                logger.error(f"Error creating Arabic indexes: {e}")
    
    async def search_arabic_content(self, query: str, table: str, fields: List[str], limit: int = 50) -> List[Dict]:
        """Search Arabic content using full-text search"""
        async with self.session_factory() as session:
            try:
                # Normalize search query
                normalized_query = f"arabic_to_tsvector('{query}')"
                
                # Build search SQL based on table and fields
                if table == "users":
                    sql = f"""
                        SELECT id, username, email, first_name, last_name, first_name_ar, last_name_ar,
                               ts_rank(arabic_to_tsvector(coalesce(first_name_ar, '') || ' ' || coalesce(last_name_ar, '')), {normalized_query}) as rank
                        FROM users 
                        WHERE arabic_to_tsvector(coalesce(first_name_ar, '') || ' ' || coalesce(last_name_ar, '')) @@ {normalized_query}
                        ORDER BY rank DESC
                        LIMIT {limit}
                    """
                elif table == "surveys":
                    sql = f"""
                        SELECT id, title, title_ar, description, description_ar,
                               ts_rank(arabic_to_tsvector(coalesce(title_ar, '') || ' ' || coalesce(description_ar, '')), {normalized_query}) as rank
                        FROM surveys 
                        WHERE arabic_to_tsvector(coalesce(title_ar, '') || ' ' || coalesce(description_ar, '')) @@ {normalized_query}
                        ORDER BY rank DESC
                        LIMIT {limit}
                    """
                elif table == "feedback":
                    sql = f"""
                        SELECT id, content, channel, sentiment_score, created_at,
                               ts_rank(arabic_to_tsvector(content), {normalized_query}) as rank
                        FROM feedback 
                        WHERE arabic_to_tsvector(content) @@ {normalized_query}
                        ORDER BY rank DESC
                        LIMIT {limit}
                    """
                else:
                    raise ValueError(f"Unsupported table: {table}")
                
                result = await session.execute(text(sql))
                return [dict(row._mapping) for row in result.fetchall()]
                
            except Exception as e:
                logger.error(f"Error searching Arabic content: {e}")
                return []
    
    async def get_arabic_analytics(self) -> Dict[str, Any]:
        """Get analytics specific to Arabic content"""
        async with self.session_factory() as session:
            try:
                analytics = {}
                
                # Arabic content statistics
                result = await session.execute(text("""
                    SELECT 
                        COUNT(*) FILTER (WHERE first_name_ar IS NOT NULL OR last_name_ar IS NOT NULL) as users_with_arabic_names,
                        COUNT(*) as total_users
                    FROM users
                """))
                user_stats = result.fetchone()
                analytics["users"] = {
                    "total": user_stats.total_users,
                    "with_arabic_names": user_stats.users_with_arabic_names,
                    "arabic_percentage": (user_stats.users_with_arabic_names / max(user_stats.total_users, 1)) * 100
                }
                
                # Survey language statistics
                result = await session.execute(text("""
                    SELECT 
                        primary_language,
                        COUNT(*) as count
                    FROM surveys
                    GROUP BY primary_language
                """))
                survey_languages = result.fetchall()
                analytics["surveys_by_language"] = {row.primary_language: row.count for row in survey_languages}
                
                # Response language statistics
                result = await session.execute(text("""
                    SELECT 
                        language_used,
                        COUNT(*) as count,
                        AVG(sentiment_score) as avg_sentiment
                    FROM responses
                    WHERE sentiment_score IS NOT NULL
                    GROUP BY language_used
                """))
                response_languages = result.fetchall()
                analytics["responses_by_language"] = {
                    row.language_used: {
                        "count": row.count,
                        "avg_sentiment": float(row.avg_sentiment) if row.avg_sentiment else 0
                    } for row in response_languages
                }
                
                # Arabic content quality metrics
                result = await session.execute(text("""
                    SELECT 
                        AVG(length(content)) as avg_content_length,
                        COUNT(*) FILTER (WHERE content ~ '[ء-ي]') as arabic_feedback_count,
                        COUNT(*) as total_feedback
                    FROM feedback
                """))
                content_stats = result.fetchone()
                analytics["content_quality"] = {
                    "avg_content_length": float(content_stats.avg_content_length) if content_stats.avg_content_length else 0,
                    "arabic_feedback_count": content_stats.arabic_feedback_count,
                    "total_feedback": content_stats.total_feedback
                }
                
                return analytics
                
            except Exception as e:
                logger.error(f"Error getting Arabic analytics: {e}")
                return {}
    
    async def optimize_arabic_queries(self):
        """Optimize database for Arabic query performance"""
        async with self.engine.begin() as conn:
            try:
                # Update statistics for better query planning
                await conn.execute(text("ANALYZE users, organizations, surveys, questions, responses, feedback"))
                
                # Vacuum indexes for better performance
                await conn.execute(text("VACUUM ANALYZE"))
                
                logger.info("Arabic query optimization completed")
                
            except Exception as e:
                logger.error(f"Error optimizing Arabic queries: {e}")
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()

# Global database manager instance
arabic_db_manager = ArabicDatabaseManager(os.environ.get("DATABASE_URL", ""))

async def init_arabic_database():
    """Initialize Arabic-optimized database"""
    await arabic_db_manager.initialize()
    await arabic_db_manager.create_arabic_indexes()
    return arabic_db_manager

async def get_arabic_db_session():
    """Get database session with Arabic optimization"""
    if not arabic_db_manager.session_factory:
        await init_arabic_database()
    
    async with arabic_db_manager.session_factory() as session:
        yield session