from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.core.config import settings
from app.core.exceptions import YouTubeAPIException, QuotaExceededException, ResourceNotFoundException

class YouTubeService:
    def __init__(self):
        # Initialize Google API Client
        try:
            self.youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        except Exception as e:
            raise YouTubeAPIException(f"Failed to initialize YouTube Client: {str(e)}")

    async def get_video_details(self, video_id: str) -> dict:
        """
        Request Metadata, Statistics and Title/Description from video
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()

            items = response.get("items", [])
            if not items:
                raise ResourceNotFoundException(resource_type="Video")

            video_data = items[0]
            snippet = video_data.get("snippet", {})
            stats = video_data.get("statistics", {})

            return {
                "video_id": video_id,
                "title" : snippet.get("title"),
                "description": snippet.get("description"),
                "channel_id" : snippet.get("channelId"),
                "channel_title" : snippet.get("channelTitle"),
                "published_at" : snippet.get("publishedAt"),
                "thumbnail_url" : snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "metrics" : {
                    "view_count" : int(stats.get("viewCount", 0)),
                    "like_count" : int(stats.get("likeCount", 0)),
                    "comment_count" : int(stats.get("commentCount", 0))
                }
            }

        except HttpError as e:
            if e.resp.status == 403 and "quotaExceeded" in str(e):
                raise QuotaExceededException()
            elif e.resp.status == 404:
                raise YouTubeAPIException(detail=f"YouTube API Error: {e.reason}")
            else:
                raise YouTubeAPIException(detail=f"Youtube API Error: {e.reason}")

        except Exception as e:
            if isinstance(e, (QuotaExceededException, ResourceNotFoundException, YouTubeAPIException)):
                raise e
            raise YouTubeAPIException(detail=f"Unexpected error: {str(e)}")

    async def get_video_comments(self, video_id: str, max_results: int = 50) -> list:
        """
        pull Top comments from video to sentiment analyse
        """
        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                order="relevance"
            )
            response = request.execute()

            comments = []
            for item in response.get("items", []):
                comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment_text)

            return comments


        except Exception as e:
            # catch non-comment video or call API unsuccessful.
            return []

    async def get_channel_recent_videos(self, channel_id: str, max_results: int = 10) -> list:
        """
        Fetch recent videos from a specific channel along with their view counts
        """
        try:
            # 1. Get recent video IDs from search endpoint
            search_request = self.youtube.search().list(
                part="snippet",
                channelId=channel_id,
                order="date",
                type="video",
                maxResults=max_results
            )
            search_response = search_request.execute()

            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            if not video_ids:
                return []

            # 2. Fetch statistics (viewCount) for those videos
            videos_request = self.youtube.videos().list(
                part="snippet, statistics",
                id=",".join(video_ids)
            )
            videos_response = videos_request.execute()

            results = []
            for item in videos_response.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                results.append({
                    "video_id" : item["id"],
                    "channel_name": snippet.get("channelTitle"),
                    "title" : snippet.get("title"),
                    "published_at" : snippet.get("publishedAt"),
                    "view_count": int(stats.get("viewCount", 0))
                })

            return results

        except HttpError as e:
            if e.resp.status == 403 and "quotaExceed" in str(e):
                raise QuotaExceededException()
            raise YouTubeAPIException(detail=f"YouTube API Error: {e.reason}")
        except Exception as e:
            raise YouTubeAPIException(detail=f"Failed to get channel videos: {str(e)}")

    async def get_category_trending_videos(self, category_id: str = "20", region_code: str = "TH", max_results: int = 10) -> list:
        """
        Fetch most popular trending videos for a given category ID
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                videoCategoryId=category_id,
                regionCode = region_code,
                maxResults = max_results
            )
            response = request.execute()

            results = []
            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                results.append({
                    "video_id": item["id"],
                    "title" : snippet.get("title"),
                    "published_at" : snippet.get("publishedAt"),
                    "view_count" : int(stats.get("viewCount", 0))
                })

            return results

        except HttpError as e:
            if e.resp.status == 403 and "quotaExceeded" in str(e):
                raise QuotaExceededException()
            raise YouTubeAPIException(detail=f"YouTube API Error: {e.reason}")
        except Exception as e:
            raise YouTubeAPIException(detail=f"Failed to get trending videos: {str(e)}")


    async def get_channel_details(self, channel_id: str) -> dict:
        """
        Fetch channel details including subscriber count, total views, and video count
        """
        try:
            # 1. call channels().list with statistic part
            request = self.youtube.channels().list(
                part = "snippet, statistics",
                id=channel_id
            )
            response = request.execute()

            items = response.get("items", [])
            if not items:
                raise ResourceNotFoundException(resource_type="Channel")

            channel_data = items[0]
            snippet = channel_data.get("snippet", {})
            stats = channel_data.get("statistics", {})

            return {
                "channel_id": channel_id,
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "custom_url": snippet.get("customUrl"),
                "subscriber_count": int(stats.get("viewCount", 0)),
                "total_views": int(stats.get("viewCount",0)),
                "video_count": int(stats.get("videoCount", 0)),
                "hidden_subscriber_count": stats.get("hiddenSubscriberCount", False)
            }

        except HttpError as e:
            if e.resp.status == 403 and "quotaExceeded" in str(e):
                raise QuotaExceededException()
            raise YouTubeAPIException(detail=f"YouTube API Error: {e.reason}")
        except Exception as e:
            if isinstance(e, (QuotaExceededException, ResourceNotFoundException, YouTubeAPIException)):
                raise e
            raise YouTubeAPIException(detail=f"failed to get channel details: {str(e)}")

    async def search_similar_channels(self, keywords: list[str], max_results: int = 5) -> list[str]:
        """
        find rival channel_id / channel that have the keywords
        """
        try:
            # combine 2-3 words using as a search query
            query = " ".join(keywords[:3]) if keywords else "Gaming"

            # Call YouTube Data API v3 (search.list)
            search_response = self.youtube.search().list(
                q = query,
                type="channel",
                part="id,snippet",
                maxResults=max_results,
                relevanceLanguage="th"
            ).execute()

            channel_ids = []
            for item in search_response.get("items", []):
                ch_id = item.get("id", {}).get("channelId")
                if ch_id:
                    channel_ids.append(ch_id)

            return channel_ids

        except Exception as e:
            print(f"Error in search_similar_channels: {e}")
            return []