"""
Assessment + Voice endpoint - Add voice analysis to existing GAD-7 assessment
Sequential flow: User completes GAD-7 first, then adds voice recording

ASYNC ARCHITECTURE (v2):
  POST /{id}/add-voice       → Validates, uploads to S3, creates stub DB record,
                               kicks off BackgroundTask, returns 202 immediately.
  GET  /{id}/voice-status/{voice_id} → Poll for completion (processing/completed/failed)
"""
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, File, Form, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
import httpx
import json
import logging

from app.core.database import get_db, SessionLocal
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


# ──────────────────────────────────────────────────────────────────────────────
# Background pipeline (runs AFTER 202 response is sent to client)
# ──────────────────────────────────────────────────────────────────────────────

async def _run_voice_pipeline(
    voice_analysis_id: int,
    audio_bytes: bytes,
    audio_filename: str,
    audio_content_type: str,
    gender_for_voice_service: str,
    assessment_id: int,
    prompt_text: str,
    file_size: int,
):
    """
    Heavy pipeline executed as a BackgroundTask:
      1. Call voice-service (Deepgram + emotion ML)
      2. Call Gemini for combined cross-analysis
      3. Update VoiceAnalysis record → status='completed' (or 'failed')
    """
    db = SessionLocal()
    try:
        voice_analysis = db.query(VoiceAnalysis).filter(VoiceAnalysis.id == voice_analysis_id).first()
        if not voice_analysis:
            logger.error(f"[bg] VoiceAnalysis {voice_analysis_id} missing from DB")
            return

        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            logger.error(f"[bg] Assessment {assessment_id} missing from DB")
            return

        # ── Step 1: voice-service ──────────────────────────────────────────
        logger.info(f"[bg] Sending to voice-service: {VOICE_SERVICE_URL}/api/v1/voice/analyze")
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{VOICE_SERVICE_URL}/api/v1/voice/analyze",
                files={"file": (audio_filename, audio_bytes, audio_content_type or "audio/mpeg")},
                data={"user_id": str(voice_analysis.student_id), "gender": gender_for_voice_service},
            )
            response.raise_for_status()
            voice_result = response.json()

        transcript_text = (
            voice_result.get("transcript", {}).get("transcript", "")
            if voice_result.get("transcript") else ""
        )
        logger.info(
            f"[bg] Voice analysis done: emotion={voice_result.get('emotion_result', {}).get('primary_emotion')}, "
            f"transcript_len={len(transcript_text)}"
        )

        # ── Step 2: Gemini combined analysis ──────────────────────────────
        gad7_data = {
            "answers": assessment.answers,
            "total_score": assessment.total_score,
            "severity": assessment.severity_level,
            "functional_impairment": assessment.functional_impairment or 0,
        }
        try:
            logger.info("[bg] Calling Gemini for combined analysis...")
            gemini_result = await gemini_service.analyze_combined(
                gad7_data=gad7_data, voice_data=voice_result
            )
            comprehensive_analysis = gemini_result["analysis"]
            comprehensive_recommendations = gemini_result["recommendations"]
            logger.info("[bg] Gemini analysis completed")
        except Exception as e:
            logger.error(f"[bg] Gemini error (using fallback): {e}")
            comprehensive_analysis = (
                f"Phân tích tổng hợp: Điểm GAD-7 là {assessment.total_score}/21 "
                f"({assessment.severity_level}). "
                f"Cảm xúc giọng nói: {voice_result.get('emotion_result', {}).get('primary_emotion', 'N/A')}."
            )
            comprehensive_recommendations = [
                "Gặp tư vấn viên để được hỗ trợ chi tiết hơn",
                "Thực hành các kỹ thuật thư giãn hàng ngày",
                "Theo dõi tình trạng trong thời gian tới",
            ]

        # Normalise recommendations to plain strings
        if comprehensive_recommendations and isinstance(comprehensive_recommendations[0], dict):
            comprehensive_recommendations = [
                rec.get("recommendation", str(rec)) for rec in comprehensive_recommendations
            ]

        # ── Step 3: Update DB record ──────────────────────────────────────
        voice_analysis.audio_duration = voice_result.get("audio_duration")
        voice_analysis.audio_format = audio_filename.rsplit(".", 1)[-1] if "." in audio_filename else "unknown"

        t = voice_result.get("transcript") or {}
        voice_analysis.transcription = t.get("transcript")
        voice_analysis.transcription_language = t.get("language", "vi")
        voice_analysis.word_count = t.get("word_count", 0)
        voice_analysis.transcription_confidence = t.get("confidence")

        voice_analysis.audio_features = voice_result.get("audio_features")

        er = voice_result.get("emotion_result") or {}
        voice_analysis.detected_emotions = {"primary_emotion": er.get("primary_emotion")}
        voice_analysis.dominant_emotion = er.get("primary_emotion")
        voice_analysis.emotion_confidence = er.get("confidence", 0.0)

        ta = voice_result.get("text_analysis") or {}
        voice_analysis.sentiment_score = ta.get("sentiment_score")
        voice_analysis.keywords = ta.get("keywords")
        voice_analysis.psychological_markers = ta.get("psychological_markers")

        voice_analysis.normalized_features = voice_result.get("normalized_features")

        # comprehensive_analysis is Column(Text) — must be a string, not a dict
        if isinstance(comprehensive_analysis, dict):
            comprehensive_analysis = json.dumps(comprehensive_analysis, ensure_ascii=False)
        voice_analysis.comprehensive_analysis = comprehensive_analysis

        # comprehensive_recommendations is Column(JSON) — must be a list, not a JSON string
        if isinstance(comprehensive_recommendations, str):
            try:
                comprehensive_recommendations = json.loads(comprehensive_recommendations)
            except (json.JSONDecodeError, TypeError):
                pass
        voice_analysis.comprehensive_recommendations = comprehensive_recommendations
        voice_analysis.processing_status = "completed"
        voice_analysis.processed_at = datetime.utcnow()
        voice_analysis.processing_time = voice_result.get("processing_time", 0.0)

        db.commit()
        logger.info(f"[bg] VoiceAnalysis {voice_analysis_id} → completed ✅")

    except Exception as e:
        logger.error(f"[bg] Pipeline failed for VoiceAnalysis {voice_analysis_id}: {e}", exc_info=True)
        try:
            va = db.query(VoiceAnalysis).filter(VoiceAnalysis.id == voice_analysis_id).first()
            if va:
                va.processing_status = "failed"
                va.has_error = 1
                va.error_message = str(e)[:500]
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────────────
# POST  /{assessment_id}/add-voice  →  202 Accepted  (returns immediately)
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/{assessment_id}/add-voice", status_code=status.HTTP_202_ACCEPTED)
async def add_voice_to_assessment(
    assessment_id: int,
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(..., description="Voice recording file"),
    gender: str = Form(..., description="Gender: male, female, other, prefer_not_to_say"),
    prompt_text: Optional[str] = Form(
        "Hãy chia sẻ cảm xúc của bạn trong 2 tuần qua", description="Recording prompt"
    ),
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    """
    Start async voice analysis for an existing GAD-7 assessment.

    Returns 202 immediately with `voice_analysis_id`.
    Poll  GET /{assessment_id}/voice-status/{voice_analysis_id}  until
    `processing_status` is 'completed' or 'failed'.
    """
    student = current_user.student
    if not student:
        raise HTTPException(403, "Only students can submit assessments")

    # ── Load & authorise assessment ──────────────────────────────────────
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.student_id == student.id,
    ).first()
    if not assessment:
        raise HTTPException(404, f"Assessment {assessment_id} not found or not accessible")

    # ── Validate audio file ───────────────────────────────────────────────
    valid_genders = ["male", "female", "other", "prefer_not_to_say"]
    if gender not in valid_genders:
        raise HTTPException(400, f"Gender must be one of: {', '.join(valid_genders)}")

    audio_bytes = await audio_file.read()
    file_size = len(audio_bytes)

    if file_size == 0:
        raise HTTPException(400, "Audio file is empty")

    MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB
    if file_size > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large: {file_size / 1024 / 1024:.1f}MB. Maximum 10MB.",
        )

    gender_for_voice_service = "other" if gender == "prefer_not_to_say" else gender

    # ── Upload audio to Supabase Storage (fast, ~1-2 s) ──────────────────
    try:
        file_info = storage.save_audio(
            file_content=audio_bytes,
            filename=audio_file.filename,
            current_user=current_user,
            db=db,
        )
        storage_path = file_info["path"]
        logger.info(f"Audio saved to storage: {storage_path}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Storage error: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to save audio: {str(e)}")

    # ── Create stub VoiceAnalysis record immediately ──────────────────────
    voice_analysis = VoiceAnalysis(
        student_id=student.id,
        assessment_id=assessment_id,
        audio_file_path=storage_path,
        file_size_bytes=file_size,
        prompt_text=prompt_text,
        gender_used=gender_for_voice_service,
        processing_status="processing",
    )
    db.add(voice_analysis)
    db.commit()
    db.refresh(voice_analysis)
    logger.info(f"Created stub VoiceAnalysis id={voice_analysis.id}, status=processing")

    # ── Schedule heavy pipeline as background task ────────────────────────
    background_tasks.add_task(
        _run_voice_pipeline,
        voice_analysis.id,
        audio_bytes,
        audio_file.filename,
        audio_file.content_type or "audio/mpeg",
        gender_for_voice_service,
        assessment_id,
        prompt_text,
        file_size,
    )

    return {
        "voice_analysis_id": voice_analysis.id,
        "assessment_id": assessment_id,
        "processing_status": "processing",
        "message": "Voice analysis started. Poll voice-status endpoint for updates.",
    }


# ──────────────────────────────────────────────────────────────────────────────
# GET  /{assessment_id}/voice-status/{voice_analysis_id}  →  polling endpoint
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/{assessment_id}/voice-status/{voice_analysis_id}")
async def get_voice_analysis_status(
    assessment_id: int,
    voice_analysis_id: int,
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    """
    Poll the processing status of a voice analysis job.

    Returns:
    - processing_status = 'processing'  →  still running, poll again in 3s
    - processing_status = 'completed'   →  full result included in response
    - processing_status = 'failed'      →  error_message included
    """
    student = current_user.student
    if not student:
        raise HTTPException(403, "Students only")

    va = db.query(VoiceAnalysis).filter(
        VoiceAnalysis.id == voice_analysis_id,
        VoiceAnalysis.assessment_id == assessment_id,
        VoiceAnalysis.student_id == student.id,
    ).first()

    if not va:
        raise HTTPException(404, "Voice analysis job not found")

    if va.processing_status == "processing":
        return {"processing_status": "processing", "voice_analysis_id": va.id}

    if va.processing_status == "failed":
        return {
            "processing_status": "failed",
            "voice_analysis_id": va.id,
            "error_message": va.error_message or "Unknown error",
        }

    # Completed — return full result
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    return {
        "processing_status": "completed",
        # fields expected by frontend ComprehensiveResultsPage
        "id": va.id,
        "student_id": va.student_id,
        "assessment_id": va.assessment_id,
        "audio_file_path": va.audio_file_path,
        "transcription": va.transcription,
        "dominant_emotion": va.dominant_emotion,
        "sentiment_score": va.sentiment_score,
        "comprehensive_analysis": va.comprehensive_analysis,
        "comprehensive_recommendations": va.comprehensive_recommendations,
        "gad7_score": assessment.total_score if assessment else None,
        "gad7_severity": assessment.severity_level if assessment else None,
        "created_at": va.created_at,
    }
