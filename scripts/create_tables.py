"""
Simple script to create database tables.
Run with: doppler run -- python scripts/create_tables.py
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def main():
    print("Creating database tables...")

    try:
        from emby_recommendation_engine.shared.models.create_tables import create_tables

        if create_tables():
            print("🎉 Tables created successfully!")
        else:
            print("❌ Failed to create tables")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
