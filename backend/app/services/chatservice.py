from fastapi import HTTPException, status
import httpx
import logging

from app.config import Settings

logger = logging.getLogger(__name__)


class ChatRequest:
    def __init__(self, message: str, settings: Settings):
        self.message = message
        self.settings = settings

    async def getModelResponse(self) -> str:
        async with httpx.AsyncClient() as client:
            try:
                logger.info(
                    f"Sending request to model API at {self.settings.MODEL_API_URL} with model {self.settings.MODEL_NAME}"
                )
                response = await client.post(
                    f"{self.settings.MODEL_API_URL}/api/chat",
                    json={
                        "model": self.settings.MODEL_NAME,
                        "messages": [
                            {"role": "user", "content": self.message}
                        ],
                        "stream": False,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"]
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