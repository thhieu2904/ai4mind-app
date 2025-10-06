# Test Database Connection

## Test 1: Direct Connection (để verify password)

```bash
# Temporary test - sẽ fail nếu ở công ty do IPv6
DATABASE_URL=postgresql://postgres:AI4Mind2025%40@db.kfltaylgkxyogsfsvcdt.supabase.co:5432/postgres
```

## Test 2: Session Pooler (IPv4, recommended)

```bash
# Should work everywhere
DATABASE_URL=postgresql://postgres.kfltaylgkxyogsfsvcdt:AI4Mind2025%40@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

## Python Test Script

Tạo file `test_db.py`:

```python
import os
from sqlalchemy import create_engine, text

# Test Direct Connection
print("Testing Direct Connection...")
try:
    engine = create_engine("postgresql://postgres:AI4Mind2025%40@db.kfltaylgkxyogsfsvcdt.supabase.co:5432/postgres")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Direct Connection: SUCCESS")
except Exception as e:
    print(f"❌ Direct Connection: FAILED - {e}")

# Test Pooler Connection
print("\nTesting Pooler Connection...")
try:
    engine = create_engine("postgresql://postgres.kfltaylgkxyogsfsvcdt:AI4Mind2025%40@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Pooler Connection: SUCCESS")
except Exception as e:
    print(f"❌ Pooler Connection: FAILED - {e}")
```

Run:

```bash
cd ai-service
python test_db.py
```

## Expected Results

**At Home (LAN):**

- ✅ Direct Connection: SUCCESS
- ✅ Pooler Connection: SUCCESS

**At Office (WiFi):**

- ❌ Direct Connection: FAILED (IPv6/firewall)
- ✅ Pooler Connection: SUCCESS
