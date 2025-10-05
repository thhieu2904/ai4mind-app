"""
Comprehensive check of UserRole enum from database to code
This checks for the critical security bug
"""
import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from app.models.user import User, UserRole

db = SessionLocal()
try:
    print('=== 1. Check UserRole Enum Definition ===')
    print(f'STUDENT: {UserRole.STUDENT}')
    print(f'STUDENT.value: {UserRole.STUDENT.value}')
    print(f'STUDENT type: {type(UserRole.STUDENT)}')
    print(f'All enum values: {[e.value for e in UserRole]}')
    print()
    
    print('=== 2. Check Database Values ===')
    users = db.query(User).limit(5).all()
    for user in users:
        print(f'Email: {user.email}')
        print(f'  role (raw): {repr(user.role)}')
        print(f'  role type: {type(user.role)}')
        print(f'  role == UserRole.STUDENT: {user.role == UserRole.STUDENT}')
        print(f'  role == "STUDENT": {user.role == "STUDENT"}')
        print(f'  role == "student": {user.role == "student"}')
        print()
    
    print('=== 3. Check SQL Schema ===')
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT n.nspname as schema, t.typname as type, e.enumlabel as value
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid  
        JOIN pg_namespace n ON t.typnamespace = n.oid
        WHERE t.typname = 'userrole'
        ORDER BY e.enumsortorder;
    """))
    
    print('Database enum values:')
    for row in result:
        print(f'  {row.value}')
        
finally:
    db.close()
