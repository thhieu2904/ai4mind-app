"""
Quick script to list available users for testing
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai-service')))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.student import Student

def list_users():
    """List all users with their roles"""
    db = SessionLocal()
    
    try:
        users = db.query(User).filter(User.is_active == True).all()
        
        print("\n" + "=" * 70)
        print("  AVAILABLE TEST ACCOUNTS")
        print("=" * 70)
        
        if not users:
            print("\n❌ No users found in database!")
            print("\nCreate a test user first:")
            print("  1. Go to http://localhost:8000/docs")
            print("  2. Use POST /api/v1/auth/register endpoint")
            print("  3. Or register via frontend: http://localhost:5173/register")
            return
        
        print(f"\nFound {len(users)} active users:\n")
        
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Name: {user.full_name}")
            
            # Check if student has profile
            if user.role == "student":
                student = db.query(Student).filter(Student.user_id == user.id).first()
                if student:
                    print(f"   ✓ Student profile exists (ID: {student.id})")
                else:
                    print(f"   ❌ No student profile (cannot use for AI chat)")
            
            print()
        
        print("-" * 70)
        print("\n💡 Tip: Use a STUDENT account for AI Chat testing")
        print("   Update TEST_EMAIL and TEST_PASSWORD in test-ai-chat-api.py")
        print("\n" + "=" * 70)
        
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
