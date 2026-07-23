from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.services.chatservice import ChatRequest

router = APIRouter()


class MessageSchema(BaseModel):
    message: str
    conversation_id: int | None = None

@router.post("/message")
async def get_chat(
        payload: MessageSchema, 
        settings: Settings = Depends(get_settings)
    ):
    chat_request = ChatRequest(message=payload.message, conversation_id=payload.conversation_id, settings=settings)
    return await chat_request.getModelResponse()