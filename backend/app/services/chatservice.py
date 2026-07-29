from fastapi import HTTPException, status
import httpx
import logging
import json
import app.db.conversationdao as cd
from app.config import Settings
from app.services.summaryservice import SummaryRequest
import app.services.conversationservice as cs    

logger = logging.getLogger(__name__)


class ChatRequest:
    def __init__(self, message: str, conversation_id: int | None, settings: Settings):
        self.message = message
        self.conversation_id = conversation_id
        self.settings = settings
    
    async def getModelResponse(self) -> str:
        summary = None
        if not self.conversation_id:
            cd.create_conversation(self)
            self.conversation_id = cd.get_last_conversation_id(self)

        message_count = cd.getMessagesCount(self.conversation_id)
        if message_count > self.settings.MESSAGE_THRESHOLD:
            summary = SummaryRequest(conversation_id=self.conversation_id, settings=self.settings).get_message_summary()

        cd.insert_message(self, role="user")

        async with httpx.AsyncClient() as client:
            try:
                logger.info(
                    f"Sending request to model API at {self.settings.MODEL_API_URL} with model {self.settings.MODEL_NAME}"
                )
                parts = []
                # Use an explicit streaming request so we can consume newline-delimited
                # JSON objects from the model API as they arrive.
                async with client.stream(
                    "POST",
                    f"{self.settings.MODEL_API_URL}/api/chat",
                    json={
                        "model": self.settings.MODEL_NAME,
                        "messages": cs.build_messages(self, self.settings, summary=summary, include_current_user=False),
                        "stream": True,
                    },
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()
                    textresponse = ""
                    # aiter_lines yields decoded text lines (one per newline)
                    async for raw_line in response.aiter_lines():
                        if not raw_line:
                            continue
                        line = raw_line.strip()
                        # Expect each line to be a JSON object; parse it into a Python dict
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            logger.info(f"Received non-JSON line from model API: {line}")
                            continue

                        # Server may signal completion with a field like `done`.
                        if obj.get("done") is True:
                            logger.info("Model API response stream completed.")
                            break

                        # Append partial content if present (adjust keys to your API shape)
                        content = None
                        if isinstance(obj.get("message"), dict):
                            content = obj["message"].get("content")
                        else:
                            content = obj.get("content")

                        if content:
                            logger.debug(f"Received line from model API: {content}")
                            parts.append(content)
                    logger.info(f"Final assembled response from model API: {''.join(parts)}")
                    textresponse = "".join(parts)
                    self.message = textresponse  # Update the message with the model's response
                    cd.insert_message(self, role="assistant")  # Store the model's response in the database
                    return {"response": textresponse, "conversation_id": self.conversation_id}
            
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
            
    
