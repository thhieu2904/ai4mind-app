-- Migration: Add missing columns to voice_analyses table
-- Comparing model (voice_analysis.py) vs current database schema

-- Audio file metadata
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS file_size_bytes INTEGER;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS audio_format VARCHAR(10);

-- Prompt information
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS prompt_id INTEGER;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS prompt_text TEXT;

-- Transcription metadata
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS word_count INTEGER;

-- Audio features (JSONB for PostgreSQL optimization)
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS audio_features JSONB;

-- Text/Semantic analysis
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS sentiment_score FLOAT;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS keywords JSONB;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS psychological_markers JSONB;

-- Gender-normalized features
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS gender_used VARCHAR(20);
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS normalized_features JSONB;

-- Processing status (CRITICAL - required by model with default='pending')
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS processing_status VARCHAR(20) DEFAULT 'pending' NOT NULL;

-- Created timestamp (CRITICAL - required by model)
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_voice_analyses_dominant_emotion ON voice_analyses(dominant_emotion);
CREATE INDEX IF NOT EXISTS idx_voice_analyses_processing_status ON voice_analyses(processing_status);
CREATE INDEX IF NOT EXISTS idx_voice_analyses_created_at ON voice_analyses(created_at);

-- Update existing rows to have default values
UPDATE voice_analyses 
SET processing_status = 'completed' 
WHERE processing_status IS NULL;

UPDATE voice_analyses 
SET created_at = processed_at 
WHERE created_at IS NULL AND processed_at IS NOT NULL;

UPDATE voice_analyses 
SET created_at = NOW() 
WHERE created_at IS NULL;

-- Verify: Show all columns in order
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'voice_analyses' 
ORDER BY ordinal_position;
