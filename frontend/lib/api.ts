// frontend/lib/api.ts

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// --- Types Declaration ---
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
  resolution?: string;
  brightness_score?: number;
  contrast_score?: number;
  [key: string]: unknown;
}

export interface ThumbnailAnalysisResponse {
  status?: string;
  video_title?: string;
  thumbnail_url?: string;
  analysis?: {
    cv_analysis?: CVAnalysis;
    ai_evaluation?: AIEvaluation;
  };
  cv_analysis?: CVAnalysis;
  ai_evaluation?: AIEvaluation;
}

export interface AudienceSentimentSummary {
  positive_highlights?: string[];
  negative_or_critiques?: string[];
}

export interface PerformanceAnalysis {
  performance_score?: number;
  estimated_performance_verdict?: string;
  strengths?: string[];
  weaknesses?: string[];
  audience_sentiment_summary?: AudienceSentimentSummary;
  actionable_growth_tips?: string[];
}

export interface PerformanceResponse {
  video_title?: string;
  metadata?: {
    title?: string;
  };
  performance_analysis?: PerformanceAnalysis;
  comment_sentiment?: string;
  key_drivers?: string[];
  [key: string]: unknown;
}

export interface TrendPerformanceSummary {
  channel_velocity_score?: number | string;
  status?: string;
}

export interface TrendVelocityResponse {
  views_velocity_per_day?: number;
  category_trend_comparison?: string;
  performance_summary?: TrendPerformanceSummary;
  emerging_topics?: string[];
  content_gaps?: string[];
  actionable_next_steps?: string[];
  [key: string]: unknown;
}

export interface MatchedCreator {
  channel_name: string;
  similarity_score: number;
  collaboration_synergy_reason: string;
  proposed_collab_idea: string;
  [key: string]: unknown;
}

export interface CompetitorAnalysis {
  our_strengths?: string[];
  competitor_advantages?: string[];
  content_differentiator?: string;
  [key: string]: unknown;
}

export interface MatchmakingResponse {
  status?: string;
  matched_creators?: MatchedCreator[];
  competitor_analysis?: CompetitorAnalysis;
  [key: string]: unknown;
}

// --- API Functions ---

// Feature 1: Thumbnail Analysis
export const analyzeThumbnail = async (videoId: string, category: string): Promise<ThumbnailAnalysisResponse> => {
  const response = await axios.post(`${API_BASE_URL}/api/v1/thumbnail/thumbnail-analytics/${videoId}`, {
    video_id: videoId,
    category_context: category,
  });
  return response.data;
};

// Feature 2: Performance Drivers
export const analyzePerformance = async (videoId: string, category: string): Promise<PerformanceResponse> => {
  const response = await axios.post(`${API_BASE_URL}/api/v1/performance/performance-analytics/${category}/${videoId}`, {
    video_id: videoId,
    category_id: category
  });
  return response.data;
};

// Feature 3: Trend & Velocity Analytics
export const analyzeTrendVelocity = async (channelId: string): Promise<TrendVelocityResponse> => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/trend/trend-category-analytics/${channelId}`);
  return response.data;
};

// Feature 4: Creator Matchmaking
export const analyzeMatchmaking = async (channelId: string): Promise<MatchmakingResponse> => {
  const response = await axios.post(`${API_BASE_URL}/api/v1/matchmaking/match-making-analyze/${channelId}`, {
    channel_id: channelId,
  });
  return response.data;
};
