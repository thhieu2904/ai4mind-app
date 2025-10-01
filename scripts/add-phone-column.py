"""
Add phone column to users table
Quick migration script
"""
from sqlalchemy import text
from app.core.database import engine

def add_phone_column():
    """Add phone column to users table"""
    with engine.connect() as conn:
        try:
            print("Adding 'phone' column to users table...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS phone VARCHAR(20)
            """))
            conn.commit()
            print("✓ Successfully added 'phone' column")
        except Exception as e:
            print(f"Error: {e}")
            print("Column might already exist or other issue")

if __name__ == "__main__":
    print("Migrating database...")
    add_phone_column()
    print("\nMigration complete!")
