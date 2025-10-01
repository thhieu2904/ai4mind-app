"""
Update assessments table
Add created_at and functional_impairment columns, rename gemini_analysis to analysis
"""
from sqlalchemy import text
from app.core.database import engine

def update_assessments_table():
    """Update assessments table structure"""
    with engine.connect() as conn:
        try:
            # Add created_at column (copy from completed_at if exists)
            print("Adding 'created_at' column...")
            conn.execute(text("""
                ALTER TABLE assessments 
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """))
            
            # Copy data from completed_at to created_at if completed_at exists
            print("Copying data from completed_at to created_at...")
            conn.execute(text("""
                UPDATE assessments 
                SET created_at = completed_at 
                WHERE created_at IS NULL AND completed_at IS NOT NULL
            """))
            
            # Add functional_impairment column
            print("Adding 'functional_impairment' column...")
            conn.execute(text("""
                ALTER TABLE assessments 
                ADD COLUMN IF NOT EXISTS functional_impairment INTEGER
            """))
            
            # Rename gemini_analysis to analysis if needed
            print("Renaming 'gemini_analysis' to 'analysis'...")
            conn.execute(text("""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='assessments' AND column_name='gemini_analysis'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='assessments' AND column_name='analysis'
                    ) THEN
                        ALTER TABLE assessments RENAME COLUMN gemini_analysis TO analysis;
                    END IF;
                END $$;
            """))
            
            # Change recommendations from TEXT to JSONB for better storage
            print("Converting 'recommendations' column to JSONB...")
            conn.execute(text("""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='assessments' 
                        AND column_name='recommendations'
                        AND data_type='text'
                    ) THEN
                        ALTER TABLE assessments 
                        ALTER COLUMN recommendations TYPE JSONB USING 
                            CASE 
                                WHEN recommendations IS NULL THEN NULL
                                WHEN recommendations = '' THEN NULL
                                ELSE ('["' || recommendations || '"]')::JSONB
                            END;
                    END IF;
                END $$;
            """))
            
            conn.commit()
            print("✓ Successfully updated assessments table")
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating assessments table: {e}")
            raise

if __name__ == "__main__":
    print("Updating assessments table...")
    update_assessments_table()
    print("\nMigration complete!")
