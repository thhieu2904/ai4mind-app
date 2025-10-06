"""
Test nhiều password variations để tìm đúng password
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash từ database (counselor1@ai4mind.com)
db_hash = "$2b$12$Yb1B.9BEy61lLeIPvKlra.FaLxIiur88UVuciYYRESYXGnaxv8LR."

# Test nhiều variations
test_passwords = [
    "Counselor123!",      # Expected
    "counselor123!",      # lowercase
    "COUNSELOR123!",      # uppercase
    "Counselor123",       # no exclamation
    "counselor1",         # simple
    "password",           # generic
    "123456",             # numeric
]

print("="*70)
print("TESTING PASSWORD VARIATIONS")
print("="*70)
print(f"Hash from DB: {db_hash}")
print(f"Hash length: {len(db_hash)}")
print("="*70)

for pwd in test_passwords:
    try:
        is_valid = pwd_context.verify(pwd, db_hash)
        status = "✅ MATCH!" if is_valid else "❌ No match"
        print(f"{status:15} | {pwd}")
        if is_valid:
            print("\n" + "="*70)
            print(f"🎉 FOUND IT! Correct password is: {pwd}")
            print("="*70)
            break
    except Exception as e:
        print(f"❌ Error        | {pwd} - {e}")

print("\n💡 Tip: Nếu không có password nào đúng, có thể:")
print("   1. Hash trong DB bị sai → Cần update lại")
print("   2. Password khi tạo user khác với expected")
