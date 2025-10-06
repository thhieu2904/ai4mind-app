"""
Debug script to check counselor user in database
"""
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.user import User
from app.core.security import verify_password

def check_user():
    db = next(get_db())
    
    email = "counselor1@ai4mind.com"
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print(f"❌ User {email} NOT FOUND in database")
        print("\n📌 Bạn cần chạy SQL script: database/create_counselors.sql trên Supabase")
        return
    
    print(f"✅ User found:")
    print(f"  - ID: {user.id}")
    print(f"  - Email: {user.email}")
    print(f"  - Full Name: {user.full_name}")
    print(f"  - Role: {user.role}")
    print(f"  - Is Active: {user.is_active}")
    print(f"  - Is Verified: {user.is_verified}")
    print(f"  - Hashed Password (first 30 chars): {user.hashed_password[:30]}...")
    print(f"  - Hash length: {len(user.hashed_password)} chars")
    
    # Test password verification
    test_password = "Counselor123!"
    print(f"\n🔐 Testing password: {test_password}")
    
    try:
        is_valid = verify_password(test_password, user.hashed_password)
        if is_valid:
            print(f"✅ Password CORRECT!")
        else:
            print(f"❌ Password INCORRECT!")
            print(f"\n💡 Có thể bạn đã tạo user với password khác.")
            print(f"   Hoặc hash bị lỗi khi tạo trên Supabase.")
    except Exception as e:
        print(f"❌ Error verifying password: {e}")
        print(f"\n💡 Hash có thể bị lỗi. Expected 60 chars, got {len(user.hashed_password)}")
    
    db.close()

if __name__ == "__main__":
    check_user()
