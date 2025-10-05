import sys
import os

# Add ai-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-service'))

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
conn = engine.connect()

print("=== Admin & Counselor Accounts ===")
result = conn.execute(text("""
    SELECT email, role, full_name 
    FROM users 
    WHERE role IN ('ADMIN', 'COUNSELOR') 
    ORDER BY role, email
"""))

for row in result:
    print(f"{row[1]}: {row[0]} ({row[2] or 'No name'})")

conn.close()
