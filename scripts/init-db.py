"""
Test database connection and initialize schema
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models import Base
from app.models.user import User
from app.models.student import Student
from app.models.parent import Parent, ParentConsent
from app.models.counselor import Counselor
from app.models.assessment import Assessment
from app.models.conversation import Conversation, Message
from app.models.voice_analysis import VoiceAnalysis


def test_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    print(f"   Database URL: {settings.DATABASE_URL[:50]}...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"   PostgreSQL version: {version[:50]}...")
        return engine
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def init_database(engine):
    """Create all tables"""
    print("\n📦 Creating database tables...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Show created tables
        print("\n📋 Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"   - {table_name}")
        
        return True
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("AI4Mind - Database Initialization")
    print("=" * 60)
    
    # Test connection
    engine = test_connection()
    if not engine:
        sys.exit(1)
    
    # Initialize database
    success = init_database(engine)
    if not success:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Database initialization completed!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Run seed data: python scripts/seed-data.py")
    print("   2. Start AI service: cd ai-service && python -m app.main")
    print("   3. Test API: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
