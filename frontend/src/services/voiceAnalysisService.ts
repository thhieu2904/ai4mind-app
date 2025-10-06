/**
 * Voice Analysis Service - API calls for voice analysis data
 */
import api from "./api";

export interface VoiceAnalysis {
  id: number;
  student_id: number;
  assessment_id?: number;
  audio_file_url?: string;
  transcription?: string;
  dominant_emotion?: string;
  sentiment_score?: number;
  processing_status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
}

export interface VoiceAnalysisDetail extends VoiceAnalysis {
  audio_features?: {
    pitch_mean: number;
    pitch_std: number;
    energy_mean: number;
    speech_rate: string;
    pause_count: number;
    voice_stability: number;
  };
  emotion_scores?: {
    happy: number;
    sad: number;
    angry: number;
    fearful: number;
    surprised: number;
    disgusted: number;
    neutral: number;
  };
  text_analysis?: {
    word_count: number;
    sentence_count: number;
    avg_sentence_length: number;
    sentiment_polarity: number;
    sentiment_subjectivity: number;
  };
  comprehensive_analysis?: string;
  recommendations?: string[];
}

export interface CombinedAnalysisResult {
  assessment: {
    id: number;
    total_score: number;
    severity_level: string;
    analysis: string;
    recommendations: string[];
  };
  voice_analysis: VoiceAnalysisDetail;
  combined_insights: {
    consistency_score: number;
    key_findings: string[];
    final_recommendations: string[];
    risk_level: "low" | "medium" | "high";
  };
}

export class VoiceAnalysisService {
  /**
   * Get list of voice analyses for current student
   */
  static async getVoiceAnalyses(
    page = 1,
    pageSize = 10
  ): Promise<{
    items: VoiceAnalysis[];
    total: number;
    page: number;
    page_size: number;
  }> {
    // Note: This endpoint might need student_id from user context
    const response = await api.get("/api/v1/voice-analyses/student/me", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  /**
   * Get detailed voice analysis by ID
   */
  static async getVoiceAnalysisDetail(
    id: number
  ): Promise<VoiceAnalysisDetail> {
    const response = await api.get(`/api/v1/voice-analyses/${id}`);
    return response.data;
  }

  /**
   * Submit voice analysis for existing assessment
   */
  static async submitVoiceAnalysis(data: {
    assessment_id: number;
    audio_file: File;
    language?: string;
    gender?: string;
  }): Promise<VoiceAnalysisDetail> {
    const formData = new FormData();
    formData.append("audio_file", data.audio_file);
    formData.append("assessment_id", data.assessment_id.toString());
    if (data.language) formData.append("language", data.language);
    if (data.gender) formData.append("gender", data.gender);

    const response = await api.post("/api/v1/assessments/voice", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  }

  /**
   * Get combined analysis (GAD-7 + Voice) result
   */
  static async getCombinedAnalysis(
    assessmentId: number
  ): Promise<CombinedAnalysisResult> {
    const response = await api.get(
      `/api/v1/assessments/${assessmentId}/combined`
    );
    return response.data;
  }

  /**
   * Get voice analysis summary statistics
   */
  static async getVoiceStats(): Promise<{
    total_analyses: number;
    average_sentiment: number;
    most_common_emotion: string;
    analysis_history: Array<{
      date: string;
      emotion: string;
      sentiment: number;
    }>;
  }> {
    const response = await api.get("/api/v1/voice-analyses/stats");
    return response.data;
  }
}
