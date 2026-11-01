import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';


//Feature 1: Thumnail Analyzer 
export interface CriteriaBreakdown {
  visual_clarity: number;
  text_readability: number;
  emotional_hook: number;
}

export interface AIEvaluation {
  overall_score: number;
  criteria_breakdown: CriteriaBreakdown;
  strengths: string[];
  weaknesses: string[];
  actionable_recommendations: string[];
}

export interface CVAnalysis {
  brightness_score: number;
  contrast_score: number;
  resolution: string;
}

// 💡 เพิ่ม analysis หรือปรับโครงสร้างให้ตรงกับ Backend
export interface ThumbnailAnalysisResponse {
  status?: string;
  video_title?: string;
  thumbnail_url?: string;
  analysis?: {
    cv_analysis: CVAnalysis;
    ai_evaluation: AIEvaluation;
  };
  // เผื่อไว้กรณี Backend คืนค่าแบบ Unpack Direct
  cv_analysis?: CVAnalysis;
  ai_evaluation?: AIEvaluation;
}

// -- API Service for Feature 1
export const analyzeThumbnail = async (
    videoId: string,
    categoryContext: string = 'General'
): Promise<ThumbnailAnalysisResponse> => {
    // call Endpoint of Feature 1
    const response = await axios.post(
    `${API_BASE_URL}/api/v1/analytics/${videoId}/analyze-thumbnail?category_context=${encodeURIComponent(categoryContext)}`    
    );
return response.data;
};

//Feature 4: Matchmaking
export interface MatchedCreator {
    channel_name : string;
    similarity_score: number;
    collaboration_synergy_reason: string;
    proposed_collab_idea: string;
}

export interface CompetitorAnalysis {
    our_strengths: string[];
    competitor_advantages: string[];
    content_differentiator: string;
}

export interface MatchmakingResponse{
    status?: string;
    message?: string;
    matched_creators: MatchedCreator[];
    competitor_analysis: CompetitorAnalysis;
}

export const analyzeChannel = async (channelId: string): Promise<MatchmakingResponse> => {
    const response = await axios.post(`${API_BASE_URL}/api/v1/matchmaking/analyze`, {
        channel_id: channelId,
    });
    return response.data;
}

