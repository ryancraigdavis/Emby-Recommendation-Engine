# scripts/test_database.py - Enhanced database connection test script
"""
Test script to verify database connection works with modern psycopg driver.
Run with: doppler run -- python scripts/test_database.py
"""
import sys
from pathlib import Path
import logging

# Add src to path - go up one level from scripts/ to project root, then into src/
project_root = Path(__file__).parent.parent  # Go up from scripts/ to project root
sys.path.insert(0, str(project_root / "src"))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_environment_variables():
    """Test that all required environment variables are present."""
    print("Testing environment variables...")
    
    import os
    required_vars = ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Make sure to run with Doppler: doppler run -- python scripts/test_database.py")
        return False
    
    print("✅ All required environment variables found")
    
    # Show what we're connecting to (without password)
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    user = os.getenv('POSTGRES_USER')
    database = os.getenv('POSTGRES_DB')
    
    print(f"   → Host: {host}:{port}")
    print(f"   → Database: {database}")
    print(f"   → User: {user}")
    
    return True

def test_database_manager_initialization():
    """Test database manager initialization."""
    print("\nTesting database manager initialization...")
    
    try:
        from emby_recommendation_engine.shared.database import db_manager
        
        # Initialize database manager
        db_manager.initialize()
        print("✅ Database manager initialized successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Check that your Python path is correct and modules exist")
        return False
    except Exception as e:
        print(f"❌ Database manager initialization failed: {e}")
        return False

def test_basic_connection():
    """Test basic database connection and health check."""
    print("\nTesting basic database connection...")
    
    try:
        from emby_recommendation_engine.shared.database import db_manager
        
        # Test health check
        if db_manager.health_check():
            print("✅ Database health check passed")
            return True
        else:
            print("❌ Database health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_session_operations():
    """Test session creation and basic operations."""
    print("\nTesting database sessions...")
    
    try:
        from emby_recommendation_engine.shared.database import session_scope, get_db_session
        from sqlalchemy import text
        
        # Test context manager session
        with session_scope() as db:
            version_result = db.execute(text("SELECT version()")).scalar()
            print(f"✅ PostgreSQL version: {version_result.split(',')[0]}")  # Just first part
            
            # Test UUID extension
            uuid_result = db.execute(text("SELECT gen_random_uuid()")).scalar()
            print(f"✅ UUID generation works: {str(uuid_result)[:8]}...")
            
        # Test standalone session
        session = get_db_session()
        try:
            current_db = session.execute(text("SELECT current_database()")).scalar()
            print(f"✅ Connected to database: {current_db}")
        finally:
            session.close()
            
        return True
        
    except Exception as e:
        print(f"❌ Session operations test failed: {e}")
        return False

def test_connection_info():
    """Test the new connection info method."""
    print("\nTesting connection information...")
    
    try:
        from emby_recommendation_engine.shared.database import db_manager
        
        info = db_manager.get_connection_info()
        
        if info.get("status") == "connected":
            print("✅ Connection info retrieved successfully:")
            print(f"   → Status: {info['status']}")
            print(f"   → Active connections: {info['active_connections']}")
            print(f"   → Pool size: {info['pool_size']}")
            print(f"   → Checked out: {info['checked_out_connections']}")
            return True
        else:
            print(f"❌ Connection info failed: {info}")
            return False
            
    except Exception as e:
        print(f"❌ Connection info test failed: {e}")
        return False

def test_table_operations():
    """Test table creation and dropping (safe test)."""
    print("\nTesting table operations...")
    
    try:
        from emby_recommendation_engine.shared.database import db_manager, Base, session_scope
        from sqlalchemy import Column, Integer, String, Table, text
        
        # Create a temporary test table
        test_table = Table(
            'test_connection_table',
            Base.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50)),
            extend_existing=True
        )
        
        # Create the test table
        test_table.create(db_manager.engine, checkfirst=True)
        print("✅ Test table created successfully")
        
        # Test inserting data
        with session_scope() as db:
            db.execute(
                test_table.insert().values(id=1, name="test_connection")
            )
            
            # Query the data back
            result = db.execute(
                test_table.select().where(test_table.c.id == 1)
            ).fetchone()
            
            if result and result.name == "test_connection":
                print("✅ Data insertion and retrieval works")
            else:
                print("❌ Data operations failed")
                return False
        
        # Clean up - drop the test table
        test_table.drop(db_manager.engine, checkfirst=True)
        print("✅ Test table cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Table operations test failed: {e}")
        return False

def main():
    """Run all database tests."""
    print("Emby Recommendation Engine - Enhanced Database Test")
    print("=" * 55)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Database Manager Init", test_database_manager_initialization), 
        ("Basic Connection", test_basic_connection),
        ("Session Operations", test_session_operations),
        ("Connection Info", test_connection_info),
        ("Table Operations", test_table_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except KeyboardInterrupt:
            print(f"\n⚠️  Test interrupted by user")
            return 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n{'='*55}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All database tests passed! Your setup is working perfectly.")
        print("\nNext steps:")
        print("- Your database connection is working with modern psycopg")
        print("- You can now add your data models")
        print("- Ready to create tables for your recommendation engine")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
