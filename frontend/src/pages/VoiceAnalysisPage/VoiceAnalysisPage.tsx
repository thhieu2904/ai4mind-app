import React, { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import MainLayout from "../../components/layout/MainLayout";
import api from "../../services/api";
import "./VoiceAnalysisPage.css";

interface LocationState {
  assessmentId?: number;
  gad7Score?: number;
  gad7Severity?: string;
}

// Recording prompts in Vietnamese
const RECORDING_PROMPTS = [
  {
    id: 1,
    category: "daily",
    text: "Hãy kể về một ngày điển hình của bạn, từ khi thức dậy đến khi đi ngủ.",
    duration: 60,
  },
  {
    id: 2,
    category: "emotion",
    text: "Hãy mô tả cảm xúc của bạn trong tuần qua. Có điều gì làm bạn vui hoặc buồn không?",
    duration: 60,
  },
  {
    id: 3,
    category: "future",
    text: "Bạn có kế hoạch gì cho tương lai gần? Bạn cảm thấy thế nào về những kế hoạch đó?",
    duration: 60,
  },
  {
    id: 4,
    category: "emotion",
    text: "Khi gặp khó khăn, bạn thường xử lý như thế nào? Có ai bạn thường chia sẻ không?",
    duration: 60,
  },
];

const VoiceAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  // Get assessment data from navigation state OR load from backend
  const state = location.state as LocationState;
  const [assessmentId, setAssessmentId] = useState<number | null>(
    state?.assessmentId || null
  );
  const [gad7Score, setGad7Score] = useState<number>(state?.gad7Score || 0);
  const [gad7Severity, setGad7Severity] = useState<string>(
    state?.gad7Severity || ""
  );

  // Assessment selection state
  const [loadingAssessments, setLoadingAssessments] = useState(true);
  const [showAssessmentSelection, setShowAssessmentSelection] =
    useState(!assessmentId);

  const [selectedLanguage, setSelectedLanguage] = useState("vi");
  const [userGender, setUserGender] = useState<string>("other"); // Auto-detect from profile
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [showPrompts, setShowPrompts] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState<
    (typeof RECORDING_PROMPTS)[0] | null
  >(null);

  // All useRef hooks must be declared before any conditional logic
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<number | null>(null); // Fixed: use number instead of NodeJS.Timeout
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load student profile to get gender
  useEffect(() => {
    const loadStudentProfile = async () => {
      try {
        if (user?.role === "STUDENT") {
          const response = await api.get("/api/v1/students/me");
          const studentProfile = response.data;
          if (studentProfile.gender) {
            setUserGender(studentProfile.gender);
            console.log(
              "📊 Auto-detected gender from profile:",
              studentProfile.gender
            );
          }
        }
      } catch (error) {
        console.warn(
          "⚠️ Could not load student profile for gender detection:",
          error
        );
        // Fallback to default "other"
      }
    };

    loadStudentProfile();
  }, [user]);

  // Load available assessments - OPTIMIZED with /latest endpoint
  useEffect(() => {
    const loadAssessments = async () => {
      try {
        setLoadingAssessments(true);

        // OPTIMIZATION: Use /latest endpoint instead of loading all assessments
        // Old: GET /api/v1/assessments/ → Returns ALL assessments (slow!)
        // New: GET /api/v1/assessments/latest → Returns only latest (fast!)
        try {
          console.log("🚀 Calling /api/v1/assessments/latest...");
          const response = await api.get("/api/v1/assessments/latest");
          const latestAssessment = response.data;

          // Auto-select latest assessment
          setAssessmentId(latestAssessment.id);
          setGad7Score(latestAssessment.total_score);
          setGad7Severity(latestAssessment.severity_level);
          setShowAssessmentSelection(false); // Go directly to voice analysis
          console.log(
            `📋 Loaded latest assessment: ${latestAssessment.total_score}/21 (${latestAssessment.severity_level})`
          );
        } catch (error: any) {
          // 404 = No assessments found
          if (error.response?.status === 404) {
            console.log(
              "📝 No assessments found, user needs to complete GAD-7 first"
            );
            setShowAssessmentSelection(true); // Show "need GAD-7" message
          } else {
            throw error; // Re-throw other errors
          }
        }
      } catch (error) {
        console.error("❌ Failed to load assessments:", error);
        setShowAssessmentSelection(true); // Show error state
      } finally {
        setLoadingAssessments(false);
      }
    };

    // FIX: Support both uppercase and lowercase roles (backend uses UPPERCASE enum)
    console.log("🔍 User role check:", user?.role, "Type:", typeof user?.role);
    if (user?.role === "STUDENT") {
      console.log("✅ User is student, loading assessments...");
      loadAssessments();
    } else {
      console.log("⚠️ User is not student, role:", user?.role);
    }
  }, [user]); // ✅ useEffect dependency array

  // Show simple "need GAD-7" message if no assessments
  if (showAssessmentSelection) {
    return (
      <MainLayout>
        <div className="voice-analysis-container">
          <div className="voice-header">
            <button
              className="back-button"
              onClick={() => navigate("/dashboard")}
              aria-label="Quay lại dashboard"
            >
              ←
            </button>
            <h1 className="voice-title">Phân tích giọng nói</h1>
            <div className="header-spacer"></div>
          </div>

          {loadingAssessments ? (
            <div className="loading-message">
              <p>🔄 Đang kiểm tra đánh giá GAD-7...</p>
            </div>
          ) : (
            <div className="error-message">
              <h2>📝 Cần đánh giá GAD-7 trước</h2>
              <p>
                Bạn cần thực hiện đánh giá GAD-7 trước khi ghi âm phân tích
                giọng nói.
              </p>
              <button
                onClick={() => navigate("/assessment")}
                className="btn-primary"
              >
                Bắt đầu đánh giá GAD-7
              </button>
            </div>
          )}
        </div>
      </MainLayout>
    );
  }

  const handleBackToDashboard = () => {
    navigate("/dashboard");
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Try to use audio/wav if supported, otherwise fall back to webm
      let mimeType = "audio/webm";
      if (MediaRecorder.isTypeSupported("audio/wav")) {
        mimeType = "audio/wav";
      } else if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
        mimeType = "audio/webm;codecs=opus";
      }

      console.log("🎤 VoiceAnalysisPage - Recording with mimeType:", mimeType);

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mimeType,
        });
        console.log(
          "✅ Recording stopped. Blob type:",
          audioBlob.type,
          "Size:",
          audioBlob.size
        );
        setAudioBlob(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("Không thể truy cập microphone. Vui lòng cho phép quyền truy cập.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    }
  };

  // Convert Blob to WAV format using Web Audio API
  const convertToWav = async (blob: Blob): Promise<Blob> => {
    try {
      console.log(
        "🔄 Starting conversion. Input blob type:",
        blob.type,
        "Size:",
        blob.size
      );

      // If already WAV, return as is
      if (blob.type === "audio/wav" || blob.type === "audio/x-wav") {
        console.log("✅ Already WAV format, no conversion needed");
        return blob;
      }

      const audioContext = new AudioContext();
      const arrayBuffer = await blob.arrayBuffer();
      console.log("📊 ArrayBuffer size:", arrayBuffer.byteLength);

      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      console.log(
        "🎵 Decoded audio:",
        audioBuffer.duration,
        "seconds",
        audioBuffer.numberOfChannels,
        "channels"
      );

      // Convert to WAV format
      const wav = audioBufferToWav(audioBuffer);
      const wavBlob = new Blob([wav], { type: "audio/wav" });
      console.log("✅ Converted to WAV. Size:", wavBlob.size);

      await audioContext.close();
      return wavBlob;
    } catch (error) {
      console.error("❌ Error converting to WAV:", error);
      throw error;
    }
  };

  // Helper function to convert AudioBuffer to WAV format
  const audioBufferToWav = (buffer: AudioBuffer): ArrayBuffer => {
    const numOfChan = buffer.numberOfChannels;
    const length = buffer.length * numOfChan * 2 + 44;
    const bufferArray = new ArrayBuffer(length);
    const view = new DataView(bufferArray);
    const channels: Float32Array[] = [];
    let offset = 0;
    let pos = 0;

    // Write WAV header
    const setUint16 = (data: number) => {
      view.setUint16(pos, data, true);
      pos += 2;
    };
    const setUint32 = (data: number) => {
      view.setUint32(pos, data, true);
      pos += 4;
    };

    // "RIFF" chunk descriptor
    setUint32(0x46464952); // "RIFF"
    setUint32(length - 8); // file length - 8
    setUint32(0x45564157); // "WAVE"

    // "fmt " sub-chunk
    setUint32(0x20746d66); // "fmt "
    setUint32(16); // subchunk1size
    setUint16(1); // audio format (1 is PCM)
    setUint16(numOfChan);
    setUint32(buffer.sampleRate);
    setUint32(buffer.sampleRate * 2 * numOfChan); // byte rate
    setUint16(numOfChan * 2); // block align
    setUint16(16); // bits per sample

    // "data" sub-chunk
    setUint32(0x61746164); // "data"
    setUint32(length - pos - 4); // subchunk2size

    // Write interleaved data
    for (let i = 0; i < buffer.numberOfChannels; i++) {
      channels.push(buffer.getChannelData(i));
    }

    while (pos < length) {
      for (let i = 0; i < numOfChan; i++) {
        let sample = Math.max(-1, Math.min(1, channels[i][offset])); // clamp
        sample = sample < 0 ? sample * 0x8000 : sample * 0x7fff; // convert to 16-bit
        view.setInt16(pos, sample, true);
        pos += 2;
      }
      offset++;
    }

    return bufferArray;
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Check file type
      const allowedTypes = [
        "audio/wav",
        "audio/mp3",
        "audio/mpeg",
        "audio/m4a",
        "audio/x-m4a",
      ];
      if (
        !allowedTypes.includes(file.type) &&
        !file.name.match(/\.(wav|mp3|m4a)$/i)
      ) {
        alert(
          "Định dạng file không hợp lệ. Vui lòng chọn file WAV, MP3 hoặc M4A."
        );
        return;
      }

      // Check file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert("File quá lớn. Vui lòng chọn file nhỏ hơn 10MB.");
        return;
      }

      setAudioBlob(file);
    }
  };

  const handleAnalyze = async () => {
    if (!audioBlob) {
      alert("Vui lòng ghi âm hoặc tải lên file âm thanh trước.");
      return;
    }

    if (!assessmentId) {
      alert(
        "Không tìm thấy thông tin đánh giá GAD-7. Vui lòng làm lại từ đầu."
      );
      return;
    }

    setIsUploading(true);

    try {
      console.log("🎯 ========== handleAnalyze START ==========");
      console.log("📍 assessmentId:", assessmentId);
      console.log("📍 gad7Score:", gad7Score);
      console.log("📍 gad7Severity:", gad7Severity);
      console.log("📍 audioBlob:", audioBlob);
      console.log("📍 audioBlob size:", audioBlob.size);
      console.log("📍 recordingTime:", recordingTime);

      // Convert to WAV before uploading
      let wavBlob: Blob;
      try {
        console.log("🚀 Starting audio processing...");
        wavBlob = await convertToWav(audioBlob);
        console.log("📤 Ready to upload WAV file. Size:", wavBlob.size);
      } catch (convertError) {
        console.error("❌ Conversion error:", convertError);
        console.log("⚠️ Attempting to send original blob as fallback...");
        // Fallback: try sending original with .wav extension
        wavBlob = new Blob([audioBlob], { type: "audio/wav" });
      }

      console.log("✅ Validation passed, starting analysis...");

      // Prepare FormData for ai-service /assessments/{id}/add-voice endpoint
      console.log("� Starting audio processing...");
      const formData = new FormData();
      formData.append("audio_file", wavBlob, "recording.wav"); // Note: "audio_file" not "file"
      formData.append("gender", userGender); // Auto-detected from profile

      // Add prompt_text if selected
      if (selectedPrompt) {
        formData.append("prompt_text", selectedPrompt.text);
        console.log("📋 Added prompt_text:", selectedPrompt.text);
      } else {
        formData.append(
          "prompt_text",
          "Hãy chia sẻ cảm xúc của bạn trong 2 tuần qua"
        );
      }

      console.log("📋 FormData prepared with file: recording.wav");
      console.log("📋 wavBlob size:", wavBlob.size);
      console.log("📋 wavBlob type:", wavBlob.type);
      console.log("📋 gender:", userGender);

      console.log("🚀 About to call API:");
      console.log("   URL:", `/api/v1/assessments/${assessmentId}/add-voice`);
      console.log("   Method: POST");
      console.log("   Headers: multipart/form-data");

      // Call ai-service add-voice endpoint (not voice-service!)
      const response = await api.post(
        `/api/v1/assessments/${assessmentId}/add-voice`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log("✅ API Response received:", response);
      console.log("📊 Response data:", response.data);

      const result = response.data;

      // Navigate to comprehensive results with the real data
      navigate("/comprehensive-results", {
        state: {
          assessmentId: result.assessment_id || assessmentId,
          gad7Score: result.gad7_score || gad7Score,
          gad7Severity: result.gad7_severity || gad7Severity,
          voiceAnalysisId: result.id,
          dominantEmotion: result.dominant_emotion,
          sentimentScore: result.sentiment_score,
          transcription: result.transcription,
          comprehensiveAnalysis: result.comprehensive_analysis,
          comprehensiveRecommendations: result.comprehensive_recommendations,
        },
      });
    } catch (error) {
      console.error("Analysis error:", error);
      alert(
        error instanceof Error
          ? error.message
          : "Có lỗi xảy ra khi phân tích. Vui lòng thử lại."
      );
    } finally {
      setIsUploading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <MainLayout>
      <div className="voice-analysis-container">
        {/* Header */}
        <div className="voice-header">
          <button className="back-button" onClick={handleBackToDashboard}>
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
          <h1 className="voice-title">Phân tích giọng nói</h1>
          <div className="header-spacer"></div>
        </div>

        {/* Top Buttons */}
        <div className="top-buttons">
          <button
            className="gradient-button"
            onClick={() => setShowInstructions(!showInstructions)}
          >
            Hướng dẫn ghi âm
          </button>
          <button
            className="gradient-button"
            onClick={() => setShowPrompts(!showPrompts)}
          >
            Bộ câu hỏi gợi ý
          </button>
        </div>

        {/* Instructions Modal */}
        {showInstructions && (
          <div className="modal-card">
            <h3 className="modal-title">Hướng dẫn ghi âm</h3>
            <ul className="instructions-list">
              <li>Tìm một nơi yên tĩnh để ghi âm</li>
              <li>Nói rõ ràng và tự nhiên, không cần gò bó</li>
              <li>Thời lượng tối thiểu: 30 giây</li>
              <li>Thời lượng đề xuất: 60-90 giây</li>
              <li>Bạn có thể chọn câu hỏi gợi ý để dễ dàng hơn</li>
            </ul>
            <button
              className="close-modal-button"
              onClick={() => setShowInstructions(false)}
            >
              Đóng
            </button>
          </div>
        )}

        {/* Prompts Modal */}
        {showPrompts && (
          <div className="modal-card">
            <h3 className="modal-title">Chọn câu hỏi gợi ý</h3>
            <div className="prompts-list">
              {RECORDING_PROMPTS.map((prompt) => (
                <button
                  key={prompt.id}
                  className={`prompt-item ${selectedPrompt?.id === prompt.id ? "selected" : ""}`}
                  onClick={() => {
                    setSelectedPrompt(prompt);
                    setShowPrompts(false);
                  }}
                >
                  <div className="prompt-category">{prompt.category}</div>
                  <div className="prompt-text">{prompt.text}</div>
                  <div className="prompt-duration">~{prompt.duration}s</div>
                </button>
              ))}
            </div>
            <button
              className="close-modal-button"
              onClick={() => setShowPrompts(false)}
            >
              Đóng
            </button>
          </div>
        )}

        {/* Selected Prompt Display */}
        {selectedPrompt && !showPrompts && (
          <div className="selected-prompt-card">
            <div className="selected-prompt-header">
              <span className="selected-prompt-label">Câu hỏi đã chọn:</span>
              <button
                className="change-prompt-button"
                onClick={() => setShowPrompts(true)}
              >
                Đổi câu hỏi
              </button>
            </div>
            <p className="selected-prompt-text">{selectedPrompt.text}</p>
          </div>
        )}

        {/* Main Recording Card */}
        <div className="recording-card">
          {/* Language Selection */}
          <div className="language-section">
            <label className="language-label">Ngôn ngữ:</label>
            <select
              className="language-select"
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
            >
              <option value="vi">Tiếng Việt</option>
              <option value="en">English</option>
            </select>
          </div>

          {/* Gender Display - Auto-detected */}
          <div className="gender-section">
            <label className="gender-label">
              Giới tính (tự động từ hồ sơ):
            </label>
            <div className="gender-display">
              {userGender === "male" && "👨 Nam"}
              {userGender === "female" && "👩 Nữ"}
              {userGender === "other" && "🧑 Khác"}
              {userGender === "prefer_not_to_say" && "🤐 Không muốn chia sẻ"}
            </div>
            <small className="gender-note">
              💡 Giới tính được lấy từ thông tin đăng ký để tối ưu phân tích
              giọng nói
            </small>
          </div>

          {/* Recording Timer */}
          {(isRecording || audioBlob) && (
            <div className="timer-display">
              {isRecording ? (
                <>
                  <div className="recording-indicator"></div>
                  <span>Đang ghi âm: {formatTime(recordingTime)}</span>
                </>
              ) : (
                <span>✓ Đã ghi âm: {formatTime(recordingTime)}</span>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="action-buttons-group">
            {/* Microphone Button */}
            <button
              className={`circle-button ${isRecording ? "recording" : ""}`}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isUploading}
            >
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                {isRecording ? (
                  <rect
                    x="6"
                    y="6"
                    width="12"
                    height="12"
                    strokeWidth={2}
                    fill="currentColor"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                )}
              </svg>
            </button>

            {/* Upload Button */}
            <button
              className="circle-button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isRecording || isUploading}
            >
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/wav,audio/mp3,audio/mpeg,audio/m4a"
              style={{ display: "none" }}
              onChange={handleFileUpload}
            />
          </div>

          {/* Analyze Button */}
          <button
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={!audioBlob || isUploading}
          >
            {isUploading ? "Đang phân tích..." : "Phân tích"}
          </button>
        </div>

        {/* Info Text */}
        <div className="info-text">
          <p>
            Ghi âm giọng nói của bạn để AI phân tích cảm xúc. Kết quả sẽ giúp
            đánh giá sức khỏe tinh thần chính xác hơn khi kết hợp với GAD-7.
          </p>
        </div>
      </div>
    </MainLayout>
  );
};

export default VoiceAnalysisPage;
