"""
Generate bcrypt hash for counselor passwords
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_hash(password: str) -> str:
    """Generate bcrypt hash for a password"""
    return pwd_context.hash(password)

if __name__ == "__main__":
    # Tạo password hash cho 3 counselors
    passwords = {
        "counselor1@ai4mind.com": "Counselor123!",
        "counselor2@ai4mind.com": "Counselor123!",
        "counselor3@ai4mind.com": "Counselor123!",
    }
    
    print("=" * 80)
    print("BCRYPT PASSWORD HASHES")
    print("=" * 80)
    
    for email, password in passwords.items():
        hashed = generate_hash(password)
        print(f"\n{email}")
        print(f"Password: {password}")
        print(f"Hash: {hashed}")
        print("-" * 80)
    
    print("\n✅ Copy các hash này vào SQL script của bạn")
