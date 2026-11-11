import traceback
from fastapi import APIRouter, Depends, HTTPException
from app.services.youtube_service import YouTubeService
from app.services.thumbnail_service import ThumbnailService

from app.models.thumbnails import Thumbnail
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

def get_youtube_service():
    return YouTubeService()

def get_thumbnail_service():
    return ThumbnailService()

@router.get("/video/{video_id}")
async def get_video_analytics(
    video_id: str,
    yt_service: YouTubeService = Depends(get_youtube_service)
):
    """
    Endpoint to request Metadata and stat of video
    With Guardrail in case of get decline by request
    """
    data = await yt_service.get_video_details(video_id)
    return {
        "status" : "success",
        "data" : data
    }

@router.post("/thumbnail-analytics/{video_id}")
async def analyze_video_thumbnail(
    video_id: str,
    category_context: str = "General",
    yt_service: YouTubeService = Depends(get_youtube_service),
    thumb_service: ThumbnailService = Depends(get_thumbnail_service),
    db: Session = Depends(get_db),
):

    """
    Endpoint request a video + analyze thumbnail information
    """
    try:
        # 1. request information of Thumbnail from URL
        video_data = await yt_service.get_video_details(video_id)
        thumbnail_url = video_data.get("thumbnail_url")

        # 2. analyze thumbnail by ThumbnailService
        analysis_result = await thumb_service.analyze_thumbnail(
            image_url = thumbnail_url,
            category_context=category_context
    )

        print(analysis_result["ai_evaluation"])
        record = Thumbnail(
            video_id=video_id,
            strength_comments=analysis_result["ai_evaluation"]["strengths"],
            weakness_comments=analysis_result["ai_evaluation"]["weaknesses"],
            recommend_comments=analysis_result["ai_evaluation"]["actionable_recommendations"],
            visual_clarity_score=analysis_result["ai_evaluation"]["criteria_breakdown"]["visual_clarity"],
            text_readability_score=analysis_result["ai_evaluation"]["criteria_breakdown"]["text_readability"],
            emotional_hook_score=analysis_result["ai_evaluation"]["criteria_breakdown"]["emotional_hook"]
        )

        db.add(record)
        db.commit()
        db.refresh(record)

    except Exception as e:
            print("====== BACKEND ERROR TRACEBACK ======")
            traceback.print_exc()
            print("=====================================")
            raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "status": "success",
        "video_title": video_data.get("title"),
        "thumbnail_url": thumbnail_url,
        "cv_analysis": analysis_result["cv_analysis"],
        "ai_evaluation": analysis_result["ai_evaluation"]
    }

    