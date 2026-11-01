"use client";

import { useState } from "react";
import axios from "axios";
import {
  // Functions Imported from API Service (สมมติว่า API Backend พร้อม)
  analyzeThumbnail,
  analyzePerformance,
  analyzeTrendVelocity,
  analyzeMatchmaking,
  // Types Imported from API Service
  ThumbnailAnalysisResponse,
  PerformanceResponse,
  TrendVelocityResponse,
  MatchmakingResponse,
} from "@/lib/api";
import {
  Sparkles,
  Search,
  Loader2,
  Image as ImageIcon,
  Zap,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  BarChart3,
  LineChart,
  Users,
} from "lucide-react";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<
    "thumbnail" | "performance" | "trend" | "matchmaking"
  >("thumbnail");

  // --- States for Input/Loading/Data/Error ---
  // Input Video IDs / Channel ID
  const [videoId, setVideoId] = useState("");
  const [channelId, setChannelId] = useState("");
  // Context for Thumbnail
  const [categoryContext, setCategoryContext] = useState("General");

  // Loading States
  const [loading, setLoading] = useState(false);
  // Error State
  const [error, setError] = useState<string | null>(null);

  // Response Data States
  const [thumbnailData, setThumbnailData] =
    useState<ThumbnailAnalysisResponse | null>(null);
  const [performanceData, setPerformanceData] =
    useState<PerformanceResponse | null>(null);
  const [trendData, setTrendData] = useState<TrendVelocityResponse | null>(
    null,
  );
  const [matchmakingData, setMatchmakingData] =
    useState<MatchmakingResponse | null>(null);

  // --- Unified API Handler Function ---
  const handleAnalyze = async (
    e: React.FormEvent,
    featureType: typeof activeTab,
  ) => {
    e.preventDefault();
    const idToUse =
      featureType === "matchmaking" || featureType === "trend"
        ? channelId
        : videoId;
    if (!idToUse.trim()) {
      setError(
        featureType === "matchmaking" || featureType === "trend"
          ? "กรุณากรอก YouTube Channel ID"
          : "กรุณากรอก YouTube Video ID",
      );
      return;
    }

    setLoading(true);
    setError(null);
    // Reset data for the current feature
    setThumbnailData(null);
    setPerformanceData(null);
    setTrendData(null);
    setMatchmakingData(null);

    try {
      let result;
      switch (featureType) {
        case "thumbnail":
          result = await analyzeThumbnail(videoId, categoryContext);
          setThumbnailData(result?.analysis || result); // Handle nesting if needed
          break;
        case "performance":
          result = await analyzePerformance(videoId, categoryContext);
          setPerformanceData(result);
          break;
        case "trend":
          result = await analyzeTrendVelocity(channelId);
          setTrendData(result);
          break;
        case "matchmaking":
          result = await analyzeMatchmaking(channelId);
          setMatchmakingData(result);
          break;
      }
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(
          err.response?.data?.detail ||
            "เกิดข้อผิดพลาดในการดึงข้อมูล กรุณาลองใหม่อีกครั้ง",
        );
      } else {
        setError("เกิดข้อผิดพลาดในการดึงข้อมูล กรุณาลองใหม่อีกครั้ง");
      }
    } finally {
      setLoading(false);
    }
  };

  // Helper: Thumbnail Criteria Scores
  const visualClarity =
    thumbnailData?.ai_evaluation?.criteria_breakdown?.visual_clarity ?? 0;
  const textReadability =
    thumbnailData?.ai_evaluation?.criteria_breakdown?.text_readability ?? 0;
  const emotionalHook =
    thumbnailData?.ai_evaluation?.criteria_breakdown?.emotional_hook ?? 0;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header Section */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 text-indigo-400 px-4 py-1.5 rounded-full border border-indigo-500/20 text-sm font-medium">
            <Sparkles className="w-4 h-4" /> AI Content Creator Assistant -
            Dashboard v0.1.0
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            YouTube Analytics & Strategy
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto text-base">
            วิเคราะห์คุณภาพปก, ปัจจัยยอดวิว, อัตราเร่งการเติบโต
            และค้นหาพาร์ตเนอร์คอลแลบ ครบจบในที่เดียว
          </p>
        </div>
        {/* Tab Navigation */}
        <div className="flex justify-center border-b border-slate-800 overflow-x-auto">
          <div className="flex gap-2 md:gap-4 min-w-max pb-1">
            {(
              [
                {
                  id: "thumbnail",
                  label: "Thumbnail Analysis",
                  icon: ImageIcon,
                },
                {
                  id: "performance",
                  label: "Performance Drivers",
                  icon: BarChart3,
                },
                { id: "trend", label: "Trend & Velocity", icon: LineChart },
                {
                  id: "matchmaking",
                  label: "Creator Matchmaking",
                  icon: Users,
                },
              ] as const
            ).map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  setError(null);
                }}
                className={`pb-3 px-4 font-semibold transition flex items-center gap-2 border-b-2 text-sm md:text-base ${
                  activeTab === tab.id
                    ? "border-indigo-500 text-indigo-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <tab.icon className="w-4 h-4 md:w-5 h-5" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
        {/* Error Alert */}
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-xl text-center max-w-xl mx-auto text-sm animate-pulse">
            <AlertTriangle className="w-5 h-5 inline-block mr-2" /> {error}
          </div>
        )}
        {/* --- Dynamic Content Area Based on Active Tab --- */}
        <div className="space-y-8 animate-fade-in">
          {/* Universal Input Form */}
          <form
            onSubmit={(e) => handleAnalyze(e, activeTab)}
            className="max-w-3xl mx-auto"
          >
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <input
                  type="text"
                  placeholder={
                    activeTab === "matchmaking" || activeTab === "trend"
                      ? "ใส่ YouTube Channel ID (เช่น UCXxxx...)"
                      : "ใส่ YouTube Video ID (เช่น dQw4w9WgXcQ)"
                  }
                  value={
                    activeTab === "matchmaking" || activeTab === "trend"
                      ? channelId
                      : videoId
                  }
                  onChange={(e) =>
                    activeTab === "matchmaking" || activeTab === "trend"
                      ? setChannelId(e.target.value)
                      : setVideoId(e.target.value)
                  }
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3.5 pl-11 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                />
                <Search className="w-5 h-5 text-slate-500 absolute left-3.5 top-4" />
              </div>

              {activeTab === "thumbnail" && (
                <select
                  value={categoryContext}
                  onChange={(e) => setCategoryContext(e.target.value)}
                  className="bg-slate-900 border border-slate-800 text-slate-200 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="Gaming">Gaming</option>
                  <option value="Education">Education</option>
                  <option value="Entertainment">Entertainment</option>
                  <option value="Tech">Tech / Science</option>
                  <option value="Lifestyle">Lifestyle / Vlog</option>
                </select>
              )}

              {activeTab === "performance" && (
                <select
                  value={categoryContext}
                  onChange={(e) => setCategoryContext(e.target.value)}
                  className="bg-slate-900 border border-slate-800 text-slate-200 rounded-xl px-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="General">General</option>
                  <option value="Gaming">Gaming</option>
                  <option value="Education">Education</option>
                  <option value="Entertainment">Entertainment</option>
                  <option value="Tech">Tech / Science</option>
                  <option value="Lifestyle">Lifestyle / Vlog</option>
                </select>
              )}

              <button
                type="submit"
                disabled={loading}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800/50 text-white font-medium px-6 py-3.5 rounded-xl transition flex items-center justify-center gap-2 cursor-pointer"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Sparkles className="w-5 h-5" />
                )}
                วิเคราะห์
              </button>
            </div>
          </form>

          {/* Feature-Specific Results Renderers */}
          {loading && (
            <div className="text-center py-12 text-slate-500 flex flex-col items-center gap-4">
              <Loader2 className="w-10 h-10 animate-spin text-indigo-500" />
              กำลังประมวลผลข้อมูลด้วย AI...
            </div>
          )}

          {/* TAB 1: THUMBNAIL Analysis */}
          {activeTab === "thumbnail" && thumbnailData && !loading && (
            // [UI TAB 1 - ก๊อปปี้ส่วนแสดงผลจากโค้ดเดิมของคุณมาวางที่นี่]
            <div className="space-y-8">
              {/* Thumbnail Preview */}

              {/* Main Score */}
              <div className="md:col-span-7 space-y-6">
                {/* Results Section */}
                {thumbnailData && (
                  <div className="space-y-8">
                    {/* Thumbnail Preview & Main Score */}
                    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
                      <div className="md:col-span-5 flex flex-col items-center space-y-3">
                        <img
                          src={`https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`}
                          alt="Thumbnail Preview"
                          className="rounded-xl border border-slate-700 shadow-xl w-full object-cover aspect-video"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src =
                              `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
                          }}
                        />
                        <span className="text-xs text-slate-500">
                          Video ID: {videoId}
                        </span>
                      </div>

                      <div className="md:col-span-7 space-y-6">
                        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                          <div>
                            <h2 className="text-xl font-bold text-slate-100">
                              Overall Thumbnail Score
                            </h2>
                            <p className="text-slate-400 text-xs">
                              วิเคราะห์ด้วย Computer Vision + Gemini Vision
                            </p>
                          </div>
                          <div className="flex items-baseline gap-1 bg-indigo-500/10 border border-indigo-500/30 px-5 py-2.5 rounded-2xl">
                            <span className="text-4xl font-extrabold text-indigo-400">
                              {thumbnailData?.ai_evaluation?.overall_score ??
                                "-"}
                            </span>
                            <span className="text-slate-500 text-sm font-semibold">
                              /10
                            </span>
                          </div>
                        </div>

                        {/* Criteria Breakdown Progress Bars */}
                        <div className="space-y-4">
                          {/* Visual Clarity */}
                          <div>
                            <div className="flex justify-between text-xs font-semibold mb-1">
                              <span className="text-slate-300">
                                Visual Clarity (ความชัดเจนของจุดโฟกัส)
                              </span>
                              <span className="text-indigo-400">
                                {visualClarity}/10
                              </span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-2">
                              <div
                                className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                                style={{
                                  width: `${(visualClarity / 10) * 100}%`,
                                }}
                              />
                            </div>
                          </div>

                          {/* Text Readability */}
                          <div>
                            <div className="flex justify-between text-xs font-semibold mb-1">
                              <span className="text-slate-300">
                                Text Readability (ความอ่านง่ายของข้อความ)
                              </span>
                              <span className="text-indigo-400">
                                {textReadability}/10
                              </span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-2">
                              <div
                                className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                                style={{
                                  width: `${(textReadability / 10) * 100}%`,
                                }}
                              />
                            </div>
                          </div>

                          {/* Emotional Hook */}
                          <div>
                            <div className="flex justify-between text-xs font-semibold mb-1">
                              <span className="text-slate-300">
                                Emotional Hook (การส่งต่ออารมณ์/ดึงดูดสายตา)
                              </span>
                              <span className="text-indigo-400">
                                {emotionalHook}/10
                              </span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-2">
                              <div
                                className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                                style={{
                                  width: `${(emotionalHook / 10) * 100}%`,
                                }}
                              />
                            </div>
                          </div>
                        </div>

                        {/* Computer Vision Raw Metrics */}
                        {thumbnailData?.cv_analysis && (
                          <div className="pt-2 grid grid-cols-3 gap-3 text-center">
                            <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
                              <div className="text-[10px] text-slate-500 font-medium">
                                Resolution
                              </div>
                              <div className="text-xs font-bold text-slate-200 mt-0.5">
                                {thumbnailData.cv_analysis.resolution || "-"}
                              </div>
                            </div>
                            <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
                              <div className="text-[10px] text-slate-500 font-medium">
                                Brightness Score
                              </div>
                              <div className="text-xs font-bold text-slate-200 mt-0.5">
                                {thumbnailData.cv_analysis.brightness_score?.toFixed(
                                  1,
                                ) ?? "-"}
                                /255
                              </div>
                            </div>
                            <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
                              <div className="text-[10px] text-slate-500 font-medium">
                                Contrast Score
                              </div>
                              <div className="text-xs font-bold text-slate-200 mt-0.5">
                                {thumbnailData.cv_analysis.contrast_score?.toFixed(
                                  1,
                                ) ?? "-"}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Qualitative Feedback Section */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Strengths */}
                      <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl space-y-3">
                        <h3 className="font-bold text-emerald-400 flex items-center gap-2 text-base">
                          <CheckCircle className="w-5 h-5" /> จุดเด่นของภาพปก
                          (Strengths)
                        </h3>
                        <ul className="space-y-2">
                          {thumbnailData?.ai_evaluation?.strengths?.map(
                            (item, i) => (
                              <li
                                key={i}
                                className="bg-emerald-500/5 border border-emerald-500/10 text-slate-300 p-3 rounded-xl text-sm"
                              >
                                • {item}
                              </li>
                            ),
                          )}
                        </ul>
                      </div>

                      {/* Weaknesses */}
                      <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl space-y-3">
                        <h3 className="font-bold text-amber-400 flex items-center gap-2 text-base">
                          <AlertTriangle className="w-5 h-5" />{" "}
                          จุดที่ควรปรับปรุง (Weaknesses)
                        </h3>
                        <ul className="space-y-2">
                          {thumbnailData?.ai_evaluation?.weaknesses?.map(
                            (item, i) => (
                              <li
                                key={i}
                                className="bg-amber-500/5 border border-amber-500/10 text-slate-300 p-3 rounded-xl text-sm"
                              >
                                • {item}
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    </div>

                    {/* Actionable Recommendations */}
                    {thumbnailData?.ai_evaluation
                      ?.actionable_recommendations && (
                      <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-6 space-y-3">
                        <h3 className="font-bold text-indigo-300 text-base flex items-center gap-2">
                          <Lightbulb className="w-5 h-5" />{" "}
                          ข้อเสนอแนะเชิงรุกเพื่อเพิ่ม CTR (Actionable Tips)
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {thumbnailData.ai_evaluation.actionable_recommendations.map(
                            (tip, i) => (
                              <div
                                key={i}
                                className="bg-slate-950/60 border border-indigo-500/20 p-4 rounded-xl text-sm text-slate-200"
                              >
                                📌 {tip}
                              </div>
                            ),
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: PERFORMANCE Drivers */}
          {activeTab === "performance" && performanceData && !loading && (
            <div className="space-y-8">
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6">
                {/* Header & Title */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-100">
                      {performanceData.video_title ||
                        performanceData.metadata?.title}
                    </h2>
                    <p className="text-slate-400 text-sm mt-1">
                      ปัจจัยหลักขับเคลื่อนยอดวิว & ความรู้สึกผู้ชม
                    </p>
                  </div>

                  {/* Performance Score Badge */}
                  <div className="bg-indigo-500/10 border border-indigo-500/30 px-5 py-2.5 rounded-2xl flex items-center gap-3">
                    <Zap className="w-6 h-6 text-indigo-400" />
                    <div>
                      <div className="text-xs text-slate-400">
                        Performance Score
                      </div>
                      <div className="text-lg font-bold text-indigo-300">
                        {
                          performanceData.performance_analysis
                            ?.performance_score
                        }{" "}
                        / 10
                      </div>
                    </div>
                  </div>
                </div>

                {/* Verdict / Summary */}
                <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800/80">
                  <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                    Performance Verdict
                  </span>
                  <p className="text-sm text-slate-300 mt-1">
                    {performanceData.performance_analysis
                      ?.estimated_performance_verdict ?? "-"}
                  </p>
                </div>

                {/* Drivers / Sentiment UI (Grid 2 คอลัมน์) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Strengths */}
                  <div className="bg-slate-950/40 border border-emerald-500/20 rounded-xl p-5 space-y-3">
                    <h3 className="text-emerald-400 font-bold flex items-center gap-2">
                      <span>✅</span> Strengths (จุดเด่น)
                    </h3>
                    <ul className="space-y-2">
                      {performanceData.performance_analysis?.strengths?.map(
                        (item: string, idx: number) => (
                          <li
                            key={idx}
                            className="text-sm text-slate-300 bg-emerald-950/20 p-2.5 rounded-lg border border-emerald-500/10"
                          >
                            • {item}
                          </li>
                        ),
                      )}
                    </ul>
                  </div>

                  {/* Weaknesses */}
                  <div className="bg-slate-950/40 border border-rose-500/20 rounded-xl p-5 space-y-3">
                    <h3 className="text-rose-400 font-bold flex items-center gap-2">
                      <span>⚠️</span> Weaknesses (จุดที่ควรปรับปรุง)
                    </h3>
                    <ul className="space-y-2">
                      {performanceData.performance_analysis?.weaknesses?.map(
                        (item: string, idx: number) => (
                          <li
                            key={idx}
                            className="text-sm text-slate-300 bg-rose-950/20 p-2.5 rounded-lg border border-rose-500/10"
                          >
                            • {item}
                          </li>
                        ),
                      )}
                    </ul>
                  </div>
                </div>

                {/* Audience Sentiment Summary (Positive vs Negative) */}
                <div className="border-t border-slate-800 pt-6 space-y-4">
                  <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                    💬 Audience Sentiment Analysis (จากคอมเมนต์)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Positive Highlights */}
                    <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                      <span className="text-xs font-semibold text-emerald-400">
                        สิ่งที่ผู้ชมชื่นชอบ (Positive Highlights)
                      </span>
                      <ul className="mt-2 space-y-2">
                        {performanceData.performance_analysis?.audience_sentiment_summary?.positive_highlights?.map(
                          (item: string, idx: number) => (
                            <li
                              key={idx}
                              className="text-xs text-slate-300 bg-emerald-950/10 p-2 rounded-lg border border-emerald-500/10"
                            >
                              + {item}
                            </li>
                          ),
                        )}
                      </ul>
                    </div>

                    {/* Negative / Critiques */}
                    <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                      <span className="text-xs font-semibold text-rose-400">
                        ข้อติชม / สิ่งที่ผู้ชมบ่น (Critiques)
                      </span>
                      <ul className="mt-2 space-y-2">
                        {performanceData.performance_analysis?.audience_sentiment_summary?.negative_or_critiques?.map(
                          (item: string, idx: number) => (
                            <li
                              key={idx}
                              className="text-xs text-slate-300 bg-rose-950/10 p-2 rounded-lg border border-rose-500/10"
                            >
                              - {item}
                            </li>
                          ),
                        )}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Actionable Growth Tips */}
                <div className="bg-indigo-950/30 border border-indigo-500/30 rounded-xl p-5 space-y-3">
                  <h3 className="text-indigo-300 font-bold flex items-center gap-2">
                    🚀 Actionable Growth Tips (คำแนะนำสำหรับคลิปถัดไป)
                  </h3>
                  <div className="space-y-2">
                    {performanceData.performance_analysis?.actionable_growth_tips?.map(
                      (tip: string, idx: number) => (
                        <div
                          key={idx}
                          className="text-sm text-indigo-100 flex items-start gap-2 bg-indigo-900/20 p-3 rounded-lg border border-indigo-500/20"
                        >
                          <span className="font-bold text-indigo-400">
                            {idx + 1}.
                          </span>
                          <span>{tip}</span>
                        </div>
                      ),
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: TREND & VELOCITY */}
          {activeTab === "trend" && trendData && !loading && (
            // [UI TAB 3 - แสดงผล Views/Day Velocity, Category Trend]
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6">
              {/* 1. Performance Summary Card */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-4">
                <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                  📊 Performance Summary
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                    <div className="text-sm text-slate-400">
                      Channel Velocity Score
                    </div>
                    <div className="text-3xl font-extrabold text-indigo-400 mt-1">
                      {trendData.performance_summary?.channel_velocity_score ??
                        "-"}
                    </div>
                  </div>
                  <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                    <div className="text-sm text-slate-400">Status</div>
                    <div className="text-xl font-bold text-amber-400 mt-1">
                      {trendData.performance_summary?.status ?? "-"}
                    </div>
                  </div>
                </div>
              </div>

              {/* 2. Grid แสดง Emerging Topics และ Content Gaps */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Emerging Topics */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
                  <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                    🔥 Emerging Topics
                  </h3>
                  <ul className="space-y-2">
                    {trendData.emerging_topics?.map(
                      (topic: string, index: number) => (
                        <li
                          key={index}
                          className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 text-slate-300 text-sm flex items-start gap-2"
                        >
                          <span className="text-indigo-400 font-bold">•</span>{" "}
                          {topic}
                        </li>
                      ),
                    )}
                  </ul>
                </div>

                {/* Content Gaps */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
                  <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                    💡 Content Gaps
                  </h3>
                  <ul className="space-y-2">
                    {trendData.content_gaps?.map(
                      (gap: string, index: number) => (
                        <li
                          key={index}
                          className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 text-slate-300 text-sm flex items-start gap-2"
                        >
                          <span className="text-indigo-400 font-bold">•</span>{" "}
                          {gap}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              </div>

              {/* 3. Actionable Next Steps */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-4">
                <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                  🚀 Actionable Next Steps
                </h3>
                <div className="space-y-3">
                  {trendData.actionable_next_steps?.map(
                    (step: string, index: number) => (
                      <div
                        key={index}
                        className="bg-indigo-950/20 border border-indigo-500/20 p-4 rounded-xl flex items-start gap-3"
                      >
                        <div className="bg-indigo-500/10 text-indigo-400 font-bold px-2.5 py-1 rounded-lg text-sm">
                          #{index + 1}
                        </div>
                        <p className="text-slate-200 text-sm leading-relaxed self-center">
                          {step}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: CREATOR MATCHMAKING */}
          {activeTab === "matchmaking" && matchmakingData && !loading && (
            // [UI TAB 4 - ก๊อปปี้ส่วนแสดงผลจากโค้ดเดิมของคุณมาวางที่นี่]
            <div className="space-y-8">
              {/* 1. Matched Creators List */}
              <div className="grid gap-4 md:grid-cols-3">
                {matchmakingData.matched_creators?.map((creator, index) => (
                  <div
                    key={index}
                    className="p-4 bg-slate-800 rounded-xl border border-slate-700"
                  >
                    <h3 className="font-bold text-lg text-white">
                      {creator.channel_name}
                    </h3>
                    <p className="text-sm text-emerald-400 font-semibold mb-2">
                      Similarity: {Math.round(creator.similarity_score * 100)}%
                    </p>
                    <p className="text-xs text-slate-300 mb-2">
                      <strong>Synergy:</strong>{" "}
                      {creator.collaboration_synergy_reason}
                    </p>
                    <div className="bg-slate-900/60 p-2 rounded text-xs text-indigo-300">
                      💡 <strong>Collab Idea:</strong>{" "}
                      {creator.proposed_collab_idea}
                    </div>
                  </div>
                ))}
              </div>

              {/* 2. Strategic Competitor Analysis */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 space-y-6">
                <div>
                  <h4 className="text-emerald-400 font-bold mb-2">
                    Our Strengths
                  </h4>
                  <ul className="list-disc pl-5 text-sm text-slate-300 space-y-1">
                    {matchmakingData.competitor_analysis?.our_strengths?.map(
                      (item: string, idx: number) => (
                        <li key={idx}>{item}</li>
                      ),
                    )}
                  </ul>
                </div>

                <div>
                  <h4 className="text-amber-400 font-bold mb-2">
                    Competitor Advantages
                  </h4>
                  <ul className="list-disc pl-5 text-sm text-slate-300 space-y-1">
                    {matchmakingData.competitor_analysis?.competitor_advantages?.map(
                      (item: string, idx: number) => (
                        <li key={idx}>{item}</li>
                      ),
                    )}
                  </ul>
                </div>

                <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700">
                  <h4 className="text-purple-400 font-bold mb-1">
                    Content Differentiator
                  </h4>
                  <p className="text-sm text-slate-200">
                    {
                      matchmakingData.competitor_analysis
                        ?.content_differentiator
                    }
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
