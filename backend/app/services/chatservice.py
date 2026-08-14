from fastapi import HTTPException, status
import httpx
import logging
import json
import inspect
import re
import app.db.conversationdao as cd
from app.config import Settings
from app.services.summaryservice import SummaryRequest
import app.services.conversationservice as cs    

logger = logging.getLogger(__name__)

"""
ChatRequest class encapsulates the logic for handling chat requests, 
including determining if a request is trivial, 
generating titles using an LLM, and obtaining model responses. 

It interacts with the conversation database and external model APIs to 
provide a seamless chat experience.
"""
class ChatRequest:
    def __init__(self, message: str, conversation_id: int | None, settings: Settings):
        self.message = message
        self.conversation_id = conversation_id
        self.settings = settings

    def is_trivial_request(self) -> bool:
        # Delegate to the reusable trivial-text helper so the logic is single-sourced.
        return self._is_trivial_text(self.message)

    def _normalize_text(self, text: str) -> str:
        """Normalize text for triviality checks: lower-case, remove punctuation, collapse spaces."""
        raw = (text or "").strip().lower()
        compact = re.sub(r"[^a-z0-9\s]", " ", raw)
        return re.sub(r"\s+", " ", compact).strip()

    def _is_trivial_text(self, text: str) -> bool:
        """Return True for short/boilerplate greetings that shouldn't generate titles."""
        normalized = self._normalize_text(text)
        if not normalized:
            return True
        if normalized in {"hi", "hello", "hey", "thanks", "ok", "okay"}:
            return True
        if normalized in {"hi there", "hello there", "how are you"}:
            return True
        return False

    def _parse_model_response(self, data) -> str | None:
        """Extract assistant text from common API response shapes.

        Returns the assistant content string or None when not found.
        """
        # Dict response shapes
        if isinstance(data, dict):
            # {"message": {"content": "..."}} or {"message": "..."}
            msg = data.get("message")
            if isinstance(msg, dict):
                return msg.get("content") or msg.get("text")
            if isinstance(msg, str):
                return msg

            # Choices-style: {"choices": [{"message": {"content": "..."}}]}
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    cmsg = first.get("message") or first
                    if isinstance(cmsg, dict):
                        return cmsg.get("content") or cmsg.get("text")
                    return first.get("text")

        # List of objects
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                msg = first.get("message") or first.get("content") or first.get("text")
                if isinstance(msg, dict):
                    return msg.get("content") or msg.get("text")
                if isinstance(msg, str):
                    return msg

        # If it's a plain string, return it (may be raw text)
        if isinstance(data, str):
            # Try to parse as JSON that contains message
            try:
                parsed = json.loads(data)
            except Exception:
                return data
            return self._parse_model_response(parsed)

        return None

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

                # Call post() and handle both awaitable and non-awaitable returns
                post_ret = client.post(
                    f"{self.settings.MODEL_API_URL}/api/chat",
                    json=payload,
                    timeout=60.0,
                )
                if inspect.isawaitable(post_ret):
                    response = await post_ret
                else:
                    response = post_ret

                # If we got a raw dict (some test helpers return dicts), use it directly.
                if isinstance(response, dict):
                    data = response
                else:
                    try:
                        json_ret = response.json()
                        data = await json_ret if inspect.isawaitable(json_ret) else json_ret
                    except Exception:
                        # Fallback: try reading text then parse
                        raw_text = response.text() if not inspect.isawaitable(response.text()) else await response.text()
                        try:
                            data = json.loads(raw_text)
                        except Exception:
                            data = raw_text
                # Parse the model response using the shared parser helper.
                output = self._parse_model_response(data)
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
            # Defer title generation until we see the first meaningful user message.
            title = None
        else:
            title = cd.get_conversation_title(self.conversation_id)

        message_count = cd.getMessagesCount(self.conversation_id)
        if message_count > self.settings.MESSAGE_THRESHOLD:
            summary = SummaryRequest(conversation_id=self.conversation_id, settings=self.settings).get_message_summary()
        # Simple flow: if there's no stored title, check if the current message is trivial.
        # If it's non-trivial, generate a title and persist it.
        logger.info(f"Current title: {title}")
        if title is None:
            is_trivial = self.is_trivial_request()
            logger.info(f"Is trivial request: {is_trivial}")
            if not is_trivial:
                try:
                    gen_title = await self.generate_title()
                    if gen_title:
                        cd.update_conversation_title(self.conversation_id, gen_title)
                        title = gen_title
                        logger.info(f"Generated title for conversation {self.conversation_id}: {title}")
                except Exception as exc:
                    logger.warning(f"Title generation failed for conversation {self.conversation_id}: {exc}")
            else:
                logger.debug(f"Skipping title generation for conversation {self.conversation_id}: trivial message")

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
            
    
