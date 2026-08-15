from app.api import document_api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat
import logging
from contextlib import asynccontextmanager
from app.db.database import init_db, close_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database connection when the app starts
    init_db()
    yield
    # Close the database connection when the app shuts down
    close_db_connection()

app = FastAPI(title="AI Chatbot API", description="API for AI Chatbot", version="1.0.0", lifespan=lifespan)
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(document_api.router, prefix="/api/documents", tags=["documents"])

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    logging
    return {"message": "Chat API is running. Use the /chat endpoint to send messages."}
 