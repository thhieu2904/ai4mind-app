# Fix: 500 Internal Server Error - Pydantic Validation & Gemini Type Mismatch

## Vấn đề

Backend trả về **500 Internal Server Error** với 2 lỗi:

### 1. Pydantic Validation Error

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for AssessmentResponse
student_id
  Field required [type=missing, input_value={'id': 26, 'user_id': 56,...}, input_type=dict]
```

### 2. Gemini Analysis Error

```
Gemini analysis error: 'list' object has no attribute 'items'
```

## Nguyên nhân

### Lỗi 1: student_id vs user_id Mismatch

- **AssessmentResponse schema** yêu cầu field: `student_id` ✅
- **Backend code** đang trả về: `user_id` ❌
  ```python
  assessment_dict = {
      "id": assessment.id,
      "user_id": current_user.id,  # SAI! Schema cần student_id
      ...
  }
  ```

### Lỗi 2: Type Mismatch trong Gemini Service

- **Gemini function signature** expect: `answers: Dict[int, int]` ❌
- **Backend code** truyền vào: `answers_with_questions` là **List[Dict]** ❌

  ```python
  # Backend tạo list
  answers_with_questions = [
      {"question": "...", "answer": "...", "score": 1},
      ...
  ]

  # Gemini expect dict
  async def analyze_gad7(self, answers: Dict[int, int], ...)
  ```

- **Internal method** `_format_gad7_answers` cố gắng gọi `.items()` trên list → AttributeError

## Giải pháp ✅

### Fix 1: assessments.py - Dùng student_id thay vì user_id

**Before:**

```python
# Return response with user_id for frontend
assessment_dict = {
    "id": assessment.id,
    "user_id": current_user.id,  # SAI!
    "answers": assessment.answers,
    "total_score": assessment.total_score,
    ...
}
```

**After:**

```python
# Return response with student_id (not user_id)
assessment_dict = {
    "id": assessment.id,
    "student_id": assessment.student_id,  # Lấy từ assessment object
    "answers": assessment.answers,
    "total_score": assessment.total_score,
    ...
}
```

### Fix 2: gemini_service.py - Update Type Annotations

**Before:**

```python
async def analyze_gad7(self, answers: Dict[int, int], total_score: int) -> Dict[str, str]:
    """
    Args:
        answers: Dict of question_id: score (0-3)  # SAI!
    """
```

**After:**

```python
async def analyze_gad7(self, answers: List[Dict], total_score: int) -> Dict[str, any]:
    """
    Args:
        answers: List of dicts with question, answer, score  # ĐÚNG!
    """
```

### Fix 3: gemini_service.py - Update \_format_gad7_answers

**Before:**

```python
def _format_gad7_answers(self, answers: Dict[int, int]) -> str:
    """Format GAD-7 answers for prompt"""
    result = []
    for q_id, score in answers.items():  # SAI! List không có .items()
        question = questions.get(q_id, f"Câu hỏi {q_id}")
        ...
```

**After:**

```python
def _format_gad7_answers(self, answers: List[Dict]) -> str:
    """
    Format GAD-7 answers for prompt

    Args:
        answers: List of dicts with 'question', 'answer', 'score'
    """
    result = []
    for item in answers:  # ĐÚNG! Iterate over list
        question = item.get("question", "Unknown question")
        answer = item.get("answer", "N/A")
        score = item.get("score", 0)
        result.append(f"- {question}: {answer} ({score} điểm)")

    return "\n".join(result)
```

## Kết quả

### Before (Error):

```
INFO: "POST /api/v1/assessments/ HTTP/1.1" 500 Internal Server Error
Gemini analysis error: 'list' object has no attribute 'items'
pydantic_core.ValidationError: student_id Field required
```

### After (Success):

```
INFO: "POST /api/v1/assessments/ HTTP/1.1" 200 OK
✅ Gemini analysis chạy thành công
✅ Assessment saved to database
✅ Response trả về đúng schema
```

## Files Changed

1. **ai-service/app/api/v1/endpoints/assessments.py**

   - Line ~118: Changed `user_id` → `student_id`

2. **ai-service/app/services/gemini_service.py**
   - Line ~56: Updated `analyze_gad7` signature: `Dict[int, int]` → `List[Dict]`
   - Line ~170: Rewrote `_format_gad7_answers` to handle `List[Dict]` instead of `Dict[int, int]`

## Kiểm tra

Sau khi fix, flow sẽ hoạt động:

1. ✅ Frontend submit GAD-7 answers
2. ✅ Backend tính total_score và severity
3. ✅ Gemini phân tích với đúng data format
4. ✅ Assessment được lưu vào database
5. ✅ Response trả về với student_id đúng schema
6. ✅ Frontend nhận kết quả và navigate to ResultsPage

## Type Safety Lesson

Lỗi này xảy ra vì:

- Python không enforce type hints at runtime
- Function signature nói `Dict` nhưng code truyền `List`
- Chỉ fail khi runtime cố gắng call `.items()` trên list

**Best practice:**

- ✅ Luôn kiểm tra type hints khi refactor
- ✅ Sử dụng static type checker (mypy, pyright)
- ✅ Unit tests cho các service functions
- ✅ Validate input data structure trước khi process
