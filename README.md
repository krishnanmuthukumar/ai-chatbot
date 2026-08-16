# AI Chatbot

A modern full-stack conversational AI application that combines a React frontend, a FastAPI backend, and a local language model served through Ollama.

## Overview

This project delivers a browser-based chatbot flow where users send natural-language prompts, continue existing conversations, and work with a history panel of recent chats.

The application is organized around a simple but practical runtime model:

- the frontend owns the live UI and request state
- the API layer receives chat payloads and conversation restore requests
- the backend inserts user and assistant messages into SQLite, builds model context, and returns a streamed model answer
- a conversation title can be generated only for a new, meaningful request and is returned to the UI as part of the API response

## Current Behavior and Features

- React + Vite chat UI with a responsive two-pane layout
- A sidebar that presents recent conversations and allows a user to open a prior chat
- A new chat action that clears the active in-memory message list and resets the current conversation id
- Conversation restoration through `GET /api/chat/history/{conversation_id}` so the UI can continue a selected chat from the stored backend history
- Request/response handling through `POST /api/chat/message`
- PDF upload from the chat footer using a file picker and multipart form submission
- Strict PDF-only validation on the backend, including file type, signature header, and PyMuPDF parsing checks
- Conversation-aware history retrieval and message persistence through SQLite
- A meaningful-request title gate: the backend checks whether a first prompt is trivial before asking the title LLM for a conversation title
- Optional title generation that never blocks the main assistant response path if title generation fails
- Recents are refreshed using the title returned by the API response payload rather than the prompt text

## API Contract Highlights

### Send a message

```text
POST /api/chat/message
```

Request body:

```json
{
  "message": "Explain the architecture briefly",
  "conversation_id": 12
}
```

The backend creates a conversation when the request does not carry one, stores the user message, asks the model for a response, and returns a payload like:

```json
{
  "response": "The architecture is ...",
  "conversation_id": 12,
  "title": "Explain the architecture"
}
```

Notes:

- `title` is a conversation title attached to the first answer for a new conversation.
- The title is only generated when the user prompt passes the trivial-message classifier.
- If the title pipeline fails, the assistant answer still returns normally.

### Load a stored conversation

```text
GET /api/chat/history/{conversation_id}
```

This endpoint returns a history payload containing the conversation id and role-based message objects that the frontend can use to repopulate the chat window.

### Upload a document

```text
POST /api/documents
```

Request: Multipart form data with a single file field

```
Content-Type: multipart/form-data
file: <binary file data>
```

Response:

```json
{
  "document_id": "abc123def456..."
}
```

Notes:

- Accepts only PDF uploads from the client and server-side validation
- Uploaded files must match the expected PDF header and open successfully in PyMuPDF
- File extension is preserved in the stored filename
- Document ID is generated using SHA256 hash of file contents
- The backend enforces a maximum file size configured through `MAX_FILE_SIZE`

## Technology Stack

- Frontend: React, TypeScript, Vite
- Backend: Python, FastAPI
- AI Runtime: Ollama
- Model: Phi-4 Mini
- Database: SQLite
- Document Validation: PyMuPDF
- Document Storage: Local filesystem
- Containerization: Docker Compose

## Environment Configuration

The backend requires the following environment variables in a `.env` file:

```env
MODEL_API_URL=http://localhost:11434
MODEL_NAME=phi4-mini:latest
MESSAGE_THRESHOLD=5
DOCUMENT_STORAGE_TYPE=local
DOCUMENT_STORAGE_PATH=./storage/documents
ALLOWED_CONTENT_TYPE=application/pdf
MAX_FILE_SIZE=20971520
```

- `MODEL_API_URL`: The URL of the Ollama API server
- `MODEL_NAME`: The model identifier to use (e.g., phi, mistral, llama2)
- `MESSAGE_THRESHOLD`: Number of messages before triggering certain backend actions
- `DOCUMENT_STORAGE_TYPE`: Storage backend type (currently supports "local")
- `DOCUMENT_STORAGE_PATH`: Local directory path for storing uploaded documents
- `ALLOWED_CONTENT_TYPE`: Restricts uploaded documents to PDF content type
- `MAX_FILE_SIZE`: Maximum accepted PDF size in bytes (default: 20 MB)

## Architecture

The application follows a simple three-layer structure:

1. Frontend
   - Handles user input and displays chatbot responses
   - Stores recents in local storage and calls the restore history API for selected chats
   - Provides a PDF upload button in the chat footer for document ingestion
2. Backend
   - Exposes REST APIs and coordinates chat requests
   - Validates uploaded PDFs before storing them locally
   - Persists conversation / message records in SQLite
3. AI Layer
   - Runs the language model locally using Ollama

## Project Structure

```text
ai-chatbot/
├── backend/        # FastAPI application
│   ├── app/        # Application code
│   └── storage/    # Document storage 
├── frontend/       # React + Vite frontend
├── docker/         # Docker setup for local model serving
└── README.md       # Project overview
```

Note: The `backend/storage/` directory is ignored in `.gitignore` to prevent storing user-uploaded documents in version control.

## Quick Start

### 1. Start the local Ollama service

```bash
cd docker/ollama
docker compose up -d
```

This starts the Ollama container and prepares the local model runtime.

### 2. Start the backend

```bash
cd backend
uv run fastapi dev
```

The backend will be available at:

- http://localhost:8000

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:

- http://localhost:5173

## Development Notes

- The frontend stores `conversation_id` in local storage and reuses it for subsequent chat requests.
- Recent chats are kept as a browser-side list of titles and IDs and are restored through the history API.
- Conversation titles are read from the backend response where available and pushed into the recent-chat list instead of trying to infer them from the client-side request text.
- The backend is built using FastAPI for low-latency API responses.
- Ollama provides a lightweight local deployment path for running the AI model without external cloud dependencies.

## Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## License

This project is currently maintained for development and demonstration purposes.

