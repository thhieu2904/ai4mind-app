"""
Application Constants
GAD-7 Questions, Severity Levels, and Other Constants
"""

# ============================================
# GAD-7 (Generalized Anxiety Disorder - 7)
# Official Vietnamese Version
# ============================================

GAD7_INTRO_VI = """
Bảng câu hỏi về rối loạn lo âu nói chung (GAD-7 Vietnamese)

Các câu hỏi dưới đây hỏi về tần suất và mức độ nghiêm trọng của bạn 
có thể gặp các triệu chứng lo lắng trong hai tuần qua. 
Hãy giúp chúng tôi cung cấp cho bạn dịch vụ chăm sóc y tế tốt nhất 
bằng cách trả lời các câu hỏi sau.
"""

GAD7_INSTRUCTION_VI = "Trong 2 tuần qua, bạn có bị làm phiền bởi những vấn đề sau đây không?"

GAD7_QUESTIONS_VI = [
    {
        "id": 1,
        "text": "Cảm thấy lo lắng, căng thẳng hoặc bồn chồn",
        "en": "Feeling nervous, anxious or on edge"
    },
    {
        "id": 2,
        "text": "Không thể dừng lại hoặc kiểm soát được sự lo lắng",
        "en": "Not being able to stop or control worrying"
    },
    {
        "id": 3,
        "text": "Lo lắng quá nhiều về những điều khác nhau",
        "en": "Worrying too much about different things"
    },
    {
        "id": 4,
        "text": "Khó thư giãn",
        "en": "Trouble relaxing"
    },
    {
        "id": 5,
        "text": "Bồn chồn đến mức khó ngồi yên",
        "en": "Being so restless that it is hard to sit still"
    },
    {
        "id": 6,
        "text": "Trở nên dễ khó chịu hoặc cáu kỉnh",
        "en": "Becoming easily annoyed or irritable"
    },
    {
        "id": 7,
        "text": "Cảm thấy sợ hãi như thể điều gì đó khủng khiếp sắp xảy ra",
        "en": "Feeling afraid as if something awful might happen"
    }
]

GAD7_ANSWER_OPTIONS_VI = [
    {"value": 0, "text": "Không có gì", "en": "Not at all"},
    {"value": 1, "text": "Vài ngày", "en": "Several days"},
    {"value": 2, "text": "Hơn nửa số ngày", "en": "More than half the days"},
    {"value": 3, "text": "Gần như mỗi ngày", "en": "Nearly every day"}
]

GAD7_FUNCTIONAL_QUESTION_VI = """
Nếu bạn đã kiểm tra bất kỳ vấn đề nào, những vấn đề này đã khiến bạn 
khó khăn như thế nào để thực hiện công việc của mình, giải quyết mọi 
việc ở nhà, hay hòa đồng với những người khác?
"""

GAD7_FUNCTIONAL_OPTIONS_VI = [
    {"value": 0, "text": "Không khó chút nào", "en": "Not difficult at all"},
    {"value": 1, "text": "Hơi khó", "en": "Somewhat difficult"},
    {"value": 2, "text": "Rất khó", "en": "Very difficult"},
    {"value": 3, "text": "Cực kỳ khó khăn", "en": "Extremely difficult"}
]

# ============================================
# GAD-7 Scoring and Interpretation
# ============================================

GAD7_SEVERITY_LEVELS = {
    "minimal": {
        "range": (0, 4),
        "name_vi": "Lo âu tối thiểu",
        "name_en": "Minimal anxiety",
        "description_vi": "Điểm số của bạn cho thấy mức độ lo âu tối thiểu. Việc điều trị lo âu có thể không cần thiết về mặt lâm sàng.",
        "recommendation_vi": "Duy trì lối sống lành mạnh, tập thể dục thường xuyên và kỹ thuật giảm căng thẳng.",
        "color": "green",
        "clinical_note": "Treatment for anxiety may not be clinically indicated."
    },
    "mild": {
        "range": (5, 9),
        "name_vi": "Lo âu nhẹ",
        "name_en": "Mild anxiety",
        "description_vi": "Điểm số của bạn cho thấy mức độ lo âu nhẹ. Bạn có thể gặp một số triệu chứng lo âu nhưng chúng có thể được quản lý.",
        "recommendation_vi": "Cân nhắc các kỹ thuật tự chăm sóc như thiền định, tập thể dục và quản lý căng thẳng. Tham khảo ý kiến chuyên gia nếu triệu chứng tiếp tục.",
        "color": "yellow",
        "clinical_note": "Therapist uses clinical judgement about treatment needs based upon knowledge of the client, duration and severity of symptoms."
    },
    "moderate": {
        "range": (10, 14),
        "name_vi": "Lo âu trung bình",
        "name_en": "Moderate anxiety",
        "description_vi": "Điểm số của bạn cho thấy mức độ lo âu trung bình. Các triệu chứng này có thể ảnh hưởng đến cuộc sống hàng ngày của bạn.",
        "recommendation_vi": "Nên tham khảo ý kiến chuyên gia tâm lý hoặc tư vấn viên. Liệu pháp tâm lý có thể giúp bạn quản lý các triệu chứng hiệu quả.",
        "color": "orange",
        "clinical_note": "Treatment goals and interventions target the specific symptoms indicated by client's answers."
    },
    "severe": {
        "range": (15, 21),
        "name_vi": "Lo âu nặng",
        "name_en": "Moderate to severe anxiety",
        "description_vi": "Điểm số của bạn cho thấy mức độ lo âu từ trung bình đến nặng. Các triệu chứng này có thể ảnh hưởng đáng kể đến cuộc sống của bạn.",
        "recommendation_vi": "Nên gặp chuyên gia sức khỏe tâm thần ngay. Điều trị có thể bao gồm liệu pháp tâm lý, thuốc, hoặc cả hai.",
        "color": "red",
        "clinical_note": "Treatment goals and interventions target the specific symptoms indicated by client's answers. This score often warrants treatment using medication, therapy, or both."
    }
}

def get_severity_level(score: int) -> dict:
    """
    Get severity level based on GAD-7 score
    
    Args:
        score: Total GAD-7 score (0-21)
        
    Returns:
        dict: Severity level information
    """
    if 0 <= score <= 4:
        return GAD7_SEVERITY_LEVELS["minimal"]
    elif 5 <= score <= 9:
        return GAD7_SEVERITY_LEVELS["mild"]
    elif 10 <= score <= 14:
        return GAD7_SEVERITY_LEVELS["moderate"]
    elif 15 <= score <= 21:
        return GAD7_SEVERITY_LEVELS["severe"]
    else:
        raise ValueError(f"Invalid GAD-7 score: {score}. Must be between 0 and 21.")

# ============================================
# Counselor Specializations
# ============================================

COUNSELOR_SPECIALIZATIONS = [
    "Tâm lý học lâm sàng",
    "Tâm lý học tư vấn",
    "Tâm lý học trẻ em và thanh thiếu niên",
    "Tâm lý học giáo dục",
    "Tâm lý học sức khỏe",
    "Liệu pháp nhận thức hành vi (CBT)",
    "Liệu pháp tâm lý động lực",
    "Liệu pháp gia đình và hôn nhân",
    "Rối loạn lo âu và căng thẳng",
    "Trầm cảm và rối loạn tâm trạng",
    "Tư vấn nghề nghiệp",
    "Tư vấn học đường"
]

# ============================================
# Parent-Child Relationships
# ============================================

PARENT_RELATIONSHIPS = [
    "Cha",
    "Mẹ",
    "Cha dượng",
    "Mẹ kế",
    "Ông",
    "Bà",
    "Người giám hộ hợp pháp"
]

# ============================================
# Universities in Vietnam (Common ones)
# ============================================

VIETNAM_UNIVERSITIES = [
    "Đại học Quốc gia Hà Nội",
    "Đại học Quốc gia TP.HCM",
    "Đại học Bách khoa Hà Nội",
    "Đại học Công nghệ",
    "Đại học Khoa học Tự nhiên",
    "Đại học Khoa học Xã hội và Nhân văn",
    "Đại học Kinh tế Quốc dân",
    "Đại học Ngoại thương",
    "Đại học Y Hà Nội",
    "Đại học Sư phạm Hà Nội",
    "Đại học FPT",
    "Đại học RMIT Việt Nam",
    "Đại học Tôn Đức Thắng",
    "Đại học Khác"
]

# ============================================
# Common Majors
# ============================================

COMMON_MAJORS = [
    "Công nghệ thông tin",
    "Khoa học máy tính",
    "Kỹ thuật phần mềm",
    "An toàn thông tin",
    "Trí tuệ nhân tạo",
    "Kinh tế",
    "Quản trị kinh doanh",
    "Kế toán",
    "Tài chính - Ngân hàng",
    "Marketing",
    "Y khoa",
    "Dược học",
    "Điều dưỡng",
    "Luật",
    "Ngoại ngữ",
    "Báo chí",
    "Thiết kế đồ họa",
    "Kiến trúc",
    "Cơ khí",
    "Điện - Điện tử",
    "Xây dựng",
    "Khác"
]
