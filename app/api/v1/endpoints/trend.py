from fastapi import APIRouter, HTTPException, Query, Path
from app.services.trend_service import TrendAnalyticsService
from app.services.youtube_service import YouTubeService

router = APIRouter()
trend_service = TrendAnalyticsService()
youtube_service = YouTubeService()

@router.get("/trend-category-analytics/{channel_id}")
async def analyze_channel_trend(
    channel_id: str = Path(..., description="Youtube channel id that you want to analyze"),
    category_id: str = Query("20", description="YouTube Category ID (Ex 20=Gaming)")
):
    try:
        # pull video from our channel and trending video from the same category
        channel_videos = await youtube_service.get_channel_recent_videos(channel_id)
        trending_videos = await youtube_service.get_category_trending_videos(category_id)

        result = await trend_service.analyze_category_trends(
            channel_videos = channel_videos,
            category_trending_videos = trending_videos,
            category_name = category_id
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))