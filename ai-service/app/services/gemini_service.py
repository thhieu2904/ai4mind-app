"""
Gemini AI Service - Interface với Google Gemini API
Xử lý chat, phân tích GAD-7, và tạo recommendations
"""
import google.generativeai as genai
from typing import List, Dict, Optional
from app.core.config import settings


class GeminiService:
    """
    Service để tương tác với Google Gemini API
    """
    
    def __init__(self):
        """Initialize Gemini API"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def chat(self, message: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Chat với Gemini AI
        
        Args:
            message: User message
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            AI response text
        """
        try:
            # Build conversation context
            if conversation_history:
                # Format history for Gemini
                chat = self.model.start_chat(history=[
                    {
                        "role": "user" if msg["role"] == "user" else "model",
                        "parts": [msg["content"]]
                    }
                    for msg in conversation_history
                ])
                response = chat.send_message(message)
            else:
                # Single message without history
                response = self.model.generate_content(message)
            
            return response.text
        
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def analyze_gad7(self, answers: Dict[int, int], total_score: int) -> Dict[str, str]:
        """
        Phân tích kết quả GAD-7 assessment
        
        Args:
            answers: Dict of question_id: score (0-3)
            total_score: Total score (0-21)
        
        Returns:
            Dict with "analysis" and "recommendations"
        """
        # Determine severity
        if total_score <= 4:
            severity = "minimal anxiety (lo âu tối thiểu)"
        elif total_score <= 9:
            severity = "mild anxiety (lo âu nhẹ)"
        elif total_score <= 14:
            severity = "moderate anxiety (lo âu trung bình)"
        else:
            severity = "severe anxiety (lo âu nặng)"
        
        # Create prompt for Gemini
        prompt = f"""
Bạn là chuyên gia tâm lý học chuyên về sức khỏe tâm thần sinh viên.

Một sinh viên vừa hoàn thành bài đánh giá GAD-7 (Generalized Anxiety Disorder 7-item scale) với các kết quả sau:

Điểm số: {total_score}/21 điểm
Mức độ: {severity}

Chi tiết câu trả lời (scale 0-3: Không bao giờ, Vài ngày, Hơn một nửa số ngày, Gần như mỗi ngày):
{self._format_gad7_answers(answers)}

Hãy cung cấp:
1. **Phân tích ngắn gọn** về tình trạng tâm lý của sinh viên (2-3 câu)
2. **Khuyến nghị cụ thể** để cải thiện tình trạng (3-5 gợi ý thực tế)

Viết bằng tiếng Việt, giọng điệu ấm áp, khuyến khích và chuyên nghiệp.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Parse response into analysis and recommendations
            # Simple split - có thể improve parsing logic
            parts = result_text.split("**Khuyến nghị")
            
            analysis = parts[0].replace("**Phân tích", "").strip()
            recommendations = parts[1].strip() if len(parts) > 1 else ""
            
            return {
                "analysis": analysis,
                "recommendations": recommendations
            }
        
        except Exception as e:
            # Fallback if Gemini fails
            return {
                "analysis": f"Kết quả đánh giá cho thấy mức độ {severity}.",
                "recommendations": "Hãy tham khảo ý kiến chuyên gia tâm lý nếu cảm thấy cần thiết."
            }
    
    def _format_gad7_answers(self, answers: Dict[int, int]) -> str:
        """Format GAD-7 answers for prompt"""
        questions = {
            1: "Cảm thấy lo lắng, bồn chồn hoặc căng thẳng",
            2: "Không thể ngừng lo lắng hoặc kiểm soát sự lo lắng",
            3: "Lo lắng quá nhiều về những việc khác nhau",
            4: "Khó thư giãn",
            5: "Bồn chồn đến mức khó ngồi yên",
            6: "Dễ khó chịu hoặc cáu gắt",
            7: "Cảm thấy sợ hãi như thể điều gì đó tồi tệ sắp xảy ra"
        }
        
        score_labels = {0: "Không bao giờ", 1: "Vài ngày", 2: "Hơn một nửa", 3: "Gần như mỗi ngày"}
        
        result = []
        for q_id, score in answers.items():
            question = questions.get(q_id, f"Câu hỏi {q_id}")
            label = score_labels.get(score, "N/A")
            result.append(f"- {question}: {label} ({score} điểm)")
        
        return "\n".join(result)
    
    async def generate_conversation_title(self, first_message: str) -> str:
        """
        Tạo title cho conversation dựa trên message đầu tiên
        
        Args:
            first_message: First user message
        
        Returns:
            Short conversation title (max 50 chars)
        """
        prompt = f"""
Tạo một tiêu đề ngắn gọn (tối đa 6-7 từ) cho cuộc trò chuyện dựa trên tin nhắn đầu tiên:

"{first_message}"

Chỉ trả về tiêu đề, không có dấu ngoặc kép hay giải thích.
"""
        
        try:
            response = self.model.generate_content(prompt)
            title = response.text.strip().strip('"').strip("'")
            return title[:50]  # Limit to 50 chars
        except:
            # Fallback: use first 50 chars of message
            return first_message[:50] + "..." if len(first_message) > 50 else first_message


# Global instance
gemini_service = GeminiService()
