# scripts/verify_tables.py
"""
Script to verify where tables were created and what database we're connected to.
Run with: doppler run -- python scripts/verify_tables.py
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def main():
    print("🔍 Verifying table creation...")
    print("=" * 50)
    
    try:
        from emby_recommendation_engine.shared.database import db_manager
        from sqlalchemy import text
        
        # Initialize database manager
        db_manager.initialize()
        print("✅ Database manager initialized")
        
        with db_manager.session_scope() as session:
            # Check what database we're connected to
            current_db = session.execute(text("SELECT current_database()")).scalar()
            print(f"📍 Connected to database: {current_db}")
            
            # Check what user we're connected as
            current_user = session.execute(text("SELECT current_user")).scalar()
            print(f"👤 Connected as user: {current_user}")
            
            # List all tables in the public schema
            result = session.execute(text("""
                SELECT schemaname, tablename, tableowner 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)).fetchall()
            
            print(f"\n📊 Tables in database '{current_db}':")
            if result:
                for schema, table, owner in result:
                    print(f"   ✅ {schema}.{table} (owner: {owner})")
            else:
                print("   ❌ No tables found in public schema")
            
            # Check if our specific tables exist
            our_tables = ['users', 'media_items']
            print(f"\n🎯 Checking for our tables:")
            for table_name in our_tables:
                exists = session.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table_name}'
                    )
                """)).scalar()
                
                if exists:
                    print(f"   ✅ {table_name} - EXISTS")
                    
                    # Show column info
                    columns = session.execute(text(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table_name}'
                        ORDER BY ordinal_position
                    """)).fetchall()
                    
                    print(f"      Columns:")
                    for col_name, col_type, nullable in columns:
                        print(f"        - {col_name}: {col_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
                else:
                    print(f"   ❌ {table_name} - NOT FOUND")
            
            # Show connection details for pgAdmin setup
            connection_info = db_manager.get_connection_info()
            print(f"\n🔧 Connection details for pgAdmin:")
            print(f"   Host: localhost (or postgres if internal)")
            print(f"   Port: 5432")
            print(f"   Database: {current_db}")
            print(f"   Username: {current_user}")
            print(f"   Active connections: {connection_info.get('active_connections', 'unknown')}")
            
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"   Full traceback:\n{traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    exit(main())
