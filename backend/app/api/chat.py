from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class MessageSchema(BaseModel):
    message: str

@router.post("/message")
async def chat(payload: MessageSchema):
    return {"response": f"AI response to your message: {payload.message}"}