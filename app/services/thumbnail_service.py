import asyncio
import json
import httpx
from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError
from PIL import Image
import io

from app.core.config import settings
from app.services.image_utils import ImageAnalyzerUtil
from app.core.exceptions import YouTubeAPIException

class ThumbnailService:
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
    
    async def fetch_image_from_url(self, url: str) -> bytes:
        """pull image file from URL (such as youtube thumbnail url)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise YouTubeAPIException("Unable to fetch thumbnail image from URL.")
            return response.content

    async def analyze_thumbnail(self, image_url: str, category_context: str = "General") -> dict:
        # 1. request a image and calculate a CV Metrics
        image_bytes = await self.fetch_image_from_url(image_url)
        cv_metrics = ImageAnalyzerUtil.analyze_basic_metrics(image_bytes)
        pil_image = Image.open(io.BytesIO(image_bytes))

        # 2. prepare a prompt with research criteria
        prompt = f"""
        You are an expert YouTube Thumbnail Analyzer based on audience psychology and computer vision research.
        Analyze the provided YouTube thumbnail image for a video in the category: '{category_context}'.

        Evaluate based on:
        1. Visual Saliency & Focal Point (Clear subject, good contrast)
        2. Facial Expression & Emotion (If human face present)
        3. Text Legibility (Short, high contrast, readable on mobile)
        4. Curiosity Gap & Click-Through Potential

        Additional Pre-computed Image Metrics:
        - Image Resolution: {cv_metrics['resolution']}
        - Measured Brightness: {cv_metrics['brightness_score']}/255
        - Measured Contrast: {cv_metrics['contrast_score']}

        Return ONLY a JSON object with the following keys (No markdown formatting, no code blocks):
        {{
            "overall_score": <number 1-10>,
            "criteria_breakdown": {{
                "visual_clarity": <number 1-10>,
                "text_readability": <number 1-10>,
                "emotional_hook": <number 1-10>
            }},
            "strengths": [<string array of 2-3 key strengths>],
            "weaknesses": [<string array of 1-2 points to improve>],
            "actionable_recommendations": [<string array of 2 actionable tips>]
        }}
        """

        # 3. Call Gemini Vision API
        try:
            response = await self.generate_with_retry(
                            primary_model='gemini-3.5-flash',
                            contents=[pil_image, prompt],
            )

            result_json = json.loads(response.text)

            # combine CV Metrics into a response
            return {
                "cv_analysis" : cv_metrics,
                "ai_evaluation" : result_json
            }
        
        except Exception as e:
            raise YouTubeAPIException(f"Failed to analyze thumbnail with Vision Model: {str(e)}")