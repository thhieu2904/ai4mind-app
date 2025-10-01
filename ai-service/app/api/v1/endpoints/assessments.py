"""
Assessment endpoints for GAD-7 questionnaire
Submit, list, get detail, and statistics
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.core.constants import GAD7_QUESTIONS_VI, GAD7_ANSWER_OPTIONS_VI, get_severity_level
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentDetail,
    AssessmentStats,
    AssessmentListResponse
)
from app.models.user import User
from app.models.student import Student
from app.models.assessment import Assessment
from app.services.gemini_service import GeminiService


router = APIRouter()
gemini_service = GeminiService()


@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def submit_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db)
) -> Any:
    """
    Submit GAD-7 assessment
    
    Only students can submit assessments.
    System will:
    1. Calculate total score (sum of 7 answers)
    2. Determine severity level
    3. Send to Gemini for Vietnamese analysis
    4. Generate personalized recommendations
    5. Save to database
    
    **Answers:** Array of 7 integers, each 0-3
    - 0: Không có gì (Not at all)
    - 1: Vài ngày (Several days)
    - 2: Hơn nửa số ngày (More than half the days)
    - 3: Gần như mỗi ngày (Nearly every day)
    """
    # Get student profile
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Calculate total score
    total_score = sum(assessment_data.answers)
    
    # Get severity level
    severity_info = get_severity_level(total_score)
    severity_level = None
    if 0 <= total_score <= 4:
        severity_level = "minimal"
    elif 5 <= total_score <= 9:
        severity_level = "mild"
    elif 10 <= total_score <= 14:
        severity_level = "moderate"
    else:
        severity_level = "severe"
    
    # Prepare data for Gemini analysis
    answers_with_questions = []
    for i, answer in enumerate(assessment_data.answers):
        question = GAD7_QUESTIONS_VI[i]
        answer_text = GAD7_ANSWER_OPTIONS_VI[answer]["text"]
        answers_with_questions.append({
            "question": question["text"],
            "answer": answer_text,
            "score": answer
        })
    
    # Get analysis from Gemini
    try:
        analysis_result = await gemini_service.analyze_gad7(
            answers=answers_with_questions,
            total_score=total_score
        )
        analysis = analysis_result.get("analysis", "")
        recommendations = analysis_result.get("recommendations", [])
    except Exception as e:
        print(f"Gemini analysis error: {e}")
        # Fallback if Gemini fails
        analysis = severity_info["description_vi"]
        recommendations = [severity_info["recommendation_vi"]]
    
    # Create assessment record
    assessment = Assessment(
        student_id=student.id,
        answers=assessment_data.answers,
        total_score=total_score,
        severity_level=severity_level,
        analysis=analysis,
        recommendations=recommendations,
        functional_impairment=assessment_data.functional_impairment,
        notes=assessment_data.notes
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    # Return response with user_id for frontend
    assessment_dict = {
        "id": assessment.id,
        "user_id": current_user.id,
        "answers": assessment.answers,
        "total_score": assessment.total_score,
        "severity_level": assessment.severity_level,
        "created_at": assessment.created_at,
        "analysis": assessment.analysis,
        "recommendations": assessment.recommendations,
        "functional_impairment": assessment.functional_impairment,
        "notes": assessment.notes
    }
    
    return AssessmentResponse(**assessment_dict)


@router.get("/", response_model=AssessmentListResponse)
async def list_assessments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    List user's assessments with pagination
    
    - Students see their own assessments
    - Parents see their children's assessments (if consent given)
    - Counselors see assessments from assigned students
    - Admins see all assessments
    """
    query = db.query(Assessment)
    
    # Filter based on role
    if current_user.role == "student":
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        query = query.filter(Assessment.student_id == student.id)
    
    elif current_user.role == "parent":
        # TODO: Filter by children with consent
        # For now, return empty list
        query = query.filter(Assessment.id == -1)
    
    elif current_user.role == "counselor":
        # TODO: Filter by assigned students
        # For now, return empty list
        query = query.filter(Assessment.id == -1)
    
    # Admins see all (no filter needed)
    
    # Order by most recent first
    query = query.order_by(desc(Assessment.created_at))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    # Add user_id to each item
    items_with_user_id = []
    for item in items:
        student = db.query(Student).filter(Student.id == item.student_id).first()
        assessment_dict = {
            "id": item.id,
            "user_id": student.user_id if student else 0,
            "answers": item.answers,
            "total_score": item.total_score,
            "severity_level": item.severity_level,
            "created_at": item.created_at,
            "analysis": item.analysis,
            "recommendations": item.recommendations,
            "functional_impairment": item.functional_impairment,
            "notes": item.notes
        }
        items_with_user_id.append(AssessmentResponse(**assessment_dict))
    
    total_pages = (total + page_size - 1) // page_size
    
    return AssessmentListResponse(
        items=items_with_user_id,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/stats", response_model=AssessmentStats)
async def get_assessment_stats(
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get assessment statistics for current student
    
    Returns:
    - Total number of assessments
    - Average score
    - Latest score and severity
    - Trend (improving, worsening, stable)
    - Score history for charts
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Get all assessments
    assessments = db.query(Assessment).filter(
        Assessment.student_id == student.id
    ).order_by(Assessment.created_at).all()
    
    if not assessments:
        return AssessmentStats(
            total_assessments=0,
            average_score=0.0,
            latest_score=None,
            latest_severity=None,
            trend=None,
            score_history=[]
        )
    
    # Calculate statistics
    total_assessments = len(assessments)
    average_score = sum(a.total_score for a in assessments) / total_assessments
    latest = assessments[-1]
    
    # Determine trend (compare last 3 assessments if available)
    trend = "stable"
    if total_assessments >= 3:
        recent_scores = [a.total_score for a in assessments[-3:]]
        if recent_scores[2] < recent_scores[0] - 2:
            trend = "improving"
        elif recent_scores[2] > recent_scores[0] + 2:
            trend = "worsening"
    elif total_assessments >= 2:
        if assessments[-1].total_score < assessments[-2].total_score - 2:
            trend = "improving"
        elif assessments[-1].total_score > assessments[-2].total_score + 2:
            trend = "worsening"
    
    # Build score history
    score_history = []
    for assessment in assessments:
        score_history.append({
            "date": assessment.created_at.isoformat(),
            "score": assessment.total_score,
            "severity": assessment.severity_level
        })
    
    return AssessmentStats(
        total_assessments=total_assessments,
        average_score=round(average_score, 2),
        latest_score=latest.total_score,
        latest_severity=latest.severity_level,
        trend=trend,
        score_history=score_history
    )


@router.get("/{assessment_id}", response_model=AssessmentDetail)
async def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get detailed assessment by ID
    
    Includes:
    - All answers with questions
    - Severity information
    - Gemini analysis
    - Recommendations
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Check permission
    student = db.query(Student).filter(Student.id == assessment.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Students can only see their own
    if current_user.role == "student" and student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own assessments"
        )
    
    # TODO: Add permission checks for parents and counselors
    
    # Build questions with answers
    questions_with_answers = []
    for i, answer_value in enumerate(assessment.answers):
        question = GAD7_QUESTIONS_VI[i]
        answer_option = GAD7_ANSWER_OPTIONS_VI[answer_value]
        questions_with_answers.append({
            "question_id": question["id"],
            "question_text": question["text"],
            "answer_value": answer_value,
            "answer_text": answer_option["text"]
        })
    
    # Get severity info
    severity_info = get_severity_level(assessment.total_score)
    
    # Build response dict manually to include user_id
    detail_dict = {
        "id": assessment.id,
        "user_id": student.user_id,
        "answers": assessment.answers,
        "total_score": assessment.total_score,
        "severity_level": assessment.severity_level,
        "created_at": assessment.created_at,
        "analysis": assessment.analysis,
        "recommendations": assessment.recommendations,
        "functional_impairment": assessment.functional_impairment,
        "notes": assessment.notes,
        "questions_with_answers": questions_with_answers,
        "severity_info": severity_info
    }
    
    return AssessmentDetail(**detail_dict)


@router.get("/questions/list")
async def get_gad7_questions(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get GAD-7 questions in Vietnamese
    
    Returns the official GAD-7 questionnaire with:
    - 7 main questions
    - Answer options (0-3)
    - Functional impairment question
    - Instructions
    """
    from app.core.constants import (
        GAD7_INTRO_VI,
        GAD7_INSTRUCTION_VI,
        GAD7_FUNCTIONAL_QUESTION_VI,
        GAD7_FUNCTIONAL_OPTIONS_VI
    )
    
    return {
        "intro": GAD7_INTRO_VI,
        "instruction": GAD7_INSTRUCTION_VI,
        "questions": GAD7_QUESTIONS_VI,
        "answer_options": GAD7_ANSWER_OPTIONS_VI,
        "functional_question": GAD7_FUNCTIONAL_QUESTION_VI,
        "functional_options": GAD7_FUNCTIONAL_OPTIONS_VI
    }
