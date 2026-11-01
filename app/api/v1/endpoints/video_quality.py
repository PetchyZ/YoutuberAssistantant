from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.services.youtube_service import YouTubeService
from app.services.video_quality_service import VideoQualityService
import shutil
import tempfile
import os

router = APIRouter()

def get_youtube_service():
    return YouTubeService()

def get_video_quality_service():
    return VideoQualityService()

@router.post("/video/{video_id}/analyze-quality")
async def analyze_video_quality(
    video_id:str,
    #if we have video upload
    file: UploadFile = File(None),
    yt_service: YouTubeService = Depends(get_youtube_service),
    vq_service: VideoQualityService = Depends(get_video_quality_service)
):
    """
    Endpoint for analyze video quality and hold watcher (Retention Potential)
    """
    try:
        # 1. Request Metadata from video by Youtube API
        video_metadata = await yt_service.get_video_details(video_id)

        cv_metrics = {
            "analyzed_frames": 0,
            "avg_brightness": 0.0,
            "avg_contrast" : 0.0,
            "visual_pacing_score" : 0.0
        }

        # 2. if we have video file used in OpenCV for analyze
        if file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                shutil.copyfileobj(file.file, temp_video)
                temp_video_path = temp_video.name

            try:
                cv_metrics = vq_service.analyze_video_pacing_and_frames(temp_video_path)
            finally:
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)

        # 3. Use gemini to analyze Retention from Metadata + CV Metrics
        ai_evaluation = await vq_service.evaluate_video_retention_potential(
            video_metadata = video_metadata,
            cv_metrics = cv_metrics
        )

        return {
            "status": "success",
            "video_id": video_id,
            "video_title": video_metadata.get("title"),
            "cv_metrics": cv_metrics,
            "retention_evaluation": ai_evaluation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

