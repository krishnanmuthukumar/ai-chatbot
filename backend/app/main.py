from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat

app = FastAPI(title="AI Chatbot API", description="API for AI Chatbot", version="1.0.0")
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

origins = [
    "http://localhost:3000",      # React default port
    "http://localhost:5173",      # Vite / Vue default port
    "http://127.0.0.1:5500",      # Live Server extension port
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chat API is running. Use the /chat endpoint to send messages."}
 