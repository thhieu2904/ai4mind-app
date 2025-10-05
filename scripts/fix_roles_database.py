"""
Fix incorrect lowercase roles in database
"""
import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print('=== Fixing lowercase roles ===')
    
    # Fix counselor
    result = db.execute(text("UPDATE users SET role = 'COUNSELOR' WHERE role::text = 'counselor';"))
    print(f'✅ Fixed {result.rowcount} counselor roles')
    
    # Fix others (just in case)
    result = db.execute(text("UPDATE users SET role = 'STUDENT' WHERE role::text = 'student';"))
    if result.rowcount > 0:
        print(f'⚠️  Fixed {result.rowcount} student roles')
    
    result = db.execute(text("UPDATE users SET role = 'PARENT' WHERE role::text = 'parent';"))
    if result.rowcount > 0:
        print(f'⚠️  Fixed {result.rowcount} parent roles')
    
    result = db.execute(text("UPDATE users SET role = 'ADMIN' WHERE role::text = 'admin';"))
    if result.rowcount > 0:
        print(f'⚠️  Fixed {result.rowcount} admin roles')
    
    db.commit()
    print('\n✅ Database fixed successfully!')
    
    # Verify
    print('\n=== Verification ===')
    result = db.execute(text("""
        SELECT role::text, COUNT(*) 
        FROM users 
        GROUP BY role::text 
        ORDER BY role::text;
    """))
    
    for row in result:
        print(f'  {row[0]}: {row[1]} users')
        
finally:
    db.close()
