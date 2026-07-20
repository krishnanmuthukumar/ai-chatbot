from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.services.chatservice import ChatRequest

router = APIRouter()


class MessageSchema(BaseModel):
    message: str

@router.post("/message")
async def get_chat(
        payload: MessageSchema, 
        settings: Settings = Depends(get_settings)
    ):
    chat_request = ChatRequest(message=payload.message, settings=settings)
    return await chat_request.getModelResponse()