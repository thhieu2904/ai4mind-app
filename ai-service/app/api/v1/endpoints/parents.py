"""
Parent management endpoints
Linked children and child assessments for parent role.
"""
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_parent_profile, get_parent_student_ids
from app.core.database import get_db
from app.core.security import require_roles
from app.models.assessment import Assessment
from app.models.parent import ParentConsent
from app.models.student import Student
from app.models.user import User
from app.schemas.assessment import AssessmentListResponse, AssessmentResponse


router = APIRouter()


class ParentChildLatestAssessment(BaseModel):
    id: int
    total_score: int
    severity_level: str
    created_at: datetime


class ParentChildItem(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    student_code: Optional[str] = None
    university: Optional[str] = None
    major: Optional[str] = None
    is_emergency_contact: bool
    has_data_consent: bool
    total_assessments: int = 0
    latest_assessment: Optional[ParentChildLatestAssessment] = None


class ParentChildrenResponse(BaseModel):
    total_children: int
    children: List[ParentChildItem]


@router.get("/me/children", response_model=ParentChildrenResponse)
async def list_my_children(
    current_user: User = Depends(require_roles(["parent"])),
    db: Session = Depends(get_db),
) -> Any:
    """
    List children that parent can access.

    Access sources:
    - Student.emergency_contact_parent_id == current parent
    - Approved consent in parent_consents
    """
    parent = get_parent_profile(db=db, user_id=current_user.id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent profile not found",
        )

    accessible_student_ids = get_parent_student_ids(db=db, parent_id=parent.id)
    if not accessible_student_ids:
        return ParentChildrenResponse(total_children=0, children=[])

    students = (
        db.query(Student)
        .options(joinedload(Student.user))
        .filter(Student.id.in_(accessible_student_ids))
        .order_by(Student.id.desc())
        .all()
    )

    approved_consent_student_ids = {
        student_id
        for (student_id,) in db.query(ParentConsent.student_id)
        .filter(
            ParentConsent.parent_id == parent.id,
            ParentConsent.is_approved == 1,
        )
        .all()
    }

    assessment_counts = {
        student_id: total
        for student_id, total in db.query(
            Assessment.student_id,
            func.count(Assessment.id),
        )
        .filter(Assessment.student_id.in_(accessible_student_ids))
        .group_by(Assessment.student_id)
        .all()
    }

    latest_rows = (
        db.query(Assessment)
        .filter(Assessment.student_id.in_(accessible_student_ids))
        .order_by(Assessment.student_id.asc(), desc(Assessment.created_at))
        .all()
    )
    latest_assessment_map: dict[int, Assessment] = {}
    for assessment in latest_rows:
        latest_assessment_map.setdefault(assessment.student_id, assessment)

    children: List[ParentChildItem] = []
    for student in students:
        latest = latest_assessment_map.get(student.id)
        latest_payload = None
        if latest:
            latest_payload = ParentChildLatestAssessment(
                id=latest.id,
                total_score=latest.total_score,
                severity_level=latest.severity_level,
                created_at=latest.created_at,
            )

        children.append(
            ParentChildItem(
                id=student.id,
                user_id=student.user_id,
                full_name=student.user.full_name if student.user else None,
                email=student.user.email if student.user else None,
                student_code=student.student_code,
                university=student.university,
                major=student.major,
                is_emergency_contact=student.emergency_contact_parent_id == parent.id,
                has_data_consent=student.id in approved_consent_student_ids,
                total_assessments=assessment_counts.get(student.id, 0),
                latest_assessment=latest_payload,
            )
        )

    return ParentChildrenResponse(total_children=len(children), children=children)


@router.get(
    "/me/children/{student_id}/assessments",
    response_model=AssessmentListResponse,
)
async def list_child_assessments(
    student_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_roles(["parent"])),
    db: Session = Depends(get_db),
) -> Any:
    """
    List child assessments for a parent.

    Parent can only query children linked by emergency contact or approved consent.
    """
    parent = get_parent_profile(db=db, user_id=current_user.id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent profile not found",
        )

    accessible_student_ids = get_parent_student_ids(db=db, parent_id=parent.id)
    if student_id not in accessible_student_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Student is not linked to your parent account",
        )

    student_exists = db.query(Student.id).filter(Student.id == student_id).first()
    if not student_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    query = (
        db.query(Assessment)
        .filter(Assessment.student_id == student_id)
        .order_by(desc(Assessment.created_at))
    )

    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    responses = [
        AssessmentResponse(
            id=item.id,
            student_id=item.student_id,
            answers=item.answers,
            total_score=item.total_score,
            severity_level=item.severity_level,
            analysis=item.analysis,
            recommendations=item.recommendations,
            functional_impairment=item.functional_impairment,
            notes=item.notes,
            created_at=item.created_at,
        )
        for item in items
    ]

    total_pages = (total + page_size - 1) // page_size
    return AssessmentListResponse(
        items=responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
