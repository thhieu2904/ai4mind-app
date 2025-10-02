-- Fix: Allow transcription to be NULL
-- When voice processing fails, transcription will be empty

ALTER TABLE voice_analyses 
ALTER COLUMN transcription DROP NOT NULL;

-- Verify
SELECT column_name, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'voice_analyses' 
AND column_name = 'transcription';
