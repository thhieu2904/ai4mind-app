"""
Test password verification với hash từ database
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash đã generate cho counselor1
correct_hash = "$2b$12$Yb1B.9BEy61lLeIPvKlra.FaLxIiur88UVuciYYRESYXGnaxv8LR."
test_password = "Counselor123!"

print("Testing password verification...")
print(f"Password: {test_password}")
print(f"Hash length: {len(correct_hash)} chars (should be 60)")
print(f"Hash prefix: {correct_hash[:15]}")

try:
    is_valid = pwd_context.verify(test_password, correct_hash)
    if is_valid:
        print("\n✅ Password verification SUCCESS!")
        print("   This hash is CORRECT for password: Counselor123!")
    else:
        print("\n❌ Password verification FAILED!")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
print("📌 Copy hash này vào Supabase SQL script:")
print(f"   {correct_hash}")
print("="*60)
