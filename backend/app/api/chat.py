from asyncio.log import logger

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.services.chatservice import ChatRequest
import app.db.conversationdao as conversationdao
from uuid import uuid4

router = APIRouter()


class MessageSchema(BaseModel):
    message: str
    conversation_id: int | None = None
    title: str | None = None
    titleGenerated : bool | None = False

@router.get("/history/{conversation_id}")
async def get_chat_history(conversation_id: int, settings: Settings = Depends(get_settings)):
    logger.info(f"Loading conversation history for conversation_id: {conversation_id}")
    history = conversationdao.get_conversation_history(conversation_id)

    messages = []
    for role, content in history:
        messages.append({
            "id": f"history-{conversation_id}-{len(messages)}-{uuid4()}",
            "conversation_id": conversation_id,
            "text": content,
            "sender": "user" if role == "user" else "ai",
        })

    return {
        "conversation_id": conversation_id,
        "messages": messages,
    }

@router.post("/message")
async def get_chat(
        payload: MessageSchema, 
        settings: Settings = Depends(get_settings)
    ):
    logger.info(f"Received message: {payload.message} with conversation_id: {payload.conversation_id}")
    chat_request = ChatRequest(message=payload.message, conversation_id=payload.conversation_id, settings=settings)
    return await chat_request.getModelResponse()