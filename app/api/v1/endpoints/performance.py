import traceback
from fastapi import APIRouter, HTTPException, Depends
from app.services.youtube_service import YouTubeService
from app.services.performance_service import PerformanceService

router = APIRouter()

@router.post("/performance-analytics/{category_context}/{video_id}")
async def analyze_video_performance(
    video_id:str,
    category_context: str = "General",
    yt_service: YouTubeService = Depends(),
    perf_service: PerformanceService = Depends()
):
    """
    Endpoint for second feature: pull statistic & comments and analyze pro & con of views
    """
    try:
        # 1. pull metadata from Youtube API (have Refusal Logic to prevent unfound url)
        video_metadata = await yt_service.get_video_details(video_id)

        # 2. pull Top Comments
        comments = await yt_service.get_video_comments(video_id)

        # 3. push data into gemini performnace service
        analysis_result = await perf_service.analyze_video_performance(
                video_metadata=video_metadata,
                comments=comments,
                category_context=category_context
        )

    except Exception as e:
        print("====== BACKEND ERROR TRACEBACK ======")
        traceback.print_exc()
        print("=====================================")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status" : "success",
        "video_id" : video_id,
        "metadata" : video_metadata,
        "performance_analysis" : analysis_result
    }