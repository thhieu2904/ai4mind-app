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
    
    async def analyze_gad7(self, answers: List[Dict], total_score: int) -> Dict[str, any]:
        """
        Phân tích kết quả GAD-7 assessment
        
        Args:
            answers: List of dicts with question, answer, score
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
    
    def _format_gad7_answers(self, answers: List[Dict]) -> str:
        """
        Format GAD-7 answers for prompt
        
        Args:
            answers: List of dicts with 'question', 'answer', 'score'
        
        Returns:
            Formatted string
        """
        if not answers:
            return "No answers provided"
        
        result = []
        for item in answers:
            question = item.get("question", "Unknown question")
            answer = item.get("answer", "N/A")
            score = item.get("score", 0)
            result.append(f"- {question}: {answer} ({score} điểm)")
        
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
    
    async def analyze_combined(self, gad7_data: dict, voice_data: dict) -> dict:
        """
        Combined analysis using both GAD-7 and voice data (RECOMMENDED APPROACH).
        
        This provides:
        1. Cross-validation between objective (GAD-7) and subjective (voice)
        2. Detection of emotional suppression (low score but high anxiety in voice)
        3. Richer context for personalized recommendations
        
        Args:
            gad7_data: Dict with answers, total_score, severity, functional_impairment
            voice_data: Dict with transcript, emotions, audio_features, text_analysis
        
        Returns:
            Dict with "analysis" (str) and "recommendations" (list)
        """
        # Extract data
        score = gad7_data["total_score"]
        severity = gad7_data["severity"]
        answers = gad7_data["answers"]
        
        transcript = voice_data.get("transcript", "")
        emotions = voice_data.get("emotions", {})
        audio_features = voice_data.get("audio_features", {})
        text_analysis = voice_data.get("text_analysis", {})
        
        # Build enhanced prompt
        prompt = f"""
Bạn là chuyên gia tâm lý lâm sàng chuyên về sức khỏe tâm thần sinh viên. Hãy phân tích tổng hợp tình trạng tâm lý dựa trên:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PHẦN 1: BẢNG CÂU HỎI GAD-7 (Objective Assessment)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Điểm số: {score}/21 - Mức độ: {severity}
Câu trả lời chi tiết:
1. Cảm thấy lo lắng, bồn chồn: {answers[0]}/3
2. Không kiểm soát được lo lắng: {answers[1]}/3
3. Lo lắng quá nhiều về nhiều thứ: {answers[2]}/3
4. Khó thư giãn: {answers[3]}/3
5. Bồn chồn khó ngồi yên: {answers[4]}/3
6. Dễ khó chịu hoặc cáu gắt: {answers[5]}/3
7. Cảm thấy sợ hãi: {answers[6]}/3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎤 PHẦN 2: PHÂN TÍCH GIỌNG NÓI (Subjective Expression)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nội dung chia sẻ:
"{transcript}"

Cảm xúc phát hiện từ giọng nói:
- Lo âu (Anxiety): {emotions.get('anxiety', 0):.1%}
- Buồn bã (Sadness): {emotions.get('sadness', 0):.1%}
- Giận dữ (Anger): {emotions.get('anger', 0):.1%}
- Trung tính (Neutral): {emotions.get('neutral', 0):.1%}

Đặc điểm giọng nói:
- Cao độ trung bình: {audio_features.get('pitch', {}).get('mean', 0):.1f} Hz
- Độ ổn định giọng: {audio_features.get('voice_stability', 0):.2f}
- Năng lượng trung bình: {audio_features.get('energy', {}).get('mean', 0):.2f}
- Tốc độ nói: {audio_features.get('speech_rate', 0):.1f} từ/phút
- Số lần ngắt quãng: {audio_features.get('pause_count', 0)} lần
- Thời gian ngắt quãng: {audio_features.get('pause_duration', 0):.1f} giây

Phân tích văn bản:
- Cảm xúc văn bản (Sentiment): {text_analysis.get('sentiment_score', 0):.2f} (-1 to 1)
- Từ khóa tâm lý: {', '.join([k.get('word', '') for k in text_analysis.get('keywords', [])[:5]])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ PHẦN 3: CROSS-VALIDATION (Quan trọng!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hãy kiểm tra sự nhất quán giữa GAD-7 và giọng nói:

1. **Nhất quán (Consistent)**:
   - VD: GAD-7 = cao (15+) VÀ giọng nói có anxiety cao (>60%)
   → Xác nhận tình trạng lo âu đáng kể

2. **Không nhất quán (Discrepancy)**:
   - VD: GAD-7 = thấp (<10) NHƯNG giọng nói có anxiety cao (>60%)
   → Có thể đang che giấu cảm xúc hoặc chưa nhận thức được
   
   - VD: GAD-7 = cao (15+) NHƯNG giọng nói bình thường
   → Có thể đang cố gắng kiểm soát hoặc đã quen với trạng thái lo âu

3. **Dấu hiệu cần chú ý**:
   - Pause quá nhiều (>5 lần) → Khó diễn đạt, có thể stress cao
   - Giọng không ổn định (stability <0.5) → Cảm xúc dao động
   - Sentiment âm (<-0.3) + GAD-7 cao → Nguy cơ depression
   - Từ khóa tiêu cực nhiều → Cần hỗ trợ tâm lý sâu hơn

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 YÊU CẦU OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hãy đưa ra phân tích bằng tiếng Việt, bao gồm:

1. **Tổng quan (2-3 câu)**:
   - Đánh giá tổng thể về tình trạng tâm lý
   - Nhận định về sự nhất quán giữa GAD-7 và giọng nói

2. **Phân tích chi tiết (3-4 đoạn)**:
   - Phân tích GAD-7: Điểm số nào cao? Ý nghĩa?
   - Phân tích giọng nói: Cảm xúc gì nổi bật? Đặc điểm gì đáng chú ý?
   - Cross-validation: Có nhất quán không? Nếu không, giải thích tại sao?
   - Dấu hiệu cần lưu ý (nếu có)

3. **Gợi ý hỗ trợ (3-5 gợi ý cụ thể)**:
   - Dựa trên CẢ GAD-7 VÀ giọng nói
   - Cá nhân hóa theo nội dung chia sẻ
   - Thực tế, dễ thực hiện
   - Có mức độ ưu tiên

Định dạng JSON:
{{
    "analysis": "...", 
    "recommendations": ["...", "...", "..."]
}}
"""
        
        try:
            import json
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            text = response.text.strip()
            
            # Parse JSON from response
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            
            return {
                "analysis": result.get("analysis", ""),
                "recommendations": result.get("recommendations", [])
            }
            
        except Exception as e:
            print(f"Gemini combined analysis error: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to simple analysis
            return {
                "analysis": f"Phân tích tổng hợp: Điểm GAD-7 là {score}/21 ({severity}). "
                           f"Cảm xúc từ giọng nói cho thấy lo âu {emotions.get('anxiety', 0):.0%}, "
                           f"buồn bã {emotions.get('sadness', 0):.0%}. Cần đánh giá thêm với tư vấn viên.",
                "recommendations": [
                    "Gặp tư vấn viên để được hỗ trợ chi tiết hơn",
                    "Thực hành các kỹ thuật thư giãn hàng ngày như hít thở sâu, thiền",
                    "Theo dõi tình trạng trong thời gian tới và ghi chép cảm xúc",
                    "Tìm kiếm hỗ trợ từ bạn bè, gia đình khi cần"
                ]
            }


# Global instance
gemini_service = GeminiService()

