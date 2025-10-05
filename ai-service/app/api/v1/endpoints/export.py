"""
Export API endpoints - Xuất dữ liệu cá nhân của student ra Excel
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import io
import json
from datetime import datetime
import logging

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....models.student import Student
from ....models.assessment import Assessment
from ....models.voice_analysis import VoiceAnalysis
from ....models.ai_chat import AIConversation, AIMessage

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/user-data")
async def export_user_data(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Export full user data to Excel file with multiple sheets
    - Sheet 1: Thông tin cá nhân
    - Sheet 2: Lịch sử đánh giá sức khỏe
    - Sheet 3: Phân tích giọng nói
    - Sheet 4: Lịch sử chat AI
    - Sheet 5: Thống kê tổng quan
    """
    try:
        # Get student info
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # 1. User Info Sheet
        user_info_data = [
            {
                "Họ và tên": current_user.full_name,
                "Email": current_user.email,
                "Mã sinh viên": student.student_code or "N/A",
                "Ngày sinh": student.date_of_birth.strftime("%d/%m/%Y")
                if student.date_of_birth
                else "N/A",
                "Giới tính": student.gender or "N/A",
                "Số điện thoại": student.phone_number or "N/A",
                "Địa chỉ": student.address or "N/A",
                "Trường": student.university or "N/A",
                "Ngành học": student.major or "N/A",
                "Trình độ": student.education_level or "N/A",
                "Khóa/Lớp": student.grade or "N/A",
                "Ngày tạo tài khoản": current_user.created_at.strftime(
                    "%d/%m/%Y %H:%M"
                )
                if current_user.created_at
                else "N/A",
                "Đăng nhập lần cuối": current_user.last_login.strftime(
                    "%d/%m/%Y %H:%M"
                )
                if current_user.last_login
                else "Chưa có",
            }
        ]

        # 2. Assessments Sheet - CHỈ XUẤT DATA CÓ GIÁ TRỊ
        assessments = (
            db.query(Assessment)
            .filter(Assessment.student_id == student.id)
            .order_by(Assessment.created_at.desc())
            .all()
        )

        assessments_data = []
        for ass in assessments:
            # Parse answers JSON to show detailed responses
            import json
            answers_dict = json.loads(ass.answers) if isinstance(ass.answers, str) else ass.answers
            
            # Parse recommendations
            recommendations_text = ""
            if ass.recommendations:
                recs = json.loads(ass.recommendations) if isinstance(ass.recommendations, str) else ass.recommendations
                if isinstance(recs, list):
                    recommendations_text = "; ".join(recs)
                elif isinstance(recs, dict):
                    recommendations_text = str(recs)
            
            assessments_data.append(
                {
                    "Ngày đánh giá": ass.created_at.strftime("%d/%m/%Y %H:%M")
                    if ass.created_at
                    else "N/A",
                    "Tổng điểm": ass.total_score,
                    "Mức độ nghiêm trọng": ass.severity_level,
                    "Mức độ suy giảm chức năng": ass.functional_impairment or 0,
                    "Số câu trả lời": len(answers_dict) if answers_dict else 0,
                    "Phân tích chi tiết": ass.analysis or "Không có",
                    "Khuyến nghị": recommendations_text or "Không có",
                    "Ghi chú bổ sung": ass.notes or "Không có",
                }
            )

        # 3. Voice Analyses Sheet - CHỈ XUẤT DATA QUAN TRỌNG
        voice_analyses = (
            db.query(VoiceAnalysis)
            .filter(VoiceAnalysis.student_id == student.id)
            .order_by(VoiceAnalysis.created_at.desc())
            .all()
        )

        voice_data = []
        for va in voice_analyses:
            # Parse detected emotions JSON
            emotions_text = ""
            if va.detected_emotions:
                emotions = json.loads(va.detected_emotions) if isinstance(va.detected_emotions, str) else va.detected_emotions
                if isinstance(emotions, dict):
                    emotions_text = ", ".join([f"{k}: {v}" for k, v in emotions.items()])
            
            # Parse keywords
            keywords_text = ""
            if va.keywords:
                keywords = json.loads(va.keywords) if isinstance(va.keywords, str) else va.keywords
                if isinstance(keywords, list):
                    keywords_text = ", ".join(keywords[:10])  # Top 10 keywords
            
            voice_data.append(
                {
                    "Ngày phân tích": va.created_at.strftime("%d/%m/%Y %H:%M")
                    if va.created_at
                    else "N/A",
                    "Thời lượng ghi âm (giây)": round(va.audio_duration, 2) if va.audio_duration else 0,
                    "Nội dung phân tích": va.transcription or "Không có transcript",
                    "Ngôn ngữ": va.transcription_language or "N/A",
                    "Độ tin cậy transcript (%)": f"{va.transcription_confidence * 100:.1f}%"
                    if va.transcription_confidence
                    else "N/A",
                    "Cảm xúc phát hiện": emotions_text or "Không phát hiện",
                    "Cảm xúc chủ đạo": va.dominant_emotion or "N/A",
                    "Độ tin cậy cảm xúc (%)": f"{va.emotion_confidence * 100:.1f}%"
                    if va.emotion_confidence
                    else "N/A",
                    "Điểm sentiment": f"{va.sentiment_score:.2f}"
                    if va.sentiment_score
                    else "N/A",
                    "Số từ": va.word_count or 0,
                    "Từ khóa chính": keywords_text or "Không có",
                    "Trạng thái xử lý": va.processing_status or "N/A",
                    "Thời gian xử lý (giây)": round(va.processing_time, 2) if va.processing_time else 0,
                    "Phân tích toàn diện": va.comprehensive_analysis[:300] + "..."
                    if va.comprehensive_analysis and len(va.comprehensive_analysis) > 300
                    else (va.comprehensive_analysis or "Không có"),
                }
            )

        # 4. AI Conversations Sheet - CHỈ XUẤT DATA QUAN TRỌNG
        ai_conversations = (
            db.query(AIConversation)
            .filter(AIConversation.student_id == student.id)
            .order_by(AIConversation.created_at.desc())
            .all()
        )

        ai_chat_data = []
        for conv in ai_conversations:
            messages = (
                db.query(AIMessage)
                .filter(AIMessage.conversation_id == conv.id)
                .order_by(AIMessage.created_at)
                .all()
            )

            # Group messages by conversation
            conversation_content = []
            for msg in messages:
                role_label = "🧑 Bạn" if msg.role == "user" else "🤖 AI"
                conversation_content.append(f"{role_label}: {msg.content}")
            
            # Combine all messages into one readable format
            full_conversation = "\n\n".join(conversation_content)
            
            # Create one row per conversation with full content
            ai_chat_data.append(
                {
                    "ID Cuộc hội thoại": conv.id,
                    "Tiêu đề": conv.title or "Không có tiêu đề",
                    "Ngày bắt đầu": conv.created_at.strftime("%d/%m/%Y %H:%M")
                    if conv.created_at
                    else "N/A",
                    "Số tin nhắn": len(messages),
                    "Liên quan đến đánh giá": conv.latest_assessment_id or "Không",
                    "Nội dung đầy đủ": full_conversation if full_conversation else "Không có tin nhắn",
                    "Trạng thái": "Đang hoạt động" if conv.is_active else "Đã kết thúc",
                }
            )

        # 5. Summary Statistics Sheet
        summary_data = [
            {
                "Chỉ số": "Tổng số lần đánh giá",
                "Giá trị": len(assessments),
            },
            {
                "Chỉ số": "Tổng số phân tích giọng nói",
                "Giá trị": len(voice_analyses),
            },
            {
                "Chỉ số": "Tổng số cuộc hội thoại AI",
                "Giá trị": len(ai_conversations),
            },
            {
                "Chỉ số": "Tổng số tin nhắn AI",
                "Giá trị": len(ai_chat_data),
            },
            {
                "Chỉ số": "Đánh giá gần nhất",
                "Giá trị": assessments[0].created_at.strftime("%d/%m/%Y")
                if assessments
                else "Chưa có",
            },
            {
                "Chỉ số": "Mức độ gần nhất",
                "Giá trị": assessments[0].severity_level if assessments else "N/A",
            },
        ]

        # Create Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Sheet 1: User Info (always present)
            df_user = pd.DataFrame(user_info_data)
            df_user.to_excel(writer, sheet_name="Thông tin cá nhân", index=False)

            # Sheet 2: Assessments (show empty sheet if no data)
            if assessments_data:
                df_assessments = pd.DataFrame(assessments_data)
            else:
                df_assessments = pd.DataFrame([{
                    "Ngày đánh giá": "Chưa có dữ liệu",
                    "Tổng điểm": "",
                    "Mức độ": "",
                    "Suy giảm chức năng": "",
                    "Phân tích": "",
                    "Ghi chú": "",
                }])
            df_assessments.to_excel(writer, sheet_name="Lịch sử đánh giá", index=False)

            # Sheet 3: Voice Analyses (show empty sheet if no data)
            if voice_data:
                df_voice = pd.DataFrame(voice_data)
            else:
                df_voice = pd.DataFrame([{
                    "Ngày phân tích": "Chưa có dữ liệu",
                    "Thời lượng (giây)": "",
                    "Nội dung": "",
                    "Ngôn ngữ": "",
                    "Độ tin cậy": "",
                    "Cảm xúc chủ đạo": "",
                    "Điểm cảm xúc": "",
                    "Số từ": "",
                    "Trạng thái": "",
                }])
            df_voice.to_excel(writer, sheet_name="Phân tích giọng nói", index=False)

            # Sheet 4: AI Chats (show empty sheet if no data)
            if ai_chat_data:
                df_ai_chat = pd.DataFrame(ai_chat_data)
            else:
                df_ai_chat = pd.DataFrame([{
                    "Cuộc hội thoại": "Chưa có dữ liệu",
                    "Thời gian": "",
                    "Vai trò": "",
                    "Nội dung": "",
                }])
            df_ai_chat.to_excel(writer, sheet_name="Lịch sử AI Chat", index=False)

            # Sheet 5: Summary (always present)
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name="Thống kê tổng quan", index=False)

        output.seek(0)

        # Generate filename
        filename = f"AI4Mind_Data_{student.student_code or current_user.id}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        logger.info(f"Export successful for student {student.id}, filename: {filename}")

        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
