from fastapi import HTTPException, status
import httpx

from app.config import Settings


class ChatRequest:
    def __init__(self, message: str, settings: Settings):
        self.message = message
        self.settings = settings

    async def getModelResponse(self) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.settings.model_api_url}/api/chat",
                    json={"message": self.message},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"External API error: {exc}",
                ) from exc
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Error communicating with model API: {exc}",
                ) from exc