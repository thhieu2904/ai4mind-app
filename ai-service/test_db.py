"""
Test Supabase Database Connection
Run: python test_db.py
"""
from sqlalchemy import create_engine, text

print("="*60)
print("TESTING SUPABASE DATABASE CONNECTIONS")
print("="*60)

# Test 1: Direct Connection
print("\n[1/2] Testing Direct Connection (IPv6)...")
print("URL: postgresql://postgres:***@db.kfltaylgkxyogsfsvcdt.supabase.co:5432")
try:
    engine = create_engine(
        "postgresql://postgres:AI4Mind2025%40@db.kfltaylgkxyogsfsvcdt.supabase.co:5432/postgres",
        pool_pre_ping=True
    )
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print("✅ SUCCESS!")
        print(f"   PostgreSQL Version: {version[:50]}...")
except Exception as e:
    print(f"❌ FAILED!")
    print(f"   Error: {str(e)[:100]}")

# Test 2: Session Pooler Connection
print("\n[2/2] Testing Session Pooler (IPv4)...")
print("URL: postgresql://postgres.PROJECT_REF:***@aws-0-ap-southeast-1.pooler...")
try:
    engine = create_engine(
        "postgresql://postgres.kfltaylgkxyogsfsvcdt:AI4Mind2025%40@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres",
        pool_pre_ping=True
    )
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print("✅ SUCCESS!")
        print(f"   PostgreSQL Version: {version[:50]}...")
except Exception as e:
    print(f"❌ FAILED!")
    print(f"   Error: {str(e)[:100]}")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
print("- At Home (LAN): Use Direct Connection (faster)")
print("- At Office (WiFi): Use Session Pooler (works with firewall)")
print("="*60)
