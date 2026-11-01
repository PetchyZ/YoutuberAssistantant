import json
import asyncio
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.exceptions import YouTubeAPIException
from google.genai.errors import ServerError, APIError

class PerformanceService:
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
    
    async def analyze_video_performance(
            self,
            video_metadata: dict,
            comments: list[str],
            category_context: str = "General"
    ) -> dict:
        """
        Analyse pro & con and sentiment of watcher from metadata + comments
        """
        # get 20-30 comments for LLM processing
        formatted_comments = "\n".join([f"- {c}" for c in comments[:30]] if comments else "No comments available.")

        prompt = f"""
        You are an expert YouTube Data Analyst and Audience Behavior Researcher.
        Analyze the performance of the following YouTube video based on its metadata and audience comments.

        Video Category: {category_context}
        Video Title: {video_metadata.get('title')}
        View Count: {video_metadata.get('view_count')}
        Like Count: {video_metadata.get('like_count')}
        Comment Count: {video_metadata.get('comment_count')}

        Sample Audience Comments:
        {formatted_comments}

        Evaluate:
        1. Performance Drivers: Key elements driving or limiting views (title hook, engagement rate, topic interest).
        2. Audience Sentiment: What viewers love vs what they complain about.
        3. Strengths & Weaknesses: Core highlights and areas of improvement.

        Return ONLY a JSON object with the following keys (No markdown formatting, no code blocks):
        {{
            "performance_score": <number 1-10>,
            "estimated_performance_verdict": "<Short summary of why it got this view count>",
            "strengths": [<string array of 2-3 key strengths>],
            "weaknesses": [<string array of 1-2 points to improve>],
            "audience_sentiment_summary": {{
                "positive_highlights": [<string array of top praised aspects>],
                "negative_or_critiques": [<string array of viewer complaints/critiques>]
            }},
            "actionable_growth_tips": [<string array of 2-3 actionable tips for next video>]
        }}
        """
    
        try:

            response = await self.generate_with_retry(
                                        primary_model='gemini-3.5-flash',
                                        contents=prompt,
            )
            
            result_json = json.loads(response.text)
            return result_json

        except Exception as e:
            raise YouTubeAPIException(f"Failed to analyze video performance: {str(e)}")