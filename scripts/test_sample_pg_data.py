# scripts/test_sample_data.py
"""
Script to test inserting and querying sample data.
Run with: doppler run -- python scripts/test_sample_data.py
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def main():
    print("🧪 Testing sample data insertion...")
    print("=" * 40)

    try:
        from emby_recommendation_engine.shared.database import session_scope
        from emby_recommendation_engine.shared.models import User, MediaItem

        with session_scope() as db:
            # Create a test user
            print("📝 Creating test user...")
            user = User(emby_user_id="test_user_123", username="test_user")
            db.add(user)
            db.flush()  # Get the ID
            print(f"✅ User created with ID: {user.id}")

            # Create test media items
            print("📝 Creating test media items...")

            movie = MediaItem(
                emby_item_id="movie_456",
                name="The Matrix",
                type="Movie",
                tmdb_id=603,
                production_year=1999,
                runtime_minutes=136,
                genres=["Action", "Sci-Fi"],
                overview="A computer programmer discovers reality is a simulation.",
            )
            db.add(movie)

            episode = MediaItem(
                emby_item_id="episode_789",
                name="Breaking Bad - Pilot",
                type="Episode",
                tmdb_id=1396,
                production_year=2008,
                runtime_minutes=58,
                genres=["Drama", "Crime"],
                overview="High school chemistry teacher starts cooking meth.",
            )
            db.add(episode)

            db.flush()
            print(f"✅ Movie created with ID: {movie.id}")
            print(f"✅ Episode created with ID: {episode.id}")

        # Query the data back
        print("\n🔍 Querying data back...")
        with session_scope() as db:
            users = db.query(User).all()
            media_items = db.query(MediaItem).all()

            print(f"📊 Found {len(users)} users:")
            for user in users:
                print(f"   - {user.username} (Emby ID: {user.emby_user_id})")

            print(f"📊 Found {len(media_items)} media items:")
            for item in media_items:
                print(f"   - {item.name} ({item.type}, {item.production_year})")
                print(f"     Genres: {item.genres}")
                print(f"     TMDB ID: {item.tmdb_id}")

        print("\n🎉 Sample data test completed successfully!")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        print(f"   Full traceback:\n{traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit(main())
