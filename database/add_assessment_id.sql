-- Add missing assessment_id column to voice_analyses table
-- This column links voice analysis to an assessment (optional)

ALTER TABLE voice_analyses 
ADD COLUMN IF NOT EXISTS assessment_id INTEGER;

-- Add foreign key constraint
ALTER TABLE voice_analyses 
ADD CONSTRAINT fk_voice_analyses_assessment
FOREIGN KEY (assessment_id) 
REFERENCES assessments(id) 
ON DELETE SET NULL;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_voice_analyses_assessment 
ON voice_analyses(assessment_id);

-- Verify changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'voice_analyses' 
AND column_name = 'assessment_id';
