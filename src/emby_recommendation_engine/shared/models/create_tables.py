"""
Script to create the database tables.
Run with: doppler run -- python -m emby_recommendation_engine.shared.models.create_tables
"""

import sys
from pathlib import Path

# Add src to path if running directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from emby_recommendation_engine.shared.database import db_manager, Base
from emby_recommendation_engine.shared.models import User, MediaItem
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables."""
    try:
        # Initialize database manager
        db_manager.initialize()
        logger.info("Database manager initialized")

        # Create all tables
        Base.metadata.create_all(bind=db_manager.engine)
        logger.info("✅ Database tables created successfully")

        # Show what was created
        logger.info("Created tables:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False


def drop_tables():
    """Drop all tables. Use with caution!"""
    try:
        db_manager.initialize()
        Base.metadata.drop_all(bind=db_manager.engine)
        logger.info("✅ All tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage database tables")
    parser.add_argument("--drop", action="store_true", help="Drop all tables")
    args = parser.parse_args()

    if args.drop:
        print("⚠️  Are you sure you want to drop all tables? This will delete all data!")
        confirm = input("Type 'yes' to confirm: ")
        if confirm.lower() == "yes":
            drop_tables()
        else:
            print("Operation cancelled")
    else:
        create_tables()
