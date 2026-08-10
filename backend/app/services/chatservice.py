from fastapi import HTTPException, status
import httpx
import logging
import json
import re
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

    def is_trivial_request(self) -> bool:
        raw = self.message.strip().lower()
        if not raw:
            return True

        compact = re.sub(r"[^a-z0-9\s]", " ", raw)
        normalized = re.sub(r"\s+", " ", compact).strip()

        trivial_phrases = {
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "thanks", "thank you", "thanks a lot", "thanks you", "ok", "okay",
            "yes", "no", "fine", "good", "how are you", "what can you do",
            "what do you do", "who are you", "help", "hello there", "hi there"
        }

        if normalized in trivial_phrases:
            return True

        words = normalized.split()
        if len(words) <= 3 and normalized in {"hey", "hello", "hi", "how are you", "what up"}:
            return True

        if len(words) <= 2:
            simple_greeting = ["hi", "hello", "hey", "ok", "okay", "thanks"]
            if words and words[0] in simple_greeting:
                return True

        return False

    async def generate_title_with_llm(self) -> str | None:
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "model": self.settings.MODEL_NAME,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Return only a short human-readable title for this request. Keep it under 6 words and do not add punctuation."
                        },
                        {
                            "role": "user",
                            "content": f"Create a short title for this message: {self.message}"
                        }
                    ],
                    "stream": False
                }

                response = await client.post(
                    f"{self.settings.MODEL_API_URL}/api/chat",
                    json=payload,
                    timeout=60.0,
                )
                response.raise_for_status()

                data = await response.json()
                output = None
                if isinstance(data, dict):
                    message = data.get("message")
                    if isinstance(message, dict):
                        output = message.get("content")
                    elif isinstance(message, str):
                        output = message

                if not isinstance(output, str) or not output.strip():
                    output = self.message.strip()

                title = re.sub(r"\s+", " ", output.strip())
                title = title[:48].rstrip() + ("..." if len(title) > 48 else "")
                return title
            except Exception as exc:
                logger.warning(f"Title LLM generation failed: {exc}")
                return None

    async def generate_title(self) -> str | None:
        if self.is_trivial_request():
            return None

        return await self.generate_title_with_llm()
    
    async def getModelResponse(self) -> str:
        summary = None
        title = None
        if not self.conversation_id:
            cd.create_conversation(self)
            self.conversation_id = cd.get_last_conversation_id(self)
            try:
                title = await self.generate_title()
                if title:
                    cd.update_conversation_title(self.conversation_id, title)
            except Exception as exc:
                logger.warning(f"Title generation aborted for conversation {self.conversation_id}: {exc}")
                title = None
        else:
            title = cd.get_conversation_title(self.conversation_id)

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
                    return {
                        "response": textresponse,
                        "conversation_id": self.conversation_id,
                        "title": title,
                    }
            
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
            
    
