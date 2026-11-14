from fastapi import APIRouter, HTTPException, Query, Path, Depends
from app.services.trend_service import TrendAnalyticsService
from app.services.youtube_service import YouTubeService

from app.models.trends import Trend
from app.models.channels import Channel
from sqlalchemy.orm import Session
from app.db.session import get_db
from sqlalchemy import select

router = APIRouter()
trend_service = TrendAnalyticsService()
youtube_service = YouTubeService()

@router.get("/trend-category-analytics/{channel_id}")
async def analyze_channel_trend(
    channel_id: str = Path(..., description="Youtube channel id that you want to analyze"),
    category_id: str = Query("20", description="YouTube Category ID (Ex 20=Gaming)"),
    db: Session = Depends(get_db),
):
    try:
        # pull video from our channel and trending video from the same category
        channel_videos = await youtube_service.get_channel_recent_videos(channel_id)
        channel_info = await youtube_service.get_channel_details(channel_id)
        trending_videos = await youtube_service.get_category_trending_videos(category_id)

        result = await trend_service.analyze_category_trends(
            channel_videos = channel_videos,
            category_trending_videos = trending_videos,
            category_name = category_id
        )

        #database
        existing = db.scalar(
            select(Channel).where(Channel.channel_code == channel_id)
            )
                
        if existing:
            channel_record = existing
        else:      
            channel_record = Channel(
                channel_code=channel_id,
                channel_name=channel_info["title"]
                )
            db.add(channel_record)
            db.flush()

            trend_record = Trend(
                channel_id=channel_record.id,
                recent_title=channel_videos[0]["title"] if channel_videos else "",
                top_market_title=trending_videos[0]["title"] if trending_videos else "",
                channel_velocity_summary=result["performance_summary"]["status"],
                emerging_topics=result["emerging_topics"],
                content_gaps=result["content_gaps"],
                next_step_recommends=result["actionable_next_steps"],
                market_velocity=result["market_velocity"],
                avg_velocity=result["avg_velocity"],
                channel_velocity_score=result["performance_summary"]["channel_velocity_score"],
            )

        db.add(trend_record)
        db.commit()
        db.refresh(trend_record)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))