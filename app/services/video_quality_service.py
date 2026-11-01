import cv2
import asyncio
import numpy as np
import json
import tempfile
import os
import httpx
from google import genai
from google.genai.errors import ServerError, APIError
from google.genai import types
from app.core.config import settings
from app.core.exceptions import YouTubeAPIException

class VideoQualityService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate_with_retry(
            self, 
            contents: list, 
            primary_model: str = "gemini-3.5-flash", 
            fallback_models: list[str] = None, 
            max_retries: int = 2
        ):
            """
            Helper method สำหรับยิง Gemini API พร้อม Retry Logic และ Model Fallback
            """
            if fallback_models is None:
                # รายชื่อโมเดลสำรองกรณีตัวหลักติด 503 Overloaded[cite: 7]
                fallback_models = ["gemini-3.5-flash-lite"]
                
            models_to_try = [primary_model] + fallback_models
    
            for current_model in models_to_try:
                for attempt in range(max_retries):
                    try:
                        # ยิง API แบบ Async ผ่าน client.aio[cite: 7]
                        response = await self.client.aio.models.generate_content(
                            model=current_model,
                            contents=contents,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json"
                            )
                        )
                        return response
                    except (ServerError, APIError) as e:
                        # ตรวจจับทั้ง 503 ServerError หรือ Rate Limit/Overload[cite: 7]
                        print(f"⚠️ Model '{current_model}' hit error/503 (Attempt {attempt + 1}/{max_retries}): {e}")
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 1.5
                            await asyncio.sleep(wait_time)
                        else:
                            print(f"🔄 Switching to next fallback model from '{current_model}'...")
    
            # ถ้าพยายามครบทุกโมเดลแล้วยังไม่สำเร็จ[cite: 7]
            raise YouTubeAPIException("Gemini Vision AI is currently overloaded. Please try again shortly.")
    
    def analyze_video_pacing_and_frames(self, video_path: str) -> dict:
        """
        Use OpenCV for video pacing, brightness and sharpness and scence changing velocity (30 seconds.)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise YouTubeAPIException("ไม่สามารถเปิดไฟล์วิดีโอเพื่อวิเคราะห์ได้")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        brightness_list = []
        contrast_list = []
        frame_diffs = []

        prev_gray = None
        frame_count = 0

        #scan each frame (maximum 300 frames)
        max_frames_to_analyze = min(total_frames, int(fps * 30) if fps > 0 else 300)

        while cap.isOpened() and frame_count < max_frames_to_analyze:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 1. calculate Brightness & Contrast
            brightness_list.append(np.mean(gray))
            contrast_list.append(np.std(gray))

            # 2. calculate the different for each frame (Motion / Pacing)
            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                frame_diffs.append(np.mean(diff))

            prev_gray = gray
            frame_count += 1

        cap.release()

        return {
            "fps": fps,
            "analyzed_frames": frame_count,
            "avg_brightness": round(float(np.mean(brightness_list)), 2) if brightness_list else 0.0,
            "avg_contrast": round(float(np.mean(contrast_list)), 2) if contrast_list else 0.0,
            "visual_pacing_score": round(float(np.mean(frame_diffs)), 2) if frame_diffs else 0.0
        }

    async def evaluate_video_retention_potential(self, video_metadata: dict, cv_metrics: dict) -> dict:
        """
        Send Metadata and statistic from OpenCV to Gemini to analyze
        """
        prompt = f"""
        You are an expert YouTube Content Strategiest and Video Quality Analyst.
        Analyze the potential audience retention and video quality based on the provided metrics and details.

        Video Title: {video_metadata.get('title')}
        Video Description: {video_metadata.get('description')}
        Category/Contrast: YouTube Creator Content

        Pre-computed OpenCV Video Metrics (Intro / Pacing analysis):
        - Analyzed Frames: {cv_metrics.get('analyzed_frames')}
        - Average Brightness: {cv_metrics.get('avg_brightness')} / 255
        - Average Contrast: {cv_metrics.get('avg_contrast')}
        - Visual Pacing / Motion Intensity: {cv_metrics.get('visual_pacing_score')}

        Evaluate and return ONLY a JSON object with the following keys (No markdown formatting, no code blocks):
        {{
            "retention_potential_score": <number 1-10>,
            "hook_strength" : <number 1-10>,
            "visual_pacing_evaluation" : "<string describing if the pacing is too slow, too fast, or optimal>",
            "drop_off_risk_factors" : [<string array of 1-2 potential reasons viewers might click away>],
            "actionable_suggestions" : [<string array of 2 tips to improve viewer retention through the video>]
        }}
        """

        try:
            response = await self.generate_with_retry(
                            primary_model='gemini-3.5-flash',
                            contents=prompt,
            )
            result_json = json.loads(response.text)
        except Exception as e:
            raise YouTubeAPIException(f"Failed to evaluate video retention with AI: {str(e)}")