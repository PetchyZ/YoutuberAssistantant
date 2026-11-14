import traceback
from fastapi import APIRouter, HTTPException, Depends
from app.services.youtube_service import YouTubeService
from app.services.performance_service import PerformanceService

from app.models.videos_quality import Video_quality
from app.models.videos import Video
from sqlalchemy.orm import Session
from app.db.session import get_db
from sqlalchemy import select

router = APIRouter()

@router.post("/performance-analytics/{category_context}/{video_id}")
async def analyze_video_performance(
    video_id:str,
    category_context: str = "General",
    yt_service: YouTubeService = Depends(),
    perf_service: PerformanceService = Depends(),
    db: Session = Depends(get_db),
):
    """
    Endpoint for second feature: pull statistic & comments and analyze pro & con of views
    """
    try:
        # 1. pull metadata from Youtube API (have Refusal Logic to prevent unfound url)
        video_data = await yt_service.get_video_details(video_id)

        # 2. pull Top Comments
        comments = await yt_service.get_video_comments(video_id)

        # 3. push data into gemini performnace service
        analysis_result = await perf_service.analyze_video_performance(
                video_metadata=video_data,
                comments=comments,
                category_context=category_context
        )

        #database
        existing = db.scalar(
            select(Video).where(Video.video_code == video_id)
            )
        
        if existing:
             video_record = existing
        else:      
            video_record = Video(
                video_code=video_id,
                title=video_data['title']
                )
            db.add(video_record)
            db.commit()
            db.refresh(video_record)

        video_quality_record = Video_quality(
            video_id = video_record.id,
            performance_summary = analysis_result["estimated_performance_verdict"],
            audience_positive_comments = analysis_result["audience_sentiment_summary"]["positive_highlights"],
            audience_negative_comments = analysis_result["audience_sentiment_summary"]["negative_or_critiques"],
            strength_comments = analysis_result["strengths"],
            weakness_comments = analysis_result["weaknesses"],
            recommend_comments = analysis_result["actionable_growth_tips"],
            performance_score = analysis_result["performance_score"],
        )

        db.add(video_quality_record)
        db.commit()
        db.refresh(video_quality_record)
                
    except Exception as e:
        print("====== BACKEND ERROR TRACEBACK ======")
        traceback.print_exc()
        print("=====================================")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status" : "success",
        "video_id" : video_id,
        "metadata" : video_data,
        "performance_analysis" : analysis_result
    }