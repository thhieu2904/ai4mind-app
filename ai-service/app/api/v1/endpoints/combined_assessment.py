"""
Combined Assessment endpoint - GAD-7 + Voice Analysis
Unified endpoint for submitting both questionnaire and voice recording together
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
import httpx
import json
import logging

from app.core.database import get_db
from app.core.security import require_roles
from app.core.config import settings
from app.core.constants import get_severity_level
from app.models.user import User
from app.models.assessment import Assessment
from app.models.voice_analysis import VoiceAnalysis
from app.schemas.assessment import AssessmentResponse
from app.services.gemini_service import GeminiService
from app.utils.storage import storage

router = APIRouter()
gemini_service = GeminiService()
logger = logging.getLogger(__name__)

# Voice service URL - REQUIRED for production
if not settings.VOICE_SERVICE_URL:
    raise ValueError("VOICE_SERVICE_URL environment variable is required")
VOICE_SERVICE_URL = settings.VOICE_SERVICE_URL


def calculate_severity(total_score: int) -> str:
    """Calculate GAD-7 severity level from total score"""
    if total_score <= 4:
        return "minimal"
    elif total_score <= 9:
        return "mild"
    elif total_score <= 14:
        return "moderate"
    else:
        return "severe"


@router.post("/submit-with-voice", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def submit_assessment_with_voice(
    # GAD-7 data
    answers: str = Form(..., description="JSON array of 7 answers (0-3 each)"),
    functional_impairment: int = Form(0, ge=0, le=3, description="How difficult have problems made things (0-3)"),
    notes: Optional[str] = Form(None, description="Optional student notes"),
    
    # Voice data
    audio_file: UploadFile = File(..., description="Voice recording file"),
    gender: str = Form(..., description="Gender for voice analysis: male, female, other, prefer_not_to_say"),
    prompt_text: Optional[str] = Form("Hãy chia sẻ cảm xúc của bạn trong 2 tuần qua", description="Recording prompt"),
    
    # Dependencies
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db)
):
    """
    Submit GAD-7 assessment with voice recording (unified flow).
    
    **This is the recommended endpoint for comprehensive mental health assessment.**
    
    Process:
    1. Validate GAD-7 answers (7 integers, 0-3 each)
    2. Upload audio to Supabase Storage
    3. Send audio to voice-service for analysis (transcription, emotions, audio features)
    4. Combine GAD-7 + voice data and send to Gemini for integrated analysis
    5. Save both Assessment and VoiceAnalysis to database (atomic transaction)
    
    **Benefits of combined assessment**:
    - Cross-validation between objective (GAD-7 score) and subjective (voice emotions)
    - Detect emotional suppression (low score but high anxiety in voice)
    - Richer context for personalized recommendations
    - Better accuracy for AI analysis
    
    **GAD-7 Answers**: Array of 7 integers (0-3):
    - 0: Không có gì (Not at all)
    - 1: Vài ngày (Several days)
    - 2: Hơn một nửa thời gian (More than half the days)
    - 3: Gần như mỗi ngày (Nearly every day)
    
    **Gender**: Required for voice normalization
    - male, female, other, prefer_not_to_say
    - Used to normalize pitch and other voice features
    
    **Returns**: Assessment with voice_analysis_id
    """
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: Validate GAD-7 Answers
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    try:
        answers_list = json.loads(answers)
        if not isinstance(answers_list, list):
            raise ValueError("Answers must be a JSON array")
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON format for answers")
    
    if len(answers_list) != 7:
        raise HTTPException(400, f"Must provide exactly 7 answers, got {len(answers_list)}")
    
    if not all(isinstance(a, int) and 0 <= a <= 3 for a in answers_list):
        raise HTTPException(400, "Each answer must be an integer between 0-3")
    
    # Calculate GAD-7 metrics
    total_score = sum(answers_list)
    severity = calculate_severity(total_score)
    
    logger.info(f"GAD-7 validated: score={total_score}, severity={severity}, user={current_user.email}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: Process Voice Recording
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    student = current_user.student
    if not student:
        raise HTTPException(403, "Only students can submit assessments")
    
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
    
    # Gender mapping for voice-service (prefer_not_to_say → other)
    gender_for_voice_service = "other" if gender == "prefer_not_to_say" else gender
    
    # Save to Supabase Storage
    try:
        file_info = storage.save_audio(
            file_content=audio_bytes,
            filename=audio_file.filename,
            current_user=current_user,
            db=db
        )
        storage_path = file_info["path"]  # Changed: "path" not "file_path"
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
                "user_id": current_user.id,  # Required by voice-service
                "gender": gender_for_voice_service
                # prompt_id is optional
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
    
    gad7_data = {
        "answers": answers_list,
        "total_score": total_score,
        "severity": severity,
        "functional_impairment": functional_impairment
    }
    
    try:
        logger.info("Sending to Gemini for combined analysis...")
        gemini_result = await gemini_service.analyze_combined(
            gad7_data=gad7_data,
            voice_data=voice_result
        )
        logger.info("Gemini analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Gemini error: {e}", exc_info=True)
        # Fallback to simple analysis
        gemini_result = {
            "analysis": f"Phân tích tổng hợp: Điểm GAD-7 là {total_score}/21 ({severity}). "
                       f"Cảm xúc từ giọng nói: {voice_result.get('emotions', {})}. "
                       f"Cần đánh giá thêm với tư vấn viên.",
            "recommendations": [
                "Gặp tư vấn viên để được hỗ trợ chi tiết hơn",
                "Thực hành các kỹ thuật thư giãn hàng ngày",
                "Theo dõi tình trạng trong thời gian tới"
            ]
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 4: Save to Database (Atomic Transaction)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Parse recommendations: if Gemini returns list of dicts, extract text only
    recommendations_list = gemini_result["recommendations"]
    if recommendations_list and isinstance(recommendations_list[0], dict):
        # Gemini returned structured format: [{"priority": "Cao", "recommendation": "text"}, ...]
        recommendations_list = [rec.get("recommendation", str(rec)) for rec in recommendations_list]
    
    try:
        # Create assessment first
        assessment = Assessment(
            student_id=student.id,
            answers=answers_list,
            total_score=total_score,
            severity_level=severity,
            functional_impairment=functional_impairment,
            analysis=gemini_result["analysis"],
            recommendations=recommendations_list,
            notes=notes
        )
        db.add(assessment)
        db.flush()  # Get assessment.id without committing
        
        logger.info(f"Created assessment: id={assessment.id}, score={total_score}")
        
        # Create linked voice analysis (assessment_id is NOW REQUIRED!)
        voice_analysis = VoiceAnalysis(
            student_id=student.id,
            assessment_id=assessment.id,  # ← Always linked!
            
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
            
            # Processing metadata
            processing_status="completed",
            processed_at=datetime.utcnow(),
            processing_time=voice_result.get("processing_time", 0.0)
        )
        db.add(voice_analysis)
        
        # Commit both together (atomic transaction)
        db.commit()
        db.refresh(assessment)
        db.refresh(voice_analysis)
        
        logger.info(f"Saved successfully: assessment_id={assessment.id}, voice_id={voice_analysis.id}")
        
        return AssessmentResponse(
            id=assessment.id,
            student_id=assessment.student_id,
            answers=assessment.answers,
            total_score=assessment.total_score,
            severity_level=assessment.severity_level,
            functional_impairment=assessment.functional_impairment,
            analysis=assessment.analysis,
            recommendations=assessment.recommendations,
            notes=assessment.notes,
            created_at=assessment.created_at,
            voice_analysis_id=voice_analysis.id  # ← Return voice_id for reference
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to save assessment: {str(e)}")
