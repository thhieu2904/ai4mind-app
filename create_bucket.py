"""
Create Supabase Storage bucket via API
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Missing Supabase credentials in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Create bucket
try:
    result = supabase.storage.create_bucket("audio-files", options={"public": False})
    print(f"✅ Bucket created: {result}")
except Exception as e:
    if "already exists" in str(e).lower():
        print("⚠️  Bucket 'audio-files' already exists")
    else:
        print(f"❌ Error creating bucket: {e}")
        exit(1)

print("\n✅ Storage bucket ready!")
