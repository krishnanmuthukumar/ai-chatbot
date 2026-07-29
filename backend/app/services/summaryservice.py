from fastapi import HTTPException, status
from app.config import Settings
import requests
import logging
import app.db.conversationdao as cd

logger = logging.getLogger(__name__)

class SummaryRequest:
     def __init__(self, conversation_id: int, settings: Settings):
        self.conversation_id = conversation_id
        self.settings = settings


     def get_message_summary(self):
        history = cd.get_conversation_history(self.conversation_id)
        message = [{
            "role": "system",
            "content": "You are a helpful assistant that provides concise text summaries."
        }]

        text_history = ", ".join(f"{role}: {content}" for role, content in history)
        message.append({
            "role": "user",
            "content": "Summarize this conversation history: " + text_history
        })

        logger.info("generated message: %s", message)
        try:
            summary_response = requests.post(
                f"{self.settings.MODEL_API_URL}/api/chat",
                json={
                    "model": self.settings.MODEL_NAME,
                    "messages": message,
                    "stream": False,
                },
                timeout=60.0,
            )
            summary_response.raise_for_status()

            data = summary_response.json()
            summary = ""
            if isinstance(data, dict):
                if isinstance(data.get("message"), dict):
                    summary = data["message"].get("content", "") or ""
                else:
                    summary = data.get("content") or data.get("text") or ""
            else:
                summary = str(data)
            logger.info("summary from model: %s", summary)
            return summary
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error communicating with model API: {err}",
            ) from err