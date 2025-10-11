"""
Voice Analysis API Endpoints - HYBRID ARCHITECTURE

Architecture Change (2025-10-06):
✅ BEFORE: Whisper (local) → 512MB+ RAM → Build failed on Render free tier
✅ AFTER: Deepgram API (external) + Custom Emotion ML (local) → <512MB RAM → Deploy OK!

Pipeline:
1. Deepgram API → Transcription (external, lightweight)
2. Librosa → Audio features (local)
3. Gender Normalizer → Z-score normalization (local, our algorithm!)
4. Custom ML → Emotion detection (local, our unique value!)
5. Text Analyzer → Sentiment analysis (local)

This hybrid approach:
- ✅ Deploys on free tier (memory optimization)
- ✅ Keeps custom emotion ML (our competitive advantage)
- ✅ Uses production-grade transcription (Deepgram)
- ✅ Shows engineering maturity (build vs buy decision)
"""

import os
import uuid
import logging
import gc  # ✅ Add garbage collection for memory optimization
from pathlib import Path
from datetime import datetime
from typing import Optional
import time

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.schemas import (
    VoiceAnalysisResponse,
    ErrorResponse,
    AudioFeatures,
    NormalizedFeatures,
    TranscriptResult,
    EmotionResult,
    TextAnalysisResult
)
from app.services.audio_processor import AudioProcessor
from app.services.deepgram_service import DeepgramService  # NEW: Hybrid approach
# WhisperService imported conditionally below (FALLBACK: Local dev only)
from app.services.emotion_classifier import EmotionClassifier  # KEPT: Our unique value!
from app.services.text_analyzer import TextAnalyzer
from app.utils.gender_normalizer import GenderNormalizer  # KEPT: Our algorithm!
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice-analysis"])

# Initialize services (singleton pattern)
audio_processor = AudioProcessor()

# Transcription service - HYBRID APPROACH
if settings.use_deepgram:
    # Production: Use Deepgram API (lightweight, deployable)
    transcription_service = DeepgramService(api_key=settings.DEEPGRAM_API_KEY)
    logger.info("✅ Using Deepgram API for transcription (production mode)")
else:
    # Fallback: Use Whisper (local dev only, not deployable on free tier)
    # Import only when needed to avoid ModuleNotFoundError in production
    from app.services.whisper_service import WhisperService
    transcription_service = WhisperService(model_size=settings.WHISPER_MODEL)
    logger.warning("⚠️  Using Whisper for transcription (local dev only, NOT deployable!)")

# Custom ML services - KEPT (our competitive advantage!)
emotion_classifier = EmotionClassifier()
text_analyzer = TextAnalyzer()
gender_normalizer = GenderNormalizer()


@router.post("/analyze", response_model=VoiceAnalysisResponse)
async def analyze_voice(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, M4A)"),
    user_id: int = Form(..., description="User ID"),
    gender: str = Form(..., description="User gender (male/female/other)"),
    prompt_id: Optional[int] = Form(None, description="Recording prompt ID")
):
    """
    Analyze voice recording for emotional state.
    
    Process:
    1. Save uploaded audio file
    2. Extract audio features (pitch, energy, speech rate)
    3. Normalize by gender to avoid bias
    4. Transcribe to text (Whisper)
    5. Detect emotions (hybrid approach)
    6. Analyze text for psychological markers
    7. Return comprehensive analysis
    
    Args:
        file: Audio file (WAV, MP3, M4A, max 10MB)
        user_id: User identifier
        gender: User gender (male/female/other) for normalization
        prompt_id: Optional prompt ID used for recording
    
    Returns:
        Complete voice analysis with emotions, transcript, features
    
    Raises:
        400: Invalid file format or gender
        413: File too large (>10MB)
        500: Processing error
    """
    start_time = time.time()
    
    # Log incoming request details
    logger.info(f"📥 Received: file={file.filename}, content_type={file.content_type}, user_id={user_id}, gender={gender}")
    
    # Read file content for logging
    file_content = await file.read()
    file_size = len(file_content)
    logger.info(f"📊 File stats: size={file_size} bytes, first_10={file_content[:10]}")
    await file.seek(0)  # Reset for further processing
    
    # Validate file format
    allowed_formats = [".wav", ".mp3", ".m4a", ".flac", ".ogg"]
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed: {', '.join(allowed_formats)}"
        )
    
    # Validate gender
    gender = gender.lower()
    if gender not in ["male", "female", "other"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gender must be 'male', 'female', or 'other'"
        )
    
    # Generate unique analysis ID
    analysis_id = f"voice_{uuid.uuid4().hex[:12]}"
    
    logger.info(f"🎤 Starting analysis {analysis_id} for user {user_id} (gender={gender})")

    
    # Save uploaded file temporarily
    # Production: Use /tmp (always writable on Linux)
    # Development: Use configured path
    if settings.is_production:
        storage_path = Path("/tmp/ai4mind-voice")
    else:
        storage_path = Path(settings.FILE_STORAGE_PATH)
    
    temp_dir = storage_path / "temp"
    
    # Create directories if needed
    try:
        temp_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create temp directory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage initialization failed: {str(e)}"
        )
    
    temp_file_path = temp_dir / f"{analysis_id}{file_ext}"
    
    try:
        # Save file
        contents = await file.read()
        
        # Check file size (10MB limit)
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit"
            )
        
        with open(temp_file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"📁 File saved: {temp_file_path.name} ({len(contents)} bytes)")
        
        # Step 1: Extract audio features
        logger.info("🎵 Step 1/5: Extracting audio features...")
        audio_features_dict = audio_processor.process_audio_file(str(temp_file_path))
        
        audio_features = AudioFeatures(
            pitch_mean=audio_features_dict["pitch_mean"],
            pitch_std=audio_features_dict["pitch_std"],
            pitch_min=audio_features_dict["pitch_min"],
            pitch_max=audio_features_dict["pitch_max"],
            energy_mean=audio_features_dict["energy_mean"],
            energy_std=audio_features_dict["energy_std"],
            speech_rate=audio_features_dict["syllables_per_second"],
            pause_count=audio_features_dict["pause_count"],
            pause_duration=audio_features_dict["pause_duration_seconds"],
            voice_stability=audio_features_dict["voice_stability"],
            duration=audio_features_dict["duration"]
        )
        
        logger.info(f"✅ Audio features extracted: pitch={audio_features.pitch_mean:.1f}Hz, "
                   f"rate={audio_features.speech_rate:.2f} syl/s")
        
        # Step 2: Normalize by gender
        logger.info(f"⚖️ Step 2/5: Normalizing by gender ({gender})...")
        normalized = gender_normalizer.normalize_all_features(
            raw_features=audio_features_dict,
            gender=gender
        )
        
        normalized_features = NormalizedFeatures(**normalized)
        
        logger.info(f"✅ Features normalized: Z-score={normalized_features.pitch_z_score:.2f}, "
                   f"severity={normalized_features.severity}")
        
        # Step 3: Transcribe audio - HYBRID APPROACH
        logger.info("🎤 Step 3/5: Transcribing speech...")
        
        if settings.use_deepgram:
            # Production: Use Deepgram API
            logger.info("📡 Using Deepgram API for transcription...")
            transcript_dict = await transcription_service.transcribe(
                audio_path=str(temp_file_path),
                language="vi"
            )
            logger.info(f"✅ Deepgram transcription complete (source: external API)")
        else:
            # Fallback: Use local Whisper (dev only)
            logger.warning("⚠️  Using local Whisper (not deployable on free tier!)")
            # Note: Whisper is synchronous, Deepgram is async
            transcript_dict = transcription_service.transcribe(
                audio_path=str(temp_file_path),
                language="vi"
            )
            logger.info(f"✅ Whisper transcription complete (source: local)")
        
        transcript = TranscriptResult(
            transcript=transcript_dict["transcript"],
            language=transcript_dict["language"],
            duration=transcript_dict["duration"],
            confidence=transcript_dict["confidence"],
            word_count=transcript_dict["word_count"]
        )
        
        logger.info(f"✅ Transcription complete: {transcript.word_count} words, "
                   f"confidence={transcript.confidence:.2f}")
        logger.info(f"📝 Text: {transcript.transcript[:100]}...")
        
        # Step 4: Detect emotions - CUSTOM ML (our unique value!)
        logger.info("🧠 Step 4/5: Detecting emotions (custom ML model)...")
        emotion_dict = emotion_classifier.classify(
            normalized_features.dict(),
            transcript.transcript
        )
        
        emotion_result = EmotionResult(**emotion_dict)
        
        logger.info(f"✅ Emotion detected: {emotion_result.primary_emotion} "
                   f"({emotion_result.intensity}, conf={emotion_result.confidence:.2f})")
        
        # Step 5: Analyze text
        logger.info("📊 Step 5/5: Analyzing text...")
        text_analysis_dict = text_analyzer.analyze(transcript.transcript)
        
        text_analysis = TextAnalysisResult(**text_analysis_dict)
        
        logger.info(f"✅ Text analysis complete: sentiment={text_analysis.sentiment:.2f}, "
                   f"dominant={text_analysis.dominant_emotion}")
        
        # ✅ Free memory after processing
        gc.collect()
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Construct response
        response = VoiceAnalysisResponse(
            analysis_id=analysis_id,
            user_id=user_id,
            timestamp=datetime.now(),
            audio_features=audio_features,
            normalized_features=normalized_features,
            transcript=transcript,
            emotion_result=emotion_result,
            text_analysis=text_analysis,
            gender=gender,
            audio_duration=audio_features.duration,
            processing_time=round(processing_time, 2)
        )
        
        logger.info(f"🎉 Analysis complete: {analysis_id} in {processing_time:.2f}s")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice analysis failed: {str(e)}"
        )
        
    finally:
        # Clean up temporary file
        if temp_file_path.exists():
            try:
                os.remove(temp_file_path)
                logger.info(f"🗑️ Temporary file deleted: {temp_file_path.name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not delete temp file: {e}")
        
        # ✅ Force garbage collection to free memory
        gc.collect()


@router.get("/prompts")
async def get_voice_prompts():
    """
    Get Vietnamese voice recording prompts.
    
    Returns list of prompts for users to record their voice.
    Prompts are designed to elicit natural speech covering:
    - Daily activities (neutral baseline)
    - Current emotions (anxiety, mood)
    - Future outlook (hope, worry)
    
    Returns:
        List of VoicePrompt objects
    """
    from ...core.constants import VOICE_PROMPTS
    
    prompts = [
        {
            "id": i + 1,
            "text": prompt,
            "duration_estimate": 15,  # ~15 seconds per prompt
            "category": _categorize_prompt(i)
        }
        for i, prompt in enumerate(VOICE_PROMPTS)
    ]
    
    return {"prompts": prompts, "total": len(prompts)}


def _categorize_prompt(index: int) -> str:
    """Categorize prompt by index"""
    if index == 0:
        return "daily"  # Daily activities
    elif index in [1, 2]:
        return "emotion"  # Current emotional state
    else:
        return "future"  # Future outlook


@router.get("/health")
async def health_check():
    """
    Health check endpoint for voice analysis service - HYBRID ARCHITECTURE.
    
    Returns:
        Service status, version, and configuration
    """
    transcription_info = {
        "service": "deepgram-api" if settings.use_deepgram else "whisper-local",
        "deployable": settings.use_deepgram,  # Only Deepgram fits free tier
        "model": "nova-2" if settings.use_deepgram else settings.WHISPER_MODEL
    }
    
    return {
        "status": "healthy",
        "service": "voice-analysis-hybrid",
        "version": settings.VERSION,
        "timestamp": datetime.now(),
        "architecture": "hybrid",
        "transcription": transcription_info,
        "emotion_detection": "custom-ml (gender-normalized)",
        "memory_optimized": True,
        "free_tier_compatible": settings.use_deepgram
    }
