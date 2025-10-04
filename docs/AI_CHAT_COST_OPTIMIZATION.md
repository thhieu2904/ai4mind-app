# 💰 OPTIMIZATION GUIDE - Giảm Chi Phí API

## ✅ Đã tối ưu (Current Design)

1. **History Limit: 6 messages**

   - Location: `ai_chat_service.py` line 128
   - Current: `.limit(6)`
   - Tokens saved: ~70% so với unlimited history

2. **Assessment Context: Lightweight**

   - Only send: score, severity, date
   - NOT sending: full analysis text, long recommendations
   - Tokens saved: ~80% so với full assessment

3. **No Redundant Calls**
   - Assessment loaded once per conversation
   - Cached in conversation.latest_assessment_id
   - No repeated DB queries

---

## 🔧 TỐI ƯU THÊM (Optional)

### Option 1: Giảm History Limit (Giảm 20-30%)

```python
# File: ai-service/app/services/ai_chat_service.py, line 128

# BEFORE (6 messages = ~300 tokens)
recent_messages = self.db.query(AIMessage).filter(
    AIMessage.conversation_id == conversation.id
).order_by(desc(AIMessage.created_at)).limit(6).all()

# AFTER (4 messages = ~200 tokens) ⚠️ Ít context hơn
recent_messages = self.db.query(AIMessage).filter(
    AIMessage.conversation_id == conversation.id
).order_by(desc(AIMessage.created_at)).limit(4).all()
```

**Trade-off:** AI sẽ nhớ ít hơn, context kém hơn

---

### Option 2: Summarize Long Messages (Giảm 10-15%)

```python
# Truncate very long messages before sending to API
for msg in recent_messages:
    content = msg.content
    if len(content) > 500:  # ~125 tokens
        content = content[:500] + "..."
    message_history.append({
        "role": msg.role,
        "content": content
    })
```

**Trade-off:** Mất context nếu user viết rất dài

---

### Option 3: Skip Assessment cho Minimal Severity (Giảm 5%)

```python
# Only send assessment if severity needs attention
assessment_data = None
if conversation.latest_assessment_id:
    assessment = self.db.query(Assessment).get(conversation.latest_assessment_id)
    # Only send if moderate/severe
    if assessment and assessment.severity_level in ['moderate', 'severe']:
        assessment_data = {...}
```

**Trade-off:** AI không biết về "minimal" assessments

---

### Option 4: Shorter System Prompt (Giảm 30% prompt cost)

```python
# File: ai-service/app/services/gemini_service.py
# Line ~250: _build_mental_health_system_prompt()

# BEFORE: ~800 tokens
system_instruction = """
[Very long detailed instructions...]
"""

# AFTER: ~500 tokens (condensed version)
system_instruction = """
Bạn là AI4Mind Assistant - trợ lý sức khỏe tinh thần cho sinh viên Việt Nam.

Vai trò:
- Lắng nghe, đồng cảm, hỗ trợ tâm lý
- KHÔNG chẩn đoán, KHÔNG kê đơn thuốc
- Khuyến khích tìm chuyên gia khi cần

Phong cách:
- Thân thiện, ấm áp, dễ hiểu
- Tiếng Việt đơn giản
- Emoji nhẹ nhàng (1-2 mỗi tin)

Khẩn cấp:
Nếu phát hiện ý định tự tử → Đề xuất hotline: 1800545475
"""
```

---

## 📊 SO SÁNH CHI PHÍ

### Gemini 1.5 Flash Pricing (Current Model)

- Input: $0.075 per 1M tokens ($0.000075 per 1K)
- Output: $0.30 per 1M tokens ($0.0003 per 1K)

### Ước tính với 1,000 messages/ngày:

| Thiết kế                | Tokens/msg | Cost/1000 msgs | Cost/tháng (30K msgs) |
| ----------------------- | ---------- | -------------- | --------------------- |
| **Current**             | 1,400      | $0.15          | **$4.50**             |
| Option 1 (4 history)    | 1,200      | $0.13          | $3.90                 |
| Option 4 (short prompt) | 1,000      | $0.11          | $3.30                 |
| ❌ Full history         | 5,000      | $0.53          | $15.90                |

**💡 Kết luận:** Thiết kế hiện tại **RẤT TỐT** (~$5/tháng cho 30K messages)

---

## 🎯 KHUYẾN NGHỊ

### Giữ nguyên thiết kế hiện tại nếu:

- ✅ User base < 500 người
- ✅ <30,000 messages/tháng
- ✅ Ưu tiên trải nghiệm tốt hơn chi phí

### Tối ưu thêm nếu:

- ❌ User base > 5,000 người
- ❌ >300,000 messages/tháng
- ❌ Budget < $50/tháng

---

## 📝 MONITORING (Future)

Thêm tracking để biết thực tế:

```python
# In ai_chat_service.py - send_message()
import time

start = time.time()
ai_response = await self.gemini.chat_with_mental_health_context(...)
duration = time.time() - start

# Log metrics
print(f"Gemini API call: {duration:.2f}s, "
      f"input_tokens: ~{len(str(context))//4}, "
      f"output_tokens: ~{len(ai_response)//4}")
```

---

**📌 TL;DR:** Thiết kế hiện tại **ĐÃ TỐI ƯU RẤT TỐT**. Không cần thay đổi gì!
