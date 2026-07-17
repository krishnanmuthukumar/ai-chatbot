from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.services.chatservice import ChatRequest

router = APIRouter()


class MessageSchema(BaseModel):
    message: str


def get_chat_request(payload: MessageSchema, settings: Settings = Depends(get_settings)) -> ChatRequest:
    return ChatRequest(message=payload.message, settings=settings)


@router.post("/message")
async def get_chat(payload: MessageSchema, chat_request: ChatRequest = Depends(get_chat_request)):
    return await chat_request.getModelResponse()