"""
Seed test data for development
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.parent import Parent, ParentConsent
from app.models.counselor import Counselor


def seed_users(session):
    """Create test users"""
    print("\n👥 Creating test users...")
    
    users_data = [
        {
            "email": "student1@example.com",
            "password": "password123",
            "full_name": "Nguyễn Văn A",
            "role": UserRole.STUDENT
        },
        {
            "email": "student2@example.com",
            "password": "password123",
            "full_name": "Trần Thị B",
            "role": UserRole.STUDENT
        },
        {
            "email": "parent1@example.com",
            "password": "password123",
            "full_name": "Nguyễn Văn Cha",
            "role": UserRole.PARENT
        },
        {
            "email": "counselor1@example.com",
            "password": "password123",
            "full_name": "Dr. Phạm Văn Tâm",
            "role": UserRole.COUNSELOR
        },
        {
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "Admin User",
            "role": UserRole.ADMIN
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user = User(
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            is_active=True,
            is_verified=True
        )
        session.add(user)
        created_users.append(user)
        print(f"   ✅ Created user: {user.email} ({user.role})")
    
    session.commit()
    return created_users


def seed_profiles(session, users):
    """Create extended profiles"""
    print("\n📝 Creating user profiles...")
    
    # Find users by role
    students = [u for u in users if u.role == UserRole.STUDENT]
    parents = [u for u in users if u.role == UserRole.PARENT]
    counselors = [u for u in users if u.role == UserRole.COUNSELOR]
    
    # Create student profiles
    for idx, user in enumerate(students, 1):
        student = Student(
            user_id=user.id,
            student_code=f"SV{2024000 + idx}",
            date_of_birth=date(2003, 1, 15),
            phone_number="0901234567",
            university="Đại học Công nghệ Thông tin",
            major="Khoa học máy tính",
            year_of_study=3
        )
        session.add(student)
        print(f"   ✅ Created student profile: {student.student_code}")
    
    # Create parent profiles
    for user in parents:
        parent = Parent(
            user_id=user.id,
            phone_number="0912345678",
            occupation="Giáo viên"
        )
        session.add(parent)
        print(f"   ✅ Created parent profile for: {user.full_name}")
    
    # Create counselor profiles
    for user in counselors:
        counselor = Counselor(
            user_id=user.id,
            license_number="PSY2024001",
            specialization="Tâm lý học lâm sàng",
            years_of_experience=5,
            phone_number="0923456789",
            is_available=True
        )
        session.add(counselor)
        print(f"   ✅ Created counselor profile for: {user.full_name}")
    
    session.commit()


def seed_parent_consents(session):
    """Create parent consent relationships"""
    print("\n🤝 Creating parent-student relationships...")
    
    # Get first student and parent
    student = session.query(Student).first()
    parent = session.query(Parent).first()
    
    if student and parent:
        consent = ParentConsent(
            student_id=student.id,
            parent_id=parent.id,
            is_approved=1  # Approved
        )
        session.add(consent)
        session.commit()
        print(f"   ✅ Created parent consent (approved)")


def main():
    """Main function"""
    print("=" * 60)
    print("AI4Mind - Seed Test Data")
    print("=" * 60)
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Seed data
        users = seed_users(session)
        seed_profiles(session, users)
        seed_parent_consents(session)
        
        print("\n" + "=" * 60)
        print("✅ Test data seeded successfully!")
        print("=" * 60)
        print("\n📧 Test accounts:")
        print("   Student: student1@example.com / password123")
        print("   Parent: parent1@example.com / password123")
        print("   Counselor: counselor1@example.com / password123")
        print("   Admin: admin@example.com / admin123")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
