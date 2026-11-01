from fastapi import HTTPException, status

class YouTubeAPIException(HTTPException):
    def __init__(self, detail: str = "An error occurred with YouTube API", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        # บังคับรับเฉพาะ String บริสุทธิ์ ป้องกัน Crash
        super().__init__(status_code=status_code, detail=str(detail))

class QuotaExceededException(HTTPException):
    """Exception If Quota of Youtube API reach a maximum number"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "QUOTA_EXCEEDED",
                "message": "Youtube API quota exceeded, Fallback to category baseline analytics."
            }
        )

class ResourceNotFoundException(HTTPException):
    """Exception If video or channel not found (Private/Deleted/Wrong ID)"""
    def __init__(self, resource_type: str = "Video/Channel"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code" : "RESOURCE_NOT_FOUND",
                "message" : f"The requested {resource_type} could not be found or is set to private."
            }
        )