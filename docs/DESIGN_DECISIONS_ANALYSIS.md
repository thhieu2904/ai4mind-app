# Phân tích Quyết định Thiết kế - AI4Mind

## 🎨 Vấn đề 1: Card Design Philosophy

### Câu hỏi của bạn:

> "Giao diện card của từng trang sẽ khác nhau 1 chút (có trang sẽ có thêm 1 hàng với các nút điều khiển) thì hướng triển khai có đúng chuẩn chưa?"

### ✅ Phân tích Trade-offs

#### Option A: **Full Standardization** (100% đồng bộ)

```
✅ Pros:
- User nhận ra patterns nhanh
- Development đơn giản (1 component)
- Consistency cao

❌ Cons:
- Mất flexibility
- Mỗi trang có actions khác nhau → phải force vào structure chung
- Harder to customize per-page needs
```

#### Option B: **Flexible Components** (Base + Custom)

```
✅ Pros:
- Mỗi trang có freedom để thêm features
- Easy to evolve
- Phù hợp với mental health messaging (custom per context)

❌ Cons:
- Risk of inconsistency
- Harder to maintain if không có design system
```

### 🎯 **RECOMMENDATION: Hybrid Approach**

Áp dụng **"Consistent Core + Flexible Slots"** pattern:

```tsx
// Base InfoCard với slots cho customization
interface InfoCardProps {
  // CONSISTENT: Core visual style
  variant?: "primary" | "secondary" | "success" | "warning";
  gradient?: boolean;

  // CONSISTENT: Base layout structure
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;

  // FLEXIBLE: Slots cho custom content
  children: React.ReactNode;

  // FLEXIBLE: Actions per page
  actions?: React.ReactNode; // <-- KEY: Slot cho buttons/controls

  // FLEXIBLE: Header decoration
  headerExtra?: React.ReactNode; // Badge, status, etc.

  // CONSISTENT: Behavior
  clickable?: boolean;
  onClick?: () => void;
}

// Usage trong từng trang
<InfoCard
  variant="primary"
  gradient
  title="Thống kê sức khỏe"
  actions={
    // ✅ Mỗi trang custom actions riêng
    <>
      <Button onClick={handleExport}>Xuất báo cáo</Button>
      <Button onClick={handleRefresh}>Làm mới</Button>
    </>
  }
>
  {/* Custom content */}
</InfoCard>;
```

### 📊 Phân tích cho Mental Health App

**Điểm quan trọng**: App cho người có vấn đề cảm xúc cần:

1. **Predictable Layout** (Đồng bộ core)

   - ✅ Card style, spacing, colors → CONSISTENT
   - ✅ Reduce cognitive load
   - ✅ Build trust through familiarity

2. **Contextual Messaging** (Linh hoạt nội dung)

   - ✅ Mỗi trang có message phù hợp
   - ✅ Dashboard: Encouraging + Progress
   - ✅ Assessment: Supportive + Actionable
   - ✅ Profile: Empowering + Personal

3. **Page-specific Actions** (Linh hoạt controls)
   - ✅ Dashboard: Quick actions (Trắc nghiệm mới, Chat AI)
   - ✅ Statistics: Export, Date range
   - ✅ Profile: Edit, Settings

### 🛠️ Implementation Strategy

#### Step 1: Tạo Base InfoCard với Slots

```tsx
// frontend/src/components/common/InfoCard/InfoCard.tsx
export const InfoCard: React.FC<InfoCardProps> = ({
  variant = "plain",
  gradient = false,
  title,
  subtitle,
  icon,
  headerExtra,
  children,
  actions,
  clickable = false,
  onClick,
}) => {
  return (
    <div
      className={`info-card info-card--${variant} ${
        gradient ? "gradient" : ""
      }`}
      onClick={clickable ? onClick : undefined}
    >
      {/* CONSISTENT: Header structure */}
      <div className="info-card__header">
        {icon && <div className="info-card__icon">{icon}</div>}
        <div className="info-card__header-content">
          {title && <h3 className="info-card__title">{title}</h3>}
          {subtitle && <p className="info-card__subtitle">{subtitle}</p>}
        </div>
        {/* FLEXIBLE: Extra header content */}
        {headerExtra && (
          <div className="info-card__header-extra">{headerExtra}</div>
        )}
      </div>

      {/* FLEXIBLE: Main content */}
      <div className="info-card__body">{children}</div>

      {/* FLEXIBLE: Actions slot */}
      {actions && <div className="info-card__actions">{actions}</div>}
    </div>
  );
};
```

#### Step 2: Specialized Cards cho từng context

```tsx
// frontend/src/components/dashboard/WelcomeCard.tsx
export const WelcomeCard: React.FC<{ stats: DashboardStats }> = ({ stats }) => {
  return (
    <InfoCard variant="primary" gradient icon={<WavingHandIcon />}>
      <h1 className="welcome-title">
        Xin chào
        <br />
        {stats.user_name}!
      </h1>

      {/* ✅ CUSTOM: Contextual messaging cho mental health */}
      <div className="health-info">
        <p className="info-item encouraging">
          🌟 Bạn đã chăm sóc sức khỏe tinh thần được{" "}
          <strong>{stats.days_since_registration}</strong> ngày.
        </p>

        <p className={`info-item emotion-${stats.latest_emotion_class}`}>
          {getEmotionEmoji(stats.latest_severity)}
          Cảm xúc gần nhất: <strong>{stats.latest_emotion_text}</strong>
        </p>

        {/* ✅ Conditional encouraging message */}
        {stats.latest_severity === "minimal" && (
          <p className="info-item positive">
            💪 Bạn đang làm rất tốt! Hãy tiếp tục duy trì.
          </p>
        )}

        {stats.latest_severity === "severe" && (
          <p className="info-item supportive">
            🤗 Đừng lo lắng, chúng mình luôn ở đây hỗ trợ bạn.
          </p>
        )}
      </div>
    </InfoCard>
  );
};
```

```tsx
// frontend/src/components/statistics/StatsCard.tsx
export const StatsCard: React.FC<{ stats: AssessmentStats }> = ({ stats }) => {
  return (
    <InfoCard
      variant="secondary"
      title="Thống kê đánh giá"
      headerExtra={<Badge color="info">{stats.total_assessments} lần</Badge>}
      actions={
        // ✅ CUSTOM: Page-specific actions
        <Box sx={{ display: "flex", gap: 1 }}>
          <Button startIcon={<DownloadIcon />} onClick={handleExport}>
            Xuất báo cáo
          </Button>
          <Button startIcon={<RefreshIcon />} onClick={handleRefresh}>
            Làm mới
          </Button>
        </Box>
      }
    >
      {/* Custom stats content */}
      <Grid container spacing={2}>
        {/* ... */}
      </Grid>
    </InfoCard>
  );
};
```

### 📋 Design System Rules

**CONSISTENT** (Bắt buộc giữ nguyên):

- ✅ Card border-radius: `16px`
- ✅ Card shadow: `0 4px 12px rgba(0, 0, 0, 0.1)`
- ✅ Padding: `24px`
- ✅ Color palette (primary, secondary, success, warning)
- ✅ Typography scale
- ✅ Spacing system (8px grid)

**FLEXIBLE** (Tùy chỉnh theo context):

- ✅ Content structure (messages, stats, charts)
- ✅ Action buttons (số lượng, type, handlers)
- ✅ Header extras (badges, status, timestamps)
- ✅ Conditional elements (dựa vào severity, progress, etc.)

### 🎨 CSS Architecture

```css
/* InfoCard.css - CONSISTENT core styles */
.info-card {
  /* Base structure - NEVER change */
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 24px;
  background: white;
  transition: all 0.3s ease;
}

/* Variants - CONSISTENT but customizable */
.info-card--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.info-card--secondary {
  border: 1px solid #e0e0e0;
}

/* Layout slots - FLEXIBLE */
.info-card__header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.info-card__actions {
  /* Flexible slot - pages can style differently */
  margin-top: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
```

### ✅ Kết luận Vấn đề 1

**Approach đề xuất**: ✅ **ĐÚNG CHUẨN**

- ✅ Đồng bộ core visual (layout, colors, spacing)
- ✅ Linh hoạt content (messages phù hợp context)
- ✅ Linh hoạt actions (buttons/controls per page)
- ✅ Phù hợp mental health app (predictable + personalized)

**Lợi ích**:

- Users có familiarity → reduce anxiety
- Developers có flexibility → easy maintenance
- Best of both worlds!

---

## 📝 Vấn đề 2: Config-Driven Rating Form

### Câu hỏi của bạn:

> "Nếu phải xử lý trong code thì rất rắc rối, liệu mình có thể nhập danh sách qua 1 file nào đó trong frontend để tiện chỉnh sửa không?"

### ✅ Phân tích

**Vấn đề với Hardcode**:

```tsx
// ❌ BAD: Hardcoded questions
<RadioGroup>
  <FormControlLabel value="new" label="Mới dùng thử lần này" />
  <FormControlLabel value="few_days" label="Vài ngày" />
  <FormControlLabel value="week" label="Hơn 1 tuần" />
  <FormControlLabel value="month" label="Hơn 1 tháng" />
</RadioGroup>
```

**Khi cần sửa**:

- Thêm/xóa option → Edit component code
- Thay đổi wording → Edit component code
- Thêm conditional logic → Edit component code
- Risk breaking UI khi sửa

### 🎯 Solution: JSON Config Schema

#### Schema Design

Dựa trên `test_form.md`, cần support:

1. **Multiple sections** (Phần 1, 2, 3, 4)
2. **Question types**:
   - Radio (single choice)
   - Checkbox (multiple choice)
   - Scale (1-5, 1-10)
   - Text (short/long)
   - Table (matrix questions)
3. **Conditional logic** (skip/show based on answers)
4. **Validation rules**

#### JSON Schema Structure

```typescript
// frontend/src/config/ratingFormSchema.ts

export interface FormOption {
  value: string;
  label: string;
  helpText?: string; // Optional explanation
}

export interface FormQuestion {
  id: string;
  type: "radio" | "checkbox" | "scale" | "text" | "textarea" | "table";
  label: string;
  description?: string;
  required?: boolean;

  // For radio/checkbox
  options?: FormOption[];

  // For scale
  scaleMin?: number;
  scaleMax?: number;
  scaleLabels?: { [key: number]: string }; // { 1: "Rất không hài lòng", 5: "Rất hài lòng" }

  // For table
  tableRows?: string[]; // Row labels
  tableColumns?: FormOption[]; // Column options

  // Conditional logic
  showIf?: {
    questionId: string;
    operator: "equals" | "includes" | "greaterThan";
    value: string | number;
  };

  // Validation
  validation?: {
    minLength?: number;
    maxLength?: number;
    pattern?: string;
    message?: string;
  };
}

export interface FormSection {
  id: string;
  title: string;
  description?: string;
  questions: FormQuestion[];
}

export interface RatingFormConfig {
  title: string;
  description: string;
  sections: FormSection[];
}
```

#### JSON Config File

```json
// frontend/src/config/ratingForm.json
{
  "title": "Khảo sát Trải nghiệm Ứng dụng Hỗ trợ Sức khỏe Tinh thần AI4Mind",
  "description": "Cảm ơn bạn đã dành thời gian trải nghiệm AI4Mind! Những đóng góp của bạn sẽ giúp chúng tôi cải thiện và phát triển ứng dụng tốt hơn.",
  "sections": [
    {
      "id": "general_info",
      "title": "Phần 1: Thông tin chung",
      "description": "Phần này giúp chúng tôi hiểu rõ hơn về người dùng. Mọi thông tin đều được bảo mật.",
      "questions": [
        {
          "id": "discovery_channel",
          "type": "radio",
          "label": "Bạn biết đến AI4Mind qua kênh nào?",
          "required": true,
          "options": [
            { "value": "friends", "label": "Bạn bè giới thiệu" },
            {
              "value": "social_media",
              "label": "Mạng xã hội (Facebook, TikTok,...)"
            },
            { "value": "school", "label": "Trường học/Giảng viên" },
            { "value": "search", "label": "Tìm kiếm trên Google/App Store" },
            { "value": "other", "label": "Khác" }
          ]
        },
        {
          "id": "discovery_channel_other",
          "type": "text",
          "label": "Vui lòng ghi rõ:",
          "showIf": {
            "questionId": "discovery_channel",
            "operator": "equals",
            "value": "other"
          },
          "validation": {
            "minLength": 3,
            "message": "Vui lòng nhập ít nhất 3 ký tự"
          }
        },
        {
          "id": "usage_duration",
          "type": "radio",
          "label": "Bạn đã sử dụng ứng dụng trong bao lâu?",
          "required": true,
          "options": [
            { "value": "today", "label": "Mới dùng thử hôm nay" },
            { "value": "few_days", "label": "Vài ngày" },
            { "value": "week_plus", "label": "Hơn 1 tuần" },
            { "value": "month_plus", "label": "Hơn 1 tháng" }
          ]
        },
        {
          "id": "usage_frequency",
          "type": "radio",
          "label": "Tần suất sử dụng của bạn?",
          "required": true,
          "options": [
            { "value": "daily", "label": "Hàng ngày" },
            { "value": "few_times_week", "label": "Vài lần một tuần" },
            { "value": "weekly", "label": "Mỗi tuần một lần" },
            { "value": "rarely", "label": "Hiếm khi" }
          ]
        }
      ]
    },
    {
      "id": "ui_ux",
      "title": "Phần 2: Trải nghiệm và Giao diện người dùng (UI/UX)",
      "description": "Đánh giá theo thang điểm từ 1 (Rất không hài lòng) đến 5 (Rất hài lòng).",
      "questions": [
        {
          "id": "ui_table",
          "type": "table",
          "label": "Đánh giá các tiêu chí sau:",
          "required": true,
          "tableRows": [
            "Giao diện của ứng dụng có dễ nhìn và thân thiện không?",
            "Bố cục các tính năng có dễ tìm và dễ sử dụng không?",
            "Tốc độ phản hồi của ứng dụng có nhanh không?",
            "Màu sắc và hình ảnh trong ứng dụng có tạo cảm giác thoải mái không?"
          ],
          "tableColumns": [
            { "value": "1", "label": "1" },
            { "value": "2", "label": "2" },
            { "value": "3", "label": "3" },
            { "value": "4", "label": "4" },
            { "value": "5", "label": "5" }
          ]
        }
      ]
    },
    {
      "id": "features",
      "title": "Phần 3: Đánh giá các Tính năng chính",
      "questions": [
        {
          "id": "gad7_understanding",
          "type": "radio",
          "label": "Bạn có thấy bộ câu hỏi GAD-7 dễ hiểu không?",
          "required": true,
          "options": [
            { "value": "very_easy", "label": "Rất dễ hiểu" },
            { "value": "easy", "label": "Dễ hiểu" },
            { "value": "normal", "label": "Bình thường" },
            { "value": "hard", "label": "Khó hiểu" },
            { "value": "very_hard", "label": "Rất khó hiểu" }
          ]
        },
        {
          "id": "gad7_results_useful",
          "type": "scale",
          "label": "Kết quả và giải thích sau bài trắc nghiệm có hữu ích cho bạn không?",
          "description": "1 = Hoàn toàn không hữu ích, 5 = Rất hữu ích",
          "required": true,
          "scaleMin": 1,
          "scaleMax": 5,
          "scaleLabels": {
            "1": "Không hữu ích",
            "5": "Rất hữu ích"
          }
        },
        {
          "id": "ai_recommendations",
          "type": "scale",
          "label": "Các khuyến nghị mà AI đưa ra sau bài trắc nghiệm có phù hợp và thiết thực không?",
          "required": true,
          "scaleMin": 1,
          "scaleMax": 5,
          "scaleLabels": {
            "1": "Không phù hợp",
            "5": "Rất phù hợp"
          }
        },
        {
          "id": "voice_recording_help",
          "type": "radio",
          "label": "Hướng dẫn ghi âm và các câu hỏi gợi ý có giúp bạn dễ dàng chia sẻ hơn không?",
          "required": true,
          "options": [
            { "value": "very_helpful", "label": "Rất hữu ích" },
            { "value": "helpful", "label": "Hữu ích" },
            { "value": "neutral", "label": "Không ảnh hưởng nhiều" },
            { "value": "not_helpful", "label": "Không hữu ích" }
          ]
        },
        {
          "id": "voice_trust",
          "type": "scale",
          "label": "Bạn có tin tưởng vào kết quả phân tích cảm xúc qua giọng nói không?",
          "required": true,
          "scaleMin": 1,
          "scaleMax": 5,
          "scaleLabels": {
            "1": "Không tin tưởng",
            "5": "Rất tin tưởng"
          }
        },
        {
          "id": "privacy_concern",
          "type": "radio",
          "label": "Bạn có lo ngại về quyền riêng tư khi sử dụng tính năng này không?",
          "required": true,
          "options": [
            { "value": "very_concerned", "label": "Có, tôi rất lo ngại" },
            { "value": "slightly_concerned", "label": "Có một chút lo ngại" },
            {
              "value": "not_concerned",
              "label": "Không, tôi tin tưởng ứng dụng"
            }
          ]
        },
        {
          "id": "charts_clear",
          "type": "radio",
          "label": "Các biểu đồ (Xu hướng điểm, Phân bố mức độ) có trực quan và dễ hiểu không?",
          "required": true,
          "options": [
            { "value": "very_clear", "label": "Có, rất trực quan" },
            { "value": "clear", "label": "Tương đối dễ hiểu" },
            {
              "value": "needs_improvement",
              "label": "Hơi khó hiểu, cần cải thiện"
            }
          ]
        },
        {
          "id": "stats_useful",
          "type": "scale",
          "label": "Thông tin về 'Điểm trung bình', 'Điểm gần nhất' và 'Xu hướng' có hữu ích cho việc theo dõi sức khỏe tinh thần của bạn không?",
          "required": true,
          "scaleMin": 1,
          "scaleMax": 5
        },
        {
          "id": "features_used",
          "type": "checkbox",
          "label": "Bạn đã thử tính năng nào trong mục 'Tìm kiếm hỗ trợ'? (chọn nhiều)",
          "required": false,
          "options": [
            { "value": "ai_chat", "label": "Trò chuyện với AI" },
            { "value": "find_expert", "label": "Tìm kiếm chuyên gia tâm lý" },
            { "value": "find_center", "label": "Tìm trung tâm y tế gần nhất" },
            { "value": "none", "label": "Tôi chưa thử tính năng nào" }
          ]
        },
        {
          "id": "ai_chat_rating",
          "type": "scale",
          "label": "Đánh giá mức độ hữu ích của tính năng 'Trò chuyện với AI':",
          "required": false,
          "scaleMin": 1,
          "scaleMax": 5,
          "showIf": {
            "questionId": "features_used",
            "operator": "includes",
            "value": "ai_chat"
          }
        },
        {
          "id": "map_rating",
          "type": "scale",
          "label": "Bản đồ các trung tâm y tế có dễ sử dụng và thông tin có chính xác không?",
          "required": false,
          "scaleMin": 1,
          "scaleMax": 5,
          "showIf": {
            "questionId": "features_used",
            "operator": "includes",
            "value": "find_center"
          }
        }
      ]
    },
    {
      "id": "feedback",
      "title": "Phần 4: Đóng góp & Ý kiến khác",
      "questions": [
        {
          "id": "favorite_feature",
          "type": "textarea",
          "label": "Tính năng nào bạn thích nhất ở AI4Mind và tại sao?",
          "required": false,
          "validation": {
            "maxLength": 500
          }
        },
        {
          "id": "improvement_needed",
          "type": "textarea",
          "label": "Theo bạn, AI4Mind cần cải thiện điều gì nhất?",
          "required": false,
          "validation": {
            "maxLength": 500
          }
        },
        {
          "id": "feature_suggestions",
          "type": "textarea",
          "label": "Bạn có muốn đề xuất thêm tính năng nào mới cho ứng dụng không?",
          "required": false,
          "validation": {
            "maxLength": 500
          }
        },
        {
          "id": "recommend_score",
          "type": "scale",
          "label": "Bạn có sẵn sàng giới thiệu AI4Mind cho bạn bè hoặc người thân không?",
          "description": "1 = Chắc chắn không, 10 = Chắc chắn có",
          "required": true,
          "scaleMin": 1,
          "scaleMax": 10
        }
      ]
    }
  ]
}
```

#### Dynamic Form Component

```tsx
// frontend/src/components/rating/DynamicRatingForm.tsx
import React, { useState, useEffect } from "react";
import {
  Stepper,
  Step,
  StepLabel,
  Button,
  Box,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  TextField,
  Rating as MuiRating,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  FormControl,
  FormLabel,
  FormHelperText,
} from "@mui/material";

import ratingFormConfig from "../../config/ratingForm.json";
import type {
  RatingFormConfig,
  FormSection,
  FormQuestion,
} from "../../config/ratingFormSchema";

export const DynamicRatingForm: React.FC = () => {
  const config: RatingFormConfig = ratingFormConfig;
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Check if question should be shown based on conditional logic
  const shouldShowQuestion = (question: FormQuestion): boolean => {
    if (!question.showIf) return true;

    const { questionId, operator, value } = question.showIf;
    const answer = formData[questionId];

    switch (operator) {
      case "equals":
        return answer === value;
      case "includes":
        return Array.isArray(answer) && answer.includes(value);
      case "greaterThan":
        return typeof answer === "number" && answer > value;
      default:
        return true;
    }
  };

  // Validate current section
  const validateSection = (section: FormSection): boolean => {
    const newErrors: Record<string, string> = {};

    section.questions.forEach((question) => {
      if (!shouldShowQuestion(question)) return;

      if (question.required && !formData[question.id]) {
        newErrors[question.id] = "Vui lòng trả lời câu hỏi này";
      }

      if (question.validation && formData[question.id]) {
        const value = formData[question.id];
        const { minLength, maxLength, pattern, message } = question.validation;

        if (minLength && value.length < minLength) {
          newErrors[question.id] = message || `Tối thiểu ${minLength} ký tự`;
        }

        if (maxLength && value.length > maxLength) {
          newErrors[question.id] = message || `Tối đa ${maxLength} ký tự`;
        }

        if (pattern && !new RegExp(pattern).test(value)) {
          newErrors[question.id] = message || "Định dạng không hợp lệ";
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Render question based on type
  const renderQuestion = (question: FormQuestion) => {
    if (!shouldShowQuestion(question)) return null;

    const value = formData[question.id];
    const error = errors[question.id];

    switch (question.type) {
      case "radio":
        return (
          <FormControl error={!!error} fullWidth sx={{ mb: 3 }}>
            <FormLabel>{question.label}</FormLabel>
            {question.description && (
              <FormHelperText>{question.description}</FormHelperText>
            )}
            <RadioGroup
              value={value || ""}
              onChange={(e) =>
                setFormData({ ...formData, [question.id]: e.target.value })
              }
            >
              {question.options?.map((option) => (
                <FormControlLabel
                  key={option.value}
                  value={option.value}
                  control={<Radio />}
                  label={option.label}
                />
              ))}
            </RadioGroup>
            {error && <FormHelperText error>{error}</FormHelperText>}
          </FormControl>
        );

      case "checkbox":
        return (
          <FormControl error={!!error} fullWidth sx={{ mb: 3 }}>
            <FormLabel>{question.label}</FormLabel>
            {question.options?.map((option) => (
              <FormControlLabel
                key={option.value}
                control={
                  <Checkbox
                    checked={value?.includes(option.value) || false}
                    onChange={(e) => {
                      const currentValues = value || [];
                      const newValues = e.target.checked
                        ? [...currentValues, option.value]
                        : currentValues.filter(
                            (v: string) => v !== option.value
                          );
                      setFormData({ ...formData, [question.id]: newValues });
                    }}
                  />
                }
                label={option.label}
              />
            ))}
            {error && <FormHelperText error>{error}</FormHelperText>}
          </FormControl>
        );

      case "scale":
        return (
          <FormControl error={!!error} fullWidth sx={{ mb: 3 }}>
            <FormLabel>{question.label}</FormLabel>
            {question.description && (
              <FormHelperText>{question.description}</FormHelperText>
            )}
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 1 }}>
              <MuiRating
                value={value || 0}
                max={question.scaleMax}
                onChange={(_, newValue) =>
                  setFormData({ ...formData, [question.id]: newValue })
                }
                size="large"
              />
              <span>
                ({value || 0}/{question.scaleMax})
              </span>
            </Box>
            {question.scaleLabels && (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  mt: 1,
                  fontSize: "0.875rem",
                }}
              >
                <span>{question.scaleLabels[question.scaleMin!]}</span>
                <span>{question.scaleLabels[question.scaleMax!]}</span>
              </Box>
            )}
            {error && <FormHelperText error>{error}</FormHelperText>}
          </FormControl>
        );

      case "text":
        return (
          <FormControl error={!!error} fullWidth sx={{ mb: 3 }}>
            <TextField
              label={question.label}
              value={value || ""}
              onChange={(e) =>
                setFormData({ ...formData, [question.id]: e.target.value })
              }
              error={!!error}
              helperText={error || question.description}
            />
          </FormControl>
        );

      case "textarea":
        return (
          <FormControl error={!!error} fullWidth sx={{ mb: 3 }}>
            <TextField
              label={question.label}
              value={value || ""}
              onChange={(e) =>
                setFormData({ ...formData, [question.id]: e.target.value })
              }
              multiline
              rows={4}
              error={!!error}
              helperText={error || question.description}
            />
          </FormControl>
        );

      case "table":
        return (
          <FormControl error={!!error} fullWidth sx={{ mb: 3 }}>
            <FormLabel>{question.label}</FormLabel>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell></TableCell>
                  {question.tableColumns?.map((col) => (
                    <TableCell key={col.value} align="center">
                      {col.label}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {question.tableRows?.map((row, rowIndex) => (
                  <TableRow key={rowIndex}>
                    <TableCell>{row}</TableCell>
                    {question.tableColumns?.map((col) => (
                      <TableCell key={col.value} align="center">
                        <Radio
                          checked={
                            formData[`${question.id}_${rowIndex}`] === col.value
                          }
                          onChange={() =>
                            setFormData({
                              ...formData,
                              [`${question.id}_${rowIndex}`]: col.value,
                            })
                          }
                        />
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {error && <FormHelperText error>{error}</FormHelperText>}
          </FormControl>
        );

      default:
        return null;
    }
  };

  // Navigate between sections
  const handleNext = () => {
    const currentSection = config.sections[activeStep];
    if (validateSection(currentSection)) {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    // Submit to backend
    console.log("Form data:", formData);
  };

  const currentSection = config.sections[activeStep];

  return (
    <Box>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {config.sections.map((section) => (
          <Step key={section.id}>
            <StepLabel>{section.title}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Box>
        <h2>{currentSection.title}</h2>
        {currentSection.description && (
          <p style={{ color: "text.secondary" }}>
            {currentSection.description}
          </p>
        )}

        {currentSection.questions.map((question) => (
          <Box key={question.id}>{renderQuestion(question)}</Box>
        ))}
      </Box>

      <Box sx={{ display: "flex", justifyContent: "space-between", mt: 4 }}>
        <Button disabled={activeStep === 0} onClick={handleBack}>
          Quay lại
        </Button>

        {activeStep === config.sections.length - 1 ? (
          <Button variant="contained" onClick={handleSubmit}>
            Gửi đánh giá
          </Button>
        ) : (
          <Button variant="contained" onClick={handleNext}>
            Tiếp theo
          </Button>
        )}
      </Box>
    </Box>
  );
};
```

### ✅ Lợi ích Config-Driven Approach

**Pros**:

- ✅ Easy to edit (JSON file, không cần code)
- ✅ Non-developers có thể update questions
- ✅ Version control dễ (track changes in JSON)
- ✅ Reusable (dùng lại logic, chỉ đổi config)
- ✅ A/B testing (swap configs)

**Cons**:

- ⚠️ Initial setup phức tạp hơn
- ⚠️ Cần good schema design
- ⚠️ Complex conditional logic harder to express

### 📋 Kết luận Vấn đề 2

**✅ ĐÚNG HƯỚNG**: Config-driven form là best practice

**Next steps**:

1. Tạo `ratingFormSchema.ts` (TypeScript types)
2. Tạo `ratingForm.json` (dựa trên test_form.md)
3. Implement `DynamicRatingForm` component
4. Test với real data

---

## 🏠 Vấn đề 3: Simplified Dashboard Endpoint

### Yêu cầu của bạn:

1. ✅ Lấy tên người dùng
2. ✅ Lấy cảm xúc **gần nhất** (không phải trung bình)
3. ✅ Lấy số ngày từ ngày tạo tài khoản

### ✅ Phân tích

**So với previous approach**:

- ❌ Old: Calculate dominant emotion 30 days → Complex query
- ✅ New: Get latest assessment only → Simple & fast!

**Database có sẵn**:

- ✅ `User.created_at` → Calculate days
- ✅ `User.full_name` → Display name
- ✅ `Assessment.severity_level` (latest) → Emotion
- ✅ `Assessment.created_at` (latest) → Emotion date

### 🎯 Implementation

#### Backend Schema

```python
# ai-service/app/schemas/dashboard.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DashboardWelcomeData(BaseModel):
    """Simplified dashboard welcome card data"""
    user_name: str
    days_since_registration: int

    # Latest emotion
    latest_emotion_severity: Optional[str] = None  # "minimal" | "mild" | "moderate" | "severe"
    latest_emotion_text: Optional[str] = None  # "Tích cực" | "Bình thường" | "Lo âu" | "Căng thẳng"
    latest_emotion_date: Optional[datetime] = None

    # Quick stats
    total_assessments: int = 0
    has_recent_assessment: bool = False  # Within 7 days

    class Config:
        from_attributes = True
```

#### Backend Endpoint

```python
# ai-service/app/api/v1/endpoints/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import Any

from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import User
from app.models.student import Student
from app.models.assessment import Assessment
from app.schemas.dashboard import DashboardWelcomeData

router = APIRouter()

@router.get("/welcome", response_model=DashboardWelcomeData)
async def get_dashboard_welcome_data(
    current_user: User = Depends(require_roles(["STUDENT"])),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get simplified dashboard welcome card data
    - User name
    - Days since registration
    - Latest emotion (not average)
    """

    # Get student profile
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    # 1. Calculate days since registration
    days_since_registration = 0
    if current_user.created_at:
        delta = datetime.utcnow() - current_user.created_at.replace(tzinfo=None)
        days_since_registration = delta.days

    # 2. Get latest assessment (most recent)
    latest_assessment = db.query(Assessment).filter(
        Assessment.student_id == student.id
    ).order_by(desc(Assessment.created_at)).first()

    # 3. Map severity to Vietnamese emotion text
    emotion_map = {
        "minimal": "Tích cực",
        "mild": "Bình thường",
        "moderate": "Lo âu",
        "severe": "Căng thẳng"
    }

    latest_emotion_severity = None
    latest_emotion_text = None
    latest_emotion_date = None
    has_recent_assessment = False

    if latest_assessment:
        latest_emotion_severity = latest_assessment.severity_level
        latest_emotion_text = emotion_map.get(latest_assessment.severity_level, "Chưa xác định")
        latest_emotion_date = latest_assessment.created_at

        # Check if assessment is within 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        has_recent_assessment = latest_assessment.created_at.replace(tzinfo=None) >= seven_days_ago

    # 4. Count total assessments
    total_assessments = db.query(Assessment).filter(
        Assessment.student_id == student.id
    ).count()

    return DashboardWelcomeData(
        user_name=current_user.full_name,
        days_since_registration=days_since_registration,
        latest_emotion_severity=latest_emotion_severity,
        latest_emotion_text=latest_emotion_text,
        latest_emotion_date=latest_emotion_date,
        total_assessments=total_assessments,
        has_recent_assessment=has_recent_assessment,
    )
```

#### Register Router

```python
# ai-service/app/api/v1/api.py
from app.api.v1.endpoints import (
    auth,
    students,
    assessments,
    voice,
    conversations,
    export,
    dashboard,  # <-- NEW
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"]
)
```

#### Frontend Service

```typescript
// frontend/src/services/dashboardService.ts
import api from "./api";

export interface DashboardWelcomeData {
  user_name: string;
  days_since_registration: number;
  latest_emotion_severity: string | null;
  latest_emotion_text: string | null;
  latest_emotion_date: string | null;
  total_assessments: number;
  has_recent_assessment: boolean;
}

export const DashboardService = {
  async getWelcomeData(): Promise<DashboardWelcomeData> {
    const response = await api.get("/dashboard/welcome");
    return response.data;
  },
};
```

#### Frontend Component

```tsx
// frontend/src/pages/DashboardPage/DashboardPage.tsx
import React, { useEffect, useState } from "react";
import {
  DashboardService,
  DashboardWelcomeData,
} from "../../services/dashboardService";
import { useAuth } from "../../contexts/AuthContext";

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [welcomeData, setWelcomeData] = useState<DashboardWelcomeData | null>(
    null
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWelcomeData();
  }, []);

  const fetchWelcomeData = async () => {
    try {
      const data = await DashboardService.getWelcomeData();
      setWelcomeData(data);
    } catch (error) {
      console.error("Failed to fetch welcome data:", error);
    } finally {
      setLoading(false);
    }
  };

  // Helper: Get emoji based on severity
  const getEmotionEmoji = (severity: string | null) => {
    const emojiMap: Record<string, string> = {
      minimal: "😊",
      mild: "🙂",
      moderate: "😟",
      severe: "😔",
    };
    return emojiMap[severity || ""] || "💭";
  };

  // Helper: Get CSS class for emotion
  const getEmotionClass = (severity: string | null) => {
    const classMap: Record<string, string> = {
      minimal: "emotion-positive",
      mild: "emotion-neutral",
      moderate: "emotion-anxious",
      severe: "emotion-severe",
    };
    return classMap[severity || ""] || "emotion-unknown";
  };

  // Helper: Format date difference
  const formatEmotionDate = (date: string | null) => {
    if (!date) return "";

    const assessmentDate = new Date(date);
    const now = new Date();
    const diffDays = Math.floor(
      (now.getTime() - assessmentDate.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffDays === 0) return "hôm nay";
    if (diffDays === 1) return "hôm qua";
    if (diffDays <= 7) return `${diffDays} ngày trước`;
    return assessmentDate.toLocaleDateString("vi-VN");
  };

  if (loading) return <LoadingSpinner />;

  return (
    <MainLayout>
      <div className="dashboard-container">
        {/* ✅ Welcome Card with REAL DATA */}
        <div className="welcome-card">
          <h1 className="welcome-title">
            Xin chào
            <br />
            {welcomeData?.user_name || user?.full_name}!
          </h1>

          <div className="health-info">
            <p className="info-item encouraging">
              🌟 Bạn đã chăm sóc sức khỏe tinh thần cùng{" "}
              <strong>AI4Mind</strong> được{" "}
              <strong>{welcomeData?.days_since_registration || 0}</strong> ngày.
            </p>

            {welcomeData?.latest_emotion_text ? (
              <p
                className={`info-item ${getEmotionClass(
                  welcomeData.latest_emotion_severity
                )}`}
              >
                {getEmotionEmoji(welcomeData.latest_emotion_severity)} Cảm xúc
                gần nhất ({formatEmotionDate(welcomeData.latest_emotion_date)}):{" "}
                <strong>{welcomeData.latest_emotion_text}</strong>
              </p>
            ) : (
              <p className="info-item neutral">
                💭 Chưa có đánh giá nào. Hãy thử làm bài trắc nghiệm GAD-7!
              </p>
            )}

            {/* ✅ Contextual encouragement based on emotion */}
            {welcomeData?.latest_emotion_severity === "minimal" && (
              <p className="info-item positive-message">
                💪 Bạn đang làm rất tốt! Hãy tiếp tục duy trì.
              </p>
            )}

            {welcomeData?.latest_emotion_severity === "severe" && (
              <p className="info-item supportive-message">
                🤗 Đừng lo lắng, chúng mình luôn ở đây hỗ trợ bạn.{" "}
                <a href="/support">Tìm kiếm hỗ trợ</a>
              </p>
            )}

            {/* ✅ Encourage if no recent assessment */}
            {!welcomeData?.has_recent_assessment &&
              welcomeData?.total_assessments > 0 && (
                <p className="info-item reminder-message">
                  📅 Bạn chưa làm đánh giá trong tuần này. Hãy cập nhật tình
                  trạng của bạn!
                </p>
              )}
          </div>
        </div>

        {/* Feature cards... */}
      </div>
    </MainLayout>
  );
};

export default DashboardPage;
```

### 📊 Database Query Analysis

**Query Performance**:

```sql
-- Single simple query (FAST!)
SELECT
  u.full_name,
  u.created_at,
  a.severity_level,
  a.created_at as assessment_date
FROM users u
JOIN students s ON s.user_id = u.id
LEFT JOIN assessments a ON a.student_id = s.id
WHERE u.id = :user_id
ORDER BY a.created_at DESC
LIMIT 1;
```

**Complexity**: ✅ O(1) - Index scan on user_id + created_at

**vs Previous Approach**:

```sql
-- Complex aggregation query (SLOWER)
SELECT
  COUNT(*) as total,
  AVG(total_score),
  severity_level,
  COUNT(*) as severity_count
FROM assessments
WHERE student_id = :student_id
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY severity_level;
```

**Complexity**: ❌ O(n) - Full scan of 30 days data

### ✅ Kết luận Vấn đề 3

**✅ HOÀN TOÀN KHẢ THI**

**Lợi ích**:

- ✅ Simple query → Fast response
- ✅ Easy to understand
- ✅ Less code complexity
- ✅ Matches user requirements exactly

**Trade-offs**:

- ⚠️ Không show trend (chỉ latest)
- ✅ But: Đủ cho welcome card!
- ✅ Trend có thể show ở Statistics page

**Phù hợp với code hiện tại**:

- ✅ User.created_at có sẵn ✓
- ✅ Assessment.severity_level có sẵn ✓
- ✅ Relationships đã setup ✓
- ✅ Chỉ cần thêm 1 endpoint mới ✓

---

## 📋 Tổng kết & Implementation Plan

### Vấn đề 1: Card Design

**Approach**: ✅ Hybrid (Consistent core + Flexible slots)
**Effort**: ~3 hours
**Priority**: P1

### Vấn đề 2: Config-Driven Form

**Approach**: ✅ JSON config schema
**Effort**: ~6 hours (schema + component)
**Priority**: P1

### Vấn đề 3: Simplified Dashboard

**Approach**: ✅ GET /dashboard/welcome (3 fields only)
**Effort**: ~2 hours
**Priority**: P1

### Timeline

**Phase 1** (2-3 days):

- [ ] Create InfoCard base component
- [ ] Implement dashboard endpoint
- [ ] Update WelcomeCard with real data

**Phase 2** (3-4 days):

- [ ] Design rating form schema
- [ ] Create ratingForm.json
- [ ] Implement DynamicRatingForm

**Phase 3** (1-2 days):

- [ ] Refactor other pages with InfoCard
- [ ] Testing & polish
- [ ] Documentation

**Total**: ~7-9 days work

---

**Status**: Analysis Complete ✅
**Ready for**: Implementation 🚀
