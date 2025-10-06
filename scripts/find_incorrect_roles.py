"""
Find users with incorrect lowercase roles
"""
import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Check for users with lowercase roles
    result = db.execute(text("""
        SELECT id, email, full_name, role::text, created_at
        FROM users
        WHERE role::text IN ('student', 'parent', 'counselor', 'admin')
        ORDER BY created_at DESC;
    """))
    
    print('=== Users with LOWERCASE roles (BUG) ===')
    count = 0
    for row in result:
        count += 1
        print(f'{count}. ID: {row.id}, Email: {row.email}')
        print(f'   Name: {row.full_name}')
        print(f'   Role: {row.role} ❌ (should be {row.role.upper()})')
        print(f'   Created: {row.created_at}')
        print()
    
    if count == 0:
        print('✅ No users with lowercase roles found')
    else:
        print(f'\n⚠️  Found {count} users with lowercase roles!')
        print('\n=== Fix SQL ===')
        print("""
        -- Fix counselor role
        UPDATE users SET role = 'COUNSELOR' WHERE role::text = 'counselor';
        
        -- Fix other roles if any
        UPDATE users SET role = 'STUDENT' WHERE role::text = 'student';
        UPDATE users SET role = 'PARENT' WHERE role::text = 'parent';
        UPDATE users SET role = 'ADMIN' WHERE role::text = 'admin';
        """)
        
finally:
    db.close()
