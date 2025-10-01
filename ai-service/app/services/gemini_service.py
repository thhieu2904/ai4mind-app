"""
Gemini AI Service - Interface với Google Gemini API
Xử lý chat, phân tích GAD-7, và tạo recommendations
"""
import asyncio
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
                response = await asyncio.to_thread(chat.send_message, message)
            else:
                # Single message without history
                response = await asyncio.to_thread(self.model.generate_content, message)
            
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

Hãy cung cấp phản hồi theo định dạng sau (BẮT BUỘC tuân thủ format):

PHÂN TÍCH:
[Viết 2-3 câu phân tích ngắn gọn về tình trạng tâm lý của sinh viên]

KHUYẾN NGHỊ:
1. [Khuyến nghị cụ thể thứ nhất]
2. [Khuyến nghị cụ thể thứ hai]
3. [Khuyến nghị cụ thể thứ ba]
4. [Khuyến nghị cụ thể thứ tư - nếu cần]
5. [Khuyến nghị cụ thể thứ năm - nếu cần]

Viết bằng tiếng Việt, giọng điệu ấm áp, khuyến khích và chuyên nghiệp.
Mỗi khuyến nghị nên là một câu hoàn chỉnh, thực tế và dễ thực hiện.
"""
        
        try:
            # Run sync Gemini API call in thread pool to not block event loop
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            result_text = response.text
            
            # Parse response - split by section markers
            analysis = ""
            recommendations = []
            
            # Split by PHÂN TÍCH and KHUYẾN NGHỊ sections
            if "PHÂN TÍCH:" in result_text and "KHUYẾN NGHỊ:" in result_text:
                parts = result_text.split("KHUYẾN NGHỊ:")
                
                # Extract analysis
                analysis_part = parts[0].replace("PHÂN TÍCH:", "").strip()
                analysis = analysis_part
                
                # Extract recommendations from numbered list
                if len(parts) > 1:
                    rec_text = parts[1].strip()
                    import re
                    # Match numbered items (1., 2., etc.)
                    rec_items = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\Z)', rec_text, re.DOTALL)
                    recommendations = [r.strip() for r in rec_items if r.strip()]
            
            # Fallback: try old format with ** markers
            elif "**Phân tích" in result_text or "**Khuyến nghị" in result_text:
                parts = result_text.split("**Khuyến nghị")
                analysis = parts[0].replace("**Phân tích", "").replace("**:", "").strip()
                if len(parts) > 1:
                    rec_text = parts[1].strip()
                    import re
                    rec_items = re.split(r'\n\s*[\d]+\.\s*|\n\s*[-*]\s*', rec_text)
                    recommendations = [r.strip() for r in rec_items if r.strip() and len(r.strip()) > 10]
            
            # If parsing completely failed, use entire response as analysis
            if not analysis:
                analysis = result_text.strip()
            
            # If no recommendations found, provide fallback
            if not recommendations:
                if total_score <= 4:
                    recommendations = ["Duy trì lối sống lành mạnh và kỹ thuật giảm căng thẳng."]
                elif total_score <= 9:
                    recommendations = ["Thực hành kỹ thuật thư giãn hàng ngày.", "Tham khảo tài liệu tự chăm sóc sức khỏe tâm thần."]
                elif total_score <= 14:
                    recommendations = ["Nên tham khảo ý kiến chuyên gia tâm lý.", "Thực hành kỹ thuật quản lý lo âu hàng ngày."]
                else:
                    recommendations = ["Nên gặp chuyên gia sức khỏe tâm thần ngay.", "Tìm kiếm hỗ trợ từ gia đình và bạn bè."]
            
            return {
                "analysis": analysis,
                "recommendations": recommendations
            }
        
        except Exception as e:
            print(f"Gemini API error in analyze_gad7: {e}")
            import traceback
            traceback.print_exc()
            # Fallback if Gemini fails
            return {
                "analysis": f"Kết quả đánh giá cho thấy mức độ {severity}.",
                "recommendations": ["Hãy tham khảo ý kiến chuyên gia tâm lý nếu cảm thấy cần thiết."]
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
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            title = response.text.strip().strip('"').strip("'")
            return title[:50]  # Limit to 50 chars
        except:
            # Fallback: use first 50 chars of message
            return first_message[:50] + "..." if len(first_message) > 50 else first_message


# Global instance
gemini_service = GeminiService()
