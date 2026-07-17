from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.chatservice import ChatRequest

router = APIRouter()

class MessageSchema(BaseModel):
    message: str

@router.post("/message")
async def get_chat(payload: MessageSchema, chat_request: "ChatRequest" = Depends(ChatRequest)):
    return await chat_request.getModelResponse()