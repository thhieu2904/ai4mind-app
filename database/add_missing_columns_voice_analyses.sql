-- Migration: Add missing columns to voice_analyses table
-- Based on VoiceAnalysis model in app/models/voice_analysis.py

-- Audio file info (if not exists)
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS file_size_bytes INTEGER;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS audio_duration FLOAT;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS audio_format VARCHAR(10);

-- Prompt info
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS prompt_id INTEGER;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS prompt_text TEXT;

-- Transcription confidence
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS transcription_confidence FLOAT;

-- Audio features (JSONB for better querying)
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS audio_features JSONB;

-- Emotion detection
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS detected_emotions JSONB;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS emotion_confidence FLOAT;

-- Text/Semantic analysis
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS keywords JSONB;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS psychological_markers JSONB;

-- Gender-normalized features
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS gender_used VARCHAR(20);
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS normalized_features JSONB;

-- Processing metadata
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS processed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS processing_time FLOAT;

-- Error handling
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS has_error INTEGER DEFAULT 0;
ALTER TABLE voice_analyses ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Add indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_voice_analyses_dominant_emotion ON voice_analyses(dominant_emotion);
CREATE INDEX IF NOT EXISTS idx_voice_analyses_processing_status ON voice_analyses(processing_status);
CREATE INDEX IF NOT EXISTS idx_voice_analyses_has_error ON voice_analyses(has_error);

-- Verify: List all columns
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'voice_analyses' 
ORDER BY ordinal_position;
