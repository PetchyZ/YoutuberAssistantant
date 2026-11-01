import traceback
from fastapi import APIRouter, Depends, HTTPException
from app.services.youtube_service import YouTubeService
from app.services.thumbnail_service import ThumbnailService
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
    thumb_service: ThumbnailService = Depends(get_thumbnail_service)
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

    