"""
Database configuration and connection management for Emby Recommendation Engine.
Handles PostgreSQL connections with SQLAlchemy ORM using modern psycopg driver.
"""

import os
import logging
from typing import Generator, Optional, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, event, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from attrs import define, field

logger = logging.getLogger(__name__)

# Create the declarative base for all models
Base = declarative_base()


@define
class DatabaseManager:
    """Manages database connections and sessions."""

    engine: Optional[Engine] = field(default=None, init=False)
    SessionLocal: Optional[sessionmaker] = field(default=None, init=False)
    _initialized: bool = field(default=False, init=False)

    def initialize(self):
        """Initialize database connection and engine."""
        if self._initialized:
            return

        # Get database configuration from environment
        db_config = self._get_db_config()

        # Create SQLAlchemy engine with modern psycopg
        self.engine = create_engine(
            db_config["url"],
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections every hour
            echo=db_config["echo"],  # Log SQL queries if enabled
            # Modern psycopg optimizations
            connect_args={
                "options": "-c timezone=utc -c application_name=emby_recommendation_engine"
            },
            # Connection pool settings optimized for psycopg
            pool_timeout=30,
            pool_reset_on_return="commit",
        )

        # Add connection event listeners for logging
        event.listen(self.engine, "connect", self._on_connect)
        event.listen(self.engine, "checkout", self._on_checkout)

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        self._initialized = True
        logger.info("Database manager initialized successfully with psycopg")

    def _get_db_config(self) -> Dict[str, Any]:
        """Get database configuration from environment variables."""
        # Required environment variables
        required_vars = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                "Please ensure these are set (via Doppler or environment)."
            )

        # Build database URL - psycopg uses postgresql:// (same as psycopg2)
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB")

        # Use postgresql+psycopg:// scheme to explicitly use psycopg (not psycopg2)
        url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"

        return {"url": url, "echo": os.getenv("DB_ECHO", "false").lower() == "true"}

    def _on_connect(self, dbapi_connection, connection_record):
        """Called when a new database connection is created."""
        logger.debug("New database connection established")

        # Set up any connection-specific settings for psycopg
        with dbapi_connection.cursor() as cursor:
            # Enable UUID extension if not exists
            cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            dbapi_connection.commit()

    def _on_checkout(self, dbapi_connection, connection_record, connection_proxy):
        """Called when a connection is retrieved from the pool."""
        logger.debug("Database connection checked out from pool")

    def get_session(self) -> Session:
        """Get a new database session."""
        if not self._initialized:
            self.initialize()
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        Use this for operations that need guaranteed commit/rollback behavior.
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self):
        """Create all tables defined in models."""
        if not self._initialized:
            self.initialize()

        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def drop_tables(self):
        """Drop all tables. Use with caution!"""
        if not self._initialized:
            self.initialize()

        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("All tables dropped")

    def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            with self.session_scope() as session:
                result = session.execute(text("SELECT 1")).scalar()
                return result == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about the current database connection."""
        if not self._initialized:
            return {"status": "not_initialized"}

        try:
            with self.session_scope() as session:
                version_result = session.execute(text("SELECT version()")).scalar()
                connection_count = session.execute(
                    text(
                        "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
                    )
                ).scalar()

                return {
                    "status": "connected",
                    "postgresql_version": version_result,
                    "active_connections": connection_count,
                    "pool_size": self.engine.pool.size(),
                    "checked_out_connections": self.engine.pool.checkedout(),
                }
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"status": "error", "error": str(e)}


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions for FastAPI dependency injection
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get database session.
    Use this in your route functions with Depends(get_db).
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def get_db_session() -> Session:
    """
    Get a database session for use outside of FastAPI routes.
    Remember to close the session when done.
    """
    return db_manager.get_session()


# Context manager alias for convenience
session_scope = db_manager.session_scope

# Export commonly used items
__all__ = [
    "Base",
    "DatabaseManager",
    "db_manager",
    "get_db",
    "get_db_session",
    "session_scope",
]
