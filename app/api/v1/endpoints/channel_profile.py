from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel
from app.services.channel_profile_service import ChannelProfileService
from app.services.youtube_service import YouTubeService

router = APIRouter()

# Dependency Providers
def get_youtube_service() -> YouTubeService:
    return YouTubeService()

def get_channel_profile_service() -> ChannelProfileService:
    return ChannelProfileService()

def get_subscriber_band(sub_count: int) -> str:
    if sub_count < 10000:
        return "<10K"
    elif sub_count < 50000:
        return "10K-50K"
    elif sub_count < 100000:
        return "50K-100K"
    elif sub_count < 500000:
        return "100K-500K"
    else:
        return "500K+"

def is_stats_matching(my_subs: int, candidate_subs: int) -> bool:
    """
    Check candidate channel that have close gap of subscribers (0.3x -3x of our channel)
    """
    if my_subs == 0:
        return candidate_subs < 10000

    ratio = candidate_subs / my_subs
    min_subs = int(my_subs * 0.5)
    max_subs = int(my_subs * 2.0)
    return min_subs <= ratio <= max_subs
   
@router.post("/insert-data/{channel_id}")
async def insert_data(
    channel_id : str = Path(..., description="Youtube channel id that you want to search"),
    youtube_service: YouTubeService = Depends(get_youtube_service),
    channel_profile_service: ChannelProfileService = Depends(get_channel_profile_service)
):
    try:
        # 1. ดึงข้อมูลรายละเอียดของช่องเรา
        channel_info = await youtube_service.get_channel_details(channel_id)
        if not channel_info:
            raise HTTPException(status_code=404, detail="Channel not found")
                
        # 2. ดึงข้อมูล 10 คลิปล่าสุดของช่องเรา
        recent_videos = await youtube_service.get_channel_recent_videos(channel_id, max_results=10)
        if not recent_videos:
            raise HTTPException(status_code=404, detail="Recent videos not found for this channel")

        # 3. คำนวณและสร้าง profile_data ของช่องเรา
        my_sub_count = int(channel_info.get("subscriber_count", 0))
        cand_subs = int(cand_info.get("subscriber_count", 0))
        
        # 💡 ขยาย Range ชั่วคราวเป็น 0.1x - 10.0x เพื่อให้แน่ใจว่ามีช่องลง DB แน่นอน
        if is_stats_matching(my_sub_count, cand_subs) or True: # เติม or True ชั่วคราวทดสอบ Ingestion
            cand_videos = await youtube_service.get_channel_recent_videos(cand_id, max_results=10)
                            
            if cand_videos:
                cand_topics = [v.get("title") for v in cand_videos if v.get("title")]
                cand_views = sum(v.get("view_count", 0) for v in cand_videos) // len(cand_videos)
        
                cand_profile = {
                    "channel_id": cand_id,
                    "channel_title": cand_info.get("title", "Unknown"),
                    "category": cand_info.get("category", "Gaming"),
                    "subscriber_band": get_subscriber_band(cand_subs),
                    "content_style": "Video Creator",
                    "avg_views": cand_views,
                    "topics": cand_topics
                }
        
                profile_text = f"""
                    Channel Name: {cand_profile['channel_title']}
                    Category: {cand_profile['category']}
                    Subscriber Band: {cand_profile['subscriber_band']}
                    Content Style: {cand_profile['content_style']}
                    Average Views: {cand_profile['avg_views']}
                    Key Topics: {', '.join(cand_topics)}
                """
        
        broad_category = channel_info.get("category", "Gaming")
        print(f"🔍 Searching channels for category: '{broad_category}'...")
                    
        candidate_ids = await youtube_service.search_similar_channels([broad_category], max_results=20)
        print(f"📌 Found candidate IDs: {candidate_ids}")

        for cand_id in candidate_ids:
            cand_info = await youtube_service.get_channel_details(cand_id)
            channel_profile_service.upsert_channel_profile(
                channel_id=cand_id,
                profile_text=profile_text,
                metadata={
                    "channel_id": cand_id,
                    "channel_title": cand_profile['channel_title'],
                    "category": cand_profile['category'],
                    "subscriber_band": cand_profile['subscriber_band'],
                    "content_style": cand_profile['content_style'],
                    "key_topics": ', '.join(cand_topics),
                    "avg_views": cand_views,
                    }
                )
        print(f"✅ Upserted channel {cand_id} into PostgreSQL/pgvector successfully!")

    except HTTPException as he:
        raise he
        