import json
import asyncio
import traceback
from google import genai
from google.genai.errors import ServerError
from google.genai import types
from app.core.config import settings
from app.services.vector_service import VectorService
from app.core.exceptions import YouTubeAPIException

class MatchmakingService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.vector_service = VectorService()

    async def generate_with_retry(
            self, 
            primary_model: str = "gemini-3.5-flash",
            fallback_models: list[str] = None,
            prompt: str = "",
            max_retries: int = 2
        ):

        if fallback_models is None:
            fallback_models = ["gemini-3.5-flash-lite"]

        models_to_try = [primary_model] + fallback_models

        for current_model in models_to_try:
            for attempt in range(max_retries):
                try:
                    # print(f"🚀 Trying model: {current_model} (attempt {attempt + 1})")
                    response = await self.client.aio.models.generate_content(
                        model=current_model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )
                    return response
                except ServerError as e:
                    print(f"⚠️ Model '{current_model}' hit 503 Overloaded (Attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1.5) # รอนิดหน่อยแล้วยิงใหม่
                    else:
                        print(f"🔄 Switching to next fallback model...")

        # ถ้าลองครบทุกรุ่นและทุก retry แล้วยังไม่ได้ค่อยพ่น error
        raise ServerError("All Gemini models are currently overloaded. Please try again in a few minutes.")

    async def find_matches_and_analyze(self, target_channel_id: str, target_profile: dict) -> dict:
        # Safe extraction for views
        avg_views_raw = target_profile.get("avg_views", 0)
        try:
            avg_views = int(avg_views_raw) if avg_views_raw is not None else 0
        except (ValueError, TypeError):
            avg_views = 0

        topics_list = target_profile.get('topics', [])
        topics_str = ', '.join(topics_list) if isinstance(topics_list, list) else str(topics_list)

        # 1. Create Text Profile for Vector Embedding
        profile_text = f"""
        Channel Name: {target_profile.get('channel_title', 'Unknown Channel')}
        Category: {target_profile.get('category', '')}
        Subscriber Band: {target_profile.get('subscriber_band', '')}
        Content Style: {target_profile.get('content_style', '')}
        Average Views: {avg_views}
        Key Topics: {topics_str}
        """

        # 2. Save/Update channel in Vector DB
        metadata = {
            "channel_id": str(target_channel_id),
            "channel_title": str(target_profile.get("channel_title", "Unknown")),
            "category": str(target_profile.get("category", "")),
            "subscriber_band": str(target_profile.get("subscriber_band", "")),
            "avg_views": avg_views
        }

        self.vector_service.upsert_channel_profile(
            channel_id=target_channel_id,
            profile_text=profile_text,
            metadata=metadata
        )

        # 3. Find lookalike channels
        raw_similarity_results = self.vector_service.find_similar_channels(profile_text, top_k=5)

        similarity_results = [
            channel for channel in raw_similarity_results 
            if channel.get("channel_id") != target_channel_id
        ][:3]

        if not similarity_results:
            return {
                "status": "insufficient_data",
                "message": "No other candidate channels found in the database.",
                "matched_creators": [],
                "competitor_analysis": {}
            }

        # 4. Prompt Constraints
        prompt = f"""
        You are a YouTube Strategic Brand & Creator Collaboration Consultant.
        
        Target Channel Profile:
        {json.dumps(target_profile, ensure_ascii=False)}

        Retrieved Candidate Channels from Database:
        {json.dumps(similarity_results, ensure_ascii=False)}

        STRICT CONSTRAINTS:
        1. You MUST ONLY select channels present in the "Retrieved Candidate Channels from Database" list above for the `matched_creators` array.
        2. You MUST use the exact `channel_title` / `channel_name` from the provided candidate data.
        3. DO NOT invent, synthesize, or hallucinate any external channel names, handles, or IDs.

        Analyze the synergy and return ONLY a JSON object with this exact structure:
        {{
            "matched_creators": [
                {{
                    "channel_name": "<MUST be the exact name from the candidate channels list>",
                    "similarity_score": <number 0-1 from vector search candidate data>,
                    "collaboration_synergy_reason": "<why this channel is a good match>",
                    "proposed_collab_idea": "<specific video concept or crossover idea>"
                }}
            ],
            "competitor_analysis": {{
                "our_strengths": ["<strength 1>", "<strength 2>"],
                "competitor_advantages": ["<advantage 1>", "<advantage 2>"],
                "content_differentiator": "<how to stand out from these competitors>"
            }}
        }}
        """

        try:
            # ✅ แก้ไขชื่อรุ่นโมเดลเป็น gemini-3.5-flash
            response = await self.generate_with_retry(
                primary_model='gemini-3.5-flash',
                prompt=prompt
            )
            
            # ดึง Text ผลลัพธ์
            raw_text = response.text if response.text else "{}"
            
            # ทำความสะอาด Code Block Markdown (ถ้ามี)
            clean_str = str(raw_text).strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str[7:]
            elif clean_str.startswith("```"):
                clean_str = clean_str[3:]
            if clean_str.endswith("```"):
                clean_str = clean_str[:-3]

            return json.loads(clean_str.strip())

        except Exception as e:
            print("\n================== FULL ERROR TRACEBACK ==================")
            traceback.print_exc()
            print("==========================================================\n")
            
            err_msg = str(e).replace('"', "'")
            raise YouTubeAPIException(detail=f"Matchmaking failed: {err_msg}")