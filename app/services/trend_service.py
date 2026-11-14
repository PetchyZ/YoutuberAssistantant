import json
import asyncio
import numpy as np
from datetime import datetime
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.exceptions import YouTubeAPIException
from google.genai.errors import ServerError, APIError

class TrendAnalyticsService:
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
    
    @staticmethod
    def calculate_view_velocity(published_at_str: str, view_count: int) -> float:
        """calculate growth rate of views (Views/Day)"""
        pub_date = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
        days_active = max((datetime.now(pub_date.tzinfo) - pub_date).days,1)
        return round(view_count / days_active, 2)

    async def analyze_category_trends(self, channel_videos: list, category_trending_videos: list, category_name: str) -> dict:
        # 1. Calculate Metrics
        our_velocities = [self.calculate_view_velocity(v['published_at'], int(v['view_count'])) for v in channel_videos]
        market_velocities = [self.calculate_view_velocity(v['published_at'], int(v['view_count'])) for v in category_trending_videos]

        avg_our_velocity = float(np.mean(our_velocities)) if our_velocities else 0.0
        avg_market_velocity = float(np.mean(market_velocities)) if market_velocities else 0.0

        market_titles = [v['title'] for v in category_trending_videos[:10]]
        our_titles = [v['title'] for v in channel_videos[:5]]

        # 2. send data to gemini to get content gap and trend insights
        prompt = f"""
        You are a YouTube Data Analyst & Trend Strategist.
        Analyze the current video trends for Category: '{category_name}'.

        Channel's Recent Titles: {our_titles}
        Channel Avg Velocity: {avg_our_velocity} views/day

        Top Trending Titles in Market: {market_titles}
        Market Avg Velocity: {avg_market_velocity} views/day

        Provide actionable trend insights and gap analysis in strict JSON format:
        {{
            "performance_summary": {{
                "channel_velocity_score": <number 1-10 relative to market>,
                "status": "<Behind Trend / On Par / Leading Trend>"
            }},
            "market_velocity": <number; use the Market Avg Velocity value above exactly>,
            "avg_velocity": <number; use the Channel Avg Velocity value above exactly>,
            "emerging_topics": [<string array of top 3 hot topics in this category>],
            "content_gaps": [<string array of 2-3 content ideas the channel is missing>],
            "actionable_next_steps": [<string array of 2 strategic advice>]
        }}
        """

        try:

            response = await self.generate_with_retry(
                        primary_model='gemini-3.5-flash',
                        contents=prompt,
                        )
            
            result_json = json.loads(response.text)
            # These are calculated metrics, so use the exact values from our code
            # instead of relying on the model to copy them accurately.
            result_json["market_velocity"] = avg_market_velocity
            result_json["avg_velocity"] = avg_our_velocity
            return result_json

        except Exception as e:
            return {"error": f"Failed to analyze trends: {str(e)}"}
