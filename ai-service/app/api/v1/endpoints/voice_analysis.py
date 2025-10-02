"""
Voice Analysis Endpoints
Secure API for voice recording analysis with ownership verification
"""
from typing import Any, List
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status, Query
from sqlalchemy.orm import Session
import httpx
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.api.dependencies import (
    get_current_user_student,
    check_student_access,
    check_voice_analysis_ownership,
    get_pagination_params
)
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.voice_analysis import VoiceAnalysis
from app.schemas.voice_analysis import (
    VoiceAnalysisResponse,
    VoiceAnalysisDetail,
    VoiceAnalysisSummary
)
from app.utils.storage import storage


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=VoiceAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_voice(
    audio_file: UploadFile = File(..., description="Audio file (WAV format recommended)"),
    assessment_id: int = Form(None, description="Optional: Link to assessment"),
    current_student: Student = Depends(get_current_user_student),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analyze voice recording
    
    Security:
    - Only students can upload
    - File saved to student's own folder
    - Ownership verified throughout process
    
    Flow:
    1. Get student gender from database
    2. Save audio file to Supabase Storage (with ownership)
    3. Call voice-service for processing
    4. Save results to database
    5. Return response with signed URL
    
    Args:
        file: Audio file upload (max 50MB)
        assessment_id: Optional assessment ID to link
        current_student: Current student (injected by dependency)
        db: Database session
    
    Returns:
        VoiceAnalysisResponse: Analysis results with audio URL
    """
    # Validate file
    if not audio_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required"
        )
    
    # Read file content
    try:
        # Read file content for voice service
        audio_bytes = await audio_file.read()
        file_size = len(audio_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )
    
    # Check file size (max 50MB)
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    # Get student gender for normalization
    gender = current_student.gender or "prefer_not_to_say"
    
    # � Map gender to voice-service contract (male/female/other)
    # Voice-service only accepts: male, female, other
    gender_for_voice_service = "other" if gender == "prefer_not_to_say" else gender
    
    logger.info(f"� Gender mapping: {gender} -> {gender_for_voice_service}")
    
    # Save to Supabase Storage (with ownership verification)
    try:
        file_info = storage.save_audio(
            file_content=audio_bytes,  # Direct use, no copy needed
            filename=audio_file.filename,
            current_user=current_student.user,
            db=db
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Call voice-service for processing
    try:
        logger.info(f"🎤 Calling voice-service: student_id={current_student.id}, file={audio_file.filename}, size={len(audio_bytes)}")
        
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout
            response = await client.post(
                f"{settings.VOICE_SERVICE_URL}/api/v1/voice/analyze",
                files={"file": (audio_file.filename, audio_bytes)},
                data={
                    "user_id": str(current_student.id),
                    "gender": gender_for_voice_service  # Use mapped gender
                }
            )
            
            logger.info(f"📊 Voice service response: status={response.status_code}, content_length={len(response.content)}")
            
            if response.status_code != 200:
                logger.error(f"❌ Voice service error {response.status_code}: {response.text[:500]}")
                # Create failed analysis record
                voice_analysis = VoiceAnalysis(
                    student_id=current_student.id,
                    assessment_id=assessment_id,
                    audio_file_path=file_info["path"],
                    file_size_bytes=file_size,
                    gender_used=gender,
                    processing_status="failed",
                    has_error=1,
                    error_message=f"Voice service error: {response.status_code}"
                )
                db.add(voice_analysis)
                db.commit()
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Voice service returned error: {response.status_code}"
                )
            
            voice_result = response.json()
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Voice service timeout. Please try again."
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to voice service: {str(e)}"
        )
    
    # Save results to database
    voice_analysis = VoiceAnalysis(
        student_id=current_student.id,
        assessment_id=assessment_id,
        audio_file_path=file_info["path"],
        file_size_bytes=file_size,
        audio_duration=voice_result.get("audio_duration"),
        audio_format=voice_result.get("audio_format", "wav"),
        transcription=voice_result.get("transcription"),
        transcription_language="vi",
        word_count=voice_result.get("word_count"),
        audio_features=voice_result.get("audio_features"),
        detected_emotions=voice_result.get("detected_emotions"),
        dominant_emotion=voice_result.get("dominant_emotion"),
        sentiment_score=voice_result.get("sentiment_score"),
        keywords=voice_result.get("keywords"),
        psychological_markers=voice_result.get("psychological_markers"),
        gender_used=gender,
        normalized_features=voice_result.get("normalized_features"),
        processing_status="completed",
        processing_time=voice_result.get("processing_time"),
        has_error=0
    )
    
    db.add(voice_analysis)
    db.commit()
    db.refresh(voice_analysis)
    
    # Get signed URL for audio file (with access control)
    try:
        audio_url = storage.get_signed_url(
            file_path=file_info["path"],
            current_user=current_student.user,
            db=db,
            expires_in=3600  # 1 hour
        )
    except Exception as e:
        audio_url = None
    
    # Return response
    return VoiceAnalysisResponse(
        id=voice_analysis.id,
        student_id=voice_analysis.student_id,
        assessment_id=voice_analysis.assessment_id,
        audio_file_url=audio_url,
        transcription=voice_analysis.transcription,
        detected_emotions=voice_analysis.detected_emotions,
        dominant_emotion=voice_analysis.dominant_emotion,
        sentiment_score=voice_analysis.sentiment_score,
        processing_status=voice_analysis.processing_status,
        created_at=voice_analysis.created_at
    )


@router.get("/{analysis_id}", response_model=VoiceAnalysisDetail)
async def get_voice_analysis(
    voice_analysis: VoiceAnalysis = Depends(check_voice_analysis_ownership),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get voice analysis by ID
    
    Security:
    - Ownership verified by dependency
    - Signed URL generated with access control
    
    Args:
        voice_analysis: Voice analysis (injected with ownership check)
        current_user: Current user
        db: Database session
    
    Returns:
        VoiceAnalysisDetail: Complete analysis with audio URL
    """
    # Get fresh signed URL (valid for 1 hour)
    try:
        audio_url = storage.get_signed_url(
            file_path=voice_analysis.audio_file_path,
            current_user=current_user,
            db=db,
            expires_in=3600
        )
    except Exception:
        audio_url = None
    
    return VoiceAnalysisDetail(
        id=voice_analysis.id,
        student_id=voice_analysis.student_id,
        assessment_id=voice_analysis.assessment_id,
        audio_file_url=audio_url,
        file_size_bytes=voice_analysis.file_size_bytes,
        audio_duration=voice_analysis.audio_duration,
        transcription=voice_analysis.transcription,
        word_count=voice_analysis.word_count,
        audio_features=voice_analysis.audio_features,
        detected_emotions=voice_analysis.detected_emotions,
        dominant_emotion=voice_analysis.dominant_emotion,
        sentiment_score=voice_analysis.sentiment_score,
        keywords=voice_analysis.keywords,
        psychological_markers=voice_analysis.psychological_markers,
        gender_used=voice_analysis.gender_used,
        normalized_features=voice_analysis.normalized_features,
        processing_status=voice_analysis.processing_status,
        processing_time=voice_analysis.processing_time,
        has_error=voice_analysis.has_error,
        error_message=voice_analysis.error_message,
        created_at=voice_analysis.created_at
    )


@router.get("/student/{student_id}", response_model=List[VoiceAnalysisSummary])
async def list_student_analyses(
    student: Student = Depends(check_student_access),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    List all voice analyses for a student
    
    Security:
    - Student access verified by dependency
    - Role-based access control:
      - Students: Own data only
      - Counselors: Assigned students
      - Admins: All students
    
    Args:
        student: Student (injected with access check)
        page: Page number
        page_size: Items per page
        current_user: Current user
        db: Database session
    
    Returns:
        List[VoiceAnalysisSummary]: List of analyses
    """
    # Get pagination params
    pagination = get_pagination_params(page, page_size)
    
    # Query analyses
    analyses = db.query(VoiceAnalysis).filter(
        VoiceAnalysis.student_id == student.id
    ).order_by(
        VoiceAnalysis.created_at.desc()
    ).offset(pagination["skip"]).limit(pagination["limit"]).all()
    
    # Convert to response
    results = []
    for analysis in analyses:
        # Get signed URL for each
        try:
            audio_url = storage.get_signed_url(
                file_path=analysis.audio_file_path,
                current_user=current_user,
                db=db,
                expires_in=3600
            )
        except Exception:
            audio_url = None
        
        results.append(VoiceAnalysisSummary(
            id=analysis.id,
            student_id=analysis.student_id,
            assessment_id=analysis.assessment_id,
            audio_file_url=audio_url,
            transcription=analysis.transcription[:200] if analysis.transcription else None,  # First 200 chars
            dominant_emotion=analysis.dominant_emotion,
            sentiment_score=analysis.sentiment_score,
            processing_status=analysis.processing_status,
            created_at=analysis.created_at
        ))
    
    return results


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_voice_analysis(
    voice_analysis: VoiceAnalysis = Depends(check_voice_analysis_ownership),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete voice analysis
    
    Security:
    - Ownership verified by dependency
    - Only owner or admin can delete
    - Also deletes audio file from storage
    
    Args:
        voice_analysis: Voice analysis (injected with ownership check)
        current_user: Current user
        db: Database session
    """
    # Additional check: Only owner or admin can delete
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.id == voice_analysis.student_id).first()
        if student.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own analyses"
            )
    elif current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can delete analyses"
        )
    
    # Delete audio file from storage
    try:
        storage.delete_audio(
            file_path=voice_analysis.audio_file_path,
            current_user=current_user,
            db=db
        )
    except Exception as e:
        # Log error but continue (file might not exist)
        print(f"Warning: Failed to delete audio file: {e}")
    
    # Delete from database
    db.delete(voice_analysis)
    db.commit()
