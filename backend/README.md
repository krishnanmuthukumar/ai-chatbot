# Backend Overview

This backend provides the API layer for the AI chatbot application. It is built with FastAPI and is responsible for receiving chat requests, creating or reusing conversation context, persisting messages in SQLite, and forwarding prompts to the local Ollama-backed language model.

## What the backend does

The current backend implementation includes:

- a FastAPI application with CORS enabled for frontend communication
- a chat router that accepts messages from the frontend
- conversation creation and message persistence in SQLite
- streaming model requests to the configured local AI endpoint
- settings management via environment variables for model URL and model name

## Main request flow

1. The frontend sends a message to `POST /api/chat/message`.
2. The backend validates the incoming payload.
3. If no conversation ID is provided, the backend creates a new conversation row.
4. The user message is inserted into the `messages` table.
5. The backend sends the request to the Ollama model endpoint.
6. The streamed AI response is collected and stored back in the database.
7. The final response is returned to the frontend.

## Key backend files

- `app/main.py` — application startup, middleware setup, and router registration
- `app/api/chat.py` — chat endpoint definition and request handling
- `app/services/chatservice.py` — conversation logic and model streaming integration
- `app/config.py` — environment-based settings for model connection details
- `app/db/database.py` — SQLite initialization and connection management

## Configuration

The backend expects the following environment variables in a `.env` file:

```env
MODEL_API_URL=http://localhost:11434
MODEL_NAME=phi4-mini
```

## Development commands

```bash
cd backend
uv run fastapi dev
```

The API will be available at:

- http://localhost:8000

## Notes

This backend is not a generic FastAPI starter. It is a purpose-built API for an AI chat workflow, with conversation state management and local model integration wired into the request path.
