import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import MainLayout from "../../components/layout/MainLayout";
import "./AssessmentPage.css";

// GAD-7 Questions in Vietnamese
const GAD7_QUESTIONS = [
  "Cảm thấy lo lắng, bồn chồn hoặc căng thẳng",
  "Không thể ngừng lo lắng hoặc kiểm soát được sự lo lắng",
  "Lo lắng quá nhiều về nhiều vấn đề khác nhau",
  "Khó thư giãn",
  "Bồn chồn đến mức khó có thể ngồi yên",
  "Dễ cáu gắt hoặc khó chịu",
  "Cảm thấy sợ hãi như thể điều gì đó tồi tệ sắp xảy ra",
];

const ANSWER_OPTIONS = [
  { value: 0, label: "Không có ngày nào" },
  { value: 1, label: "Vài ngày" },
  { value: 2, label: "Hơn một nửa số ngày" },
  { value: 3, label: "Gần như mỗi ngày" },
];

const AssessmentPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<(number | null)[]>(
    new Array(GAD7_QUESTIONS.length).fill(null)
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAnswerSelect = (value: number) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = value;
    setAnswers(newAnswers);
  };

  const handleNext = async () => {
    if (currentQuestion < GAD7_QUESTIONS.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Calculate total score
      const totalScore = answers.reduce(
        (sum: number, ans) => sum + (ans || 0),
        0
      );

      // Submit to backend and save to database
      setIsSubmitting(true);
      try {
        const response = await api.post("/api/v1/assessments/", {
          answers: answers.map((a) => a || 0), // Convert nulls to 0
          functional_impairment: 0,
          notes: null,
        });

        const assessmentData = response.data;

        // Navigate to results with assessment_id (IMPORTANT!)
        navigate("/assessment/results", {
          state: {
            assessmentId: assessmentData.id,
            score: assessmentData.total_score,
            severity: assessmentData.severity_level,
            analysis: assessmentData.analysis,
            recommendations: assessmentData.recommendations,
            answers: assessmentData.answers,
          },
        });
      } catch (error) {
        console.error("Failed to submit assessment:", error);
        alert("Không thể lưu kết quả. Vui lòng thử lại.");
        setIsSubmitting(false);
      }
    }
  };

  const handleBack = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    } else {
      navigate("/dashboard");
    }
  };

  const isAnswered = answers[currentQuestion] !== null;
  const progress = ((currentQuestion + 1) / GAD7_QUESTIONS.length) * 100;

  return (
    <MainLayout>
      <div className="assessment-container">
        {/* Header with back button */}
        <div className="assessment-header">
          <button className="back-button" onClick={handleBack}>
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
          <h1 className="assessment-title">Đánh giá GAD-7</h1>
          <div className="header-spacer"></div>
        </div>

        {/* Progress indicator */}
        <div className="progress-section">
          <div className="progress-label">
            Câu hỏi {currentQuestion + 1}/{GAD7_QUESTIONS.length}
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Question card */}
        <div className="question-card">
          <div className="question-number">Câu {currentQuestion + 1}</div>
          <h2 className="question-text">
            Trong 2 tuần qua, bạn có thường xuyên bị làm phiền bởi vấn đề sau
            không?
          </h2>
          <p className="question-topic">{GAD7_QUESTIONS[currentQuestion]}</p>
        </div>

        {/* Answer options */}
        <div className="answers-section">
          {ANSWER_OPTIONS.map((option) => (
            <button
              key={option.value}
              className={`answer-option ${
                answers[currentQuestion] === option.value ? "selected" : ""
              }`}
              onClick={() => handleAnswerSelect(option.value)}
            >
              <div className="radio-button">
                {answers[currentQuestion] === option.value && (
                  <div className="radio-button-inner"></div>
                )}
              </div>
              <span className="answer-label">{option.label}</span>
            </button>
          ))}
        </div>

        {/* Navigation buttons */}
        <div className="navigation-section">
          <button
            className="continue-button"
            onClick={handleNext}
            disabled={!isAnswered || isSubmitting}
          >
            {isSubmitting
              ? "Đang xử lý..."
              : currentQuestion === GAD7_QUESTIONS.length - 1
                ? "Xem kết quả"
                : "Tiếp tục"}
          </button>
          {currentQuestion > 0 && (
            <button
              className="previous-button"
              onClick={() => setCurrentQuestion(currentQuestion - 1)}
            >
              Câu trước
            </button>
          )}
        </div>

        {/* Info text */}
        <div className="info-text">
          <p>
            Vui lòng trả lời thật lòng. Kết quả này sẽ giúp chúng tôi hiểu rõ
            hơn về tình trạng của bạn.
          </p>
        </div>
      </div>
    </MainLayout>
  );
};

export default AssessmentPage;
