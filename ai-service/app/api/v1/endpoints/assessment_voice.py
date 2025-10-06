"""
Assessment + Voice endpoint - Add voice analysis to existing GAD-7 assessment
Sequential flow: User completes GAD-7 first, then adds voice recording
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
import httpx
import logging

from app.core.database import get_db
from app.core.security import require_roles
from app.core.config import settings
from app.models.user import User
from app.models.assessment import Assessment
from app.models.voice_analysis import VoiceAnalysis
from app.schemas.voice_analysis import VoiceAnalysisResponse
from app.services.gemini_service import GeminiService
from app.utils.storage import storage

router = APIRouter()
gemini_service = GeminiService()
logger = logging.getLogger(__name__)

# Voice service URL
if not settings.VOICE_SERVICE_URL:
    raise ValueError("VOICE_SERVICE_URL environment variable is required")
VOICE_SERVICE_URL = settings.VOICE_SERVICE_URL


@router.post("/{assessment_id}/add-voice", response_model=VoiceAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def add_voice_to_assessment(
    assessment_id: int,
    audio_file: UploadFile = File(..., description="Voice recording file"),
    gender: str = Form(..., description="Gender for voice analysis: male, female, other, prefer_not_to_say"),
    prompt_text: Optional[str] = Form("Hãy chia sẻ cảm xúc của bạn trong 2 tuần qua", description="Recording prompt"),
    
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db)
):
    """
    Add voice analysis to existing GAD-7 assessment (Sequential flow - RECOMMENDED).
    
    **Use case:**
    1. User completes GAD-7 → Gets assessment_id
    2. User records voice → Submits to this endpoint with assessment_id
    3. Backend loads GAD-7 from database
    4. Backend calls voice-service
    5. Backend calls Gemini analyze_combined() with both data
    6. Returns comprehensive analysis
    
    **Benefits:**
    - GAD-7 already saved in DB → No risk of data loss
    - User can add voice anytime (immediately or days later)
    - No need to pass GAD-7 data through navigation
    - Flexible user flow
    
    **Process:**
    1. Load Assessment from database by assessment_id
    2. Validate ownership (student can only access their own assessments)
    3. Upload audio to Supabase Storage
    4. Send audio to voice-service for analysis
    5. Combine GAD-7 + voice data and send to Gemini
    6. Save VoiceAnalysis with assessment_id link
    7. Return comprehensive analysis
    
    **Gender:** Required for voice normalization
    - male, female, other, prefer_not_to_say
    """
    
    student = current_user.student
    if not student:
        raise HTTPException(403, "Only students can submit assessments")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: Load Assessment from Database (Already saved!) - OPTIMIZED
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.student_id == student.id  # Security: Only own assessments
    ).first()
    
    if not assessment:
        raise HTTPException(404, f"Assessment {assessment_id} not found or not accessible")
    
    logger.info(f"Loaded assessment {assessment_id}: score={assessment.total_score}, severity={assessment.severity_level}")
    
    # OPTIMIZATION: Use EXISTS query instead of .count() for checking duplicates
    # Old: .count() loads all matching rows then counts
    # New: EXISTS returns True/False immediately
    has_existing_voice = db.query(
        db.query(VoiceAnalysis).filter(
            VoiceAnalysis.assessment_id == assessment_id
        ).exists()
    ).scalar()
    
    if has_existing_voice:
        logger.info(f"Found existing voice analysis for assessment {assessment_id}, creating another one for testing")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: Process Voice Recording
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Validate gender
    valid_genders = ["male", "female", "other", "prefer_not_to_say"]
    if gender not in valid_genders:
        raise HTTPException(400, f"Gender must be one of: {', '.join(valid_genders)}")
    
    # Read audio file
    audio_bytes = await audio_file.read()
    file_size = len(audio_bytes)
    
    if file_size == 0:
        raise HTTPException(400, "Audio file is empty")
    
    logger.info(f"Audio file: {audio_file.filename}, size={file_size} bytes")
    
    # Gender mapping for voice-service
    gender_for_voice_service = "other" if gender == "prefer_not_to_say" else gender
    
    # Save to Supabase Storage
    try:
        file_info = storage.save_audio(
            file_content=audio_bytes,
            filename=audio_file.filename,
            current_user=current_user,
            db=db
        )
        storage_path = file_info["path"]
        logger.info(f"Audio saved to storage: {storage_path}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Storage error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to save audio: {str(e)}")
    
    # Send to voice-service for analysis
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            files = {
                "file": (audio_file.filename, audio_bytes, audio_file.content_type or "audio/mpeg")
            }
            data = {
                "user_id": current_user.id,
                "gender": gender_for_voice_service
            }
            
            logger.info(f"Sending to voice-service: {VOICE_SERVICE_URL}/api/v1/voice/analyze")
            response = await client.post(
                f"{VOICE_SERVICE_URL}/api/v1/voice/analyze",
                files=files,
                data=data
            )
            response.raise_for_status()
            voice_result = response.json()
            
        transcript_text = voice_result.get('transcript', {}).get('transcript', '') if voice_result.get('transcript') else ''
        logger.info(f"Voice analysis completed: primary_emotion={voice_result.get('emotion_result', {}).get('primary_emotion')}, "
                   f"transcript_length={len(transcript_text)}")
        
    except httpx.HTTPError as e:
        logger.error(f"Voice service error: {e}", exc_info=True)
        raise HTTPException(502, f"Voice analysis failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected voice service error: {e}", exc_info=True)
        raise HTTPException(500, f"Voice processing failed: {str(e)}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: Combined Gemini Analysis (Cross-validation)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Prepare GAD-7 data from database (already saved!)
    gad7_data = {
        "answers": assessment.answers,
        "total_score": assessment.total_score,
        "severity": assessment.severity_level,
        "functional_impairment": assessment.functional_impairment or 0
    }
    
    try:
        logger.info("Sending to Gemini for combined analysis...")
        gemini_result = await gemini_service.analyze_combined(
            gad7_data=gad7_data,
            voice_data=voice_result
        )
        comprehensive_analysis = gemini_result["analysis"]
        comprehensive_recommendations = gemini_result["recommendations"]
        logger.info("Gemini comprehensive analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Gemini error: {e}", exc_info=True)
        # Fallback to simple analysis
        comprehensive_analysis = (
            f"Phân tích tổng hợp: Điểm GAD-7 là {assessment.total_score}/21 ({assessment.severity_level}). "
            f"Cảm xúc từ giọng nói: {voice_result.get('emotion_result', {}).get('primary_emotion', 'N/A')}. "
            f"Cần đánh giá thêm với tư vấn viên."
        )
        comprehensive_recommendations = [
            "Gặp tư vấn viên để được hỗ trợ chi tiết hơn",
            "Thực hành các kỹ thuật thư giãn hàng ngày",
            "Theo dõi tình trạng trong thời gian tới"
        ]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 4: Save VoiceAnalysis to Database (Linked to Assessment)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Parse recommendations if structured - handle both dict and string formats
    if comprehensive_recommendations and len(comprehensive_recommendations) > 0:
        try:
            # Check if first item is dict, if so convert all
            if isinstance(comprehensive_recommendations[0], dict):
                comprehensive_recommendations = [
                    rec.get("recommendation", str(rec)) if isinstance(rec, dict) else str(rec) 
                    for rec in comprehensive_recommendations
                ]
        except (IndexError, AttributeError):
            # Fallback: ensure all items are strings
            comprehensive_recommendations = [str(rec) for rec in comprehensive_recommendations]
    
    try:
        voice_analysis = VoiceAnalysis(
            student_id=student.id,
            assessment_id=assessment_id,  # ← Link to GAD-7!
            
            # File info
            audio_file_path=storage_path,
            file_size_bytes=file_size,
            audio_duration=voice_result.get("audio_duration"),
            audio_format=audio_file.filename.split(".")[-1] if "." in audio_file.filename else "unknown",
            
            # Prompt
            prompt_text=prompt_text,
            
            # Transcription
            transcription=voice_result.get("transcript", {}).get("transcript") if voice_result.get("transcript") else None,
            transcription_language=voice_result.get("transcript", {}).get("language", "vi") if voice_result.get("transcript") else "vi",
            word_count=voice_result.get("transcript", {}).get("word_count", 0) if voice_result.get("transcript") else 0,
            transcription_confidence=voice_result.get("transcript", {}).get("confidence") if voice_result.get("transcript") else None,
            
            # Audio features
            audio_features=voice_result.get("audio_features"),
            
            # Emotions
            detected_emotions={"primary_emotion": voice_result.get("emotion_result", {}).get("primary_emotion")},
            dominant_emotion=voice_result.get("emotion_result", {}).get("primary_emotion"),
            emotion_confidence=voice_result.get("emotion_result", {}).get("confidence", 0.0),
            
            # Text analysis
            sentiment_score=voice_result.get("text_analysis", {}).get("sentiment_score"),
            keywords=voice_result.get("text_analysis", {}).get("keywords"),
            psychological_markers=voice_result.get("text_analysis", {}).get("psychological_markers"),
            
            # Normalization
            gender_used=gender_for_voice_service,
            normalized_features=voice_result.get("normalized_features"),
            
            # 🆕 Comprehensive Analysis from Gemini (cross-validation)
            comprehensive_analysis=comprehensive_analysis,
            comprehensive_recommendations=comprehensive_recommendations,
            
            # Processing metadata
            processing_status="completed",
            processed_at=datetime.utcnow(),
            processing_time=voice_result.get("processing_time", 0.0)
        )
        
        db.add(voice_analysis)
        db.commit()
        db.refresh(voice_analysis)
        
        logger.info(f"Saved voice analysis: id={voice_analysis.id}, linked to assessment={assessment_id}")
        
        # Return comprehensive response
        logger.info("🔍 Preparing response with comprehensive data...")
        logger.info(f"comprehensive_analysis length: {len(comprehensive_analysis) if comprehensive_analysis else 0}")
        logger.info(f"comprehensive_recommendations count: {len(comprehensive_recommendations) if comprehensive_recommendations else 0}")
        
        return VoiceAnalysisResponse(
            id=voice_analysis.id,
            student_id=voice_analysis.student_id,
            assessment_id=voice_analysis.assessment_id,
            audio_file_path=voice_analysis.audio_file_path,
            transcription=voice_analysis.transcription,
            dominant_emotion=voice_analysis.dominant_emotion,
            sentiment_score=voice_analysis.sentiment_score,
            processing_status=voice_analysis.processing_status,
            created_at=voice_analysis.created_at,
            
            # Add comprehensive analysis from Gemini
            comprehensive_analysis=comprehensive_analysis,
            comprehensive_recommendations=comprehensive_recommendations,
            
            # Include original GAD-7 context
            gad7_score=assessment.total_score,
            gad7_severity=assessment.severity_level
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to save voice analysis: {str(e)}")
