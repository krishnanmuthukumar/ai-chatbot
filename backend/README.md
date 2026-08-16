# Backend Overview

This backend provides the API layer for the AI chatbot application. It is built with FastAPI and is responsible for receiving chat requests, creating or reusing conversation context, persisting messages in SQLite, and forwarding prompts to the local Ollama-backed language model.

## What the backend does

The current backend implementation includes:

- a FastAPI application with CORS enabled for frontend communication
- a chat router that accepts messages from the frontend
- conversation creation and message persistence in SQLite
- conversation history lookup through `GET /api/chat/history/{conversation_id}`
- retrieval of a saved conversation title from the conversation row when a conversation is continued
- a meaningful-request title pipeline for newly created conversations
- summarization of older conversation history when the configured message threshold is reached, then sending the summary plus the latest user prompt to the model
- streaming model requests to the configured local AI endpoint
- returning a structured JSON response with `response`, `conversation_id`, and an optional `title`
- document upload endpoint for storing files with multipart form-data support
- strict PDF-only validation before storage, including content type checks, PDF signature verification, and PyMuPDF parsing validation
- max-file-size enforcement using configuration-based validation
- document persistence with SHA256-based ID generation and file extension preservation
- settings management via environment variables for model URL, model name, message threshold, document storage configuration, and PDF validation limits

## Main request flow

1. The frontend sends a message to `POST /api/chat/message`.
2. The backend validates the incoming payload.
3. If no `conversation_id` is provided, the backend creates a new conversation row.
4. The new chat request is checked against the title prefilter. If the prompt is considered trivial, the backend does not try to call the title-generation LLM.
5. For a meaningful, first-time request, the backend asks the title-generation LLM for a compact title and persists it.
6. The user message is inserted into the `messages` table.
7. The backend loads all existing messages for the target `conversation_id` and checks the configured threshold.
8. If the threshold is exceeded, older history is summarized and the model request includes that summary plus the latest user prompt.
9. Otherwise, the full history is sent to the model.
10. The backend sends the request to the Ollama model endpoint.
11. The streamed AI response is collected and stored back in the database.
12. The final response is returned to the frontend as JSON with `response`, `conversation_id`, and `title` when one is available.
13. The frontend saves the returned `conversation_id` and updates its recent-chat list using the `title` value from the response.

## Title generation details

The current service layer supports a title-only pipeline that is intentionally non-blocking:

- `ChatRequest.is_trivial_request()` prefilters the first user prompt.
- `generate_title()` consults the trivial-request classifier and returns `None` for conversationally empty or short greeting-like input.
- `generate_title_with_llm()` performs the local Ollama chat call that asks for a short title.
- `getModelResponse()` stores the returned title on the conversation when the conversation is newly created.
- A title-generation exception is caught and logged as a warning, but it does not poison the main assistant answer.

## Document upload flow

The document upload feature follows a layered architecture:

1. The frontend sends a multipart file upload to `POST /api/documents`.
2. The endpoint calls `validate_pdf(file)` before any storage logic is executed.
3. The validator checks the file content type, enforces the configured max size, confirms the `%PDF-` signature is present, and opens the file with PyMuPDF to confirm it is a valid PDF.
4. The endpoint uses dependency injection to obtain the `DocumentService` instance via `get_document_service()`.
5. `get_document_service()` returns a service configured with storage initialized through `get_document_storage()`.
6. `get_document_storage()` reads the `DOCUMENT_STORAGE_TYPE` setting and instantiates the appropriate storage backend (currently only `LocalDocStorage`).
7. `DocumentService.upload_document()` reads the multipart file, generates a SHA256-based ID, preserves the file extension, and calls `storage.save()`.
8. The storage implementation persists the file to disk at `{DOCUMENT_STORAGE_PATH}/{document_id_with_extension}`.
9. The generated document ID (with file extension) is returned to the frontend as JSON.

## API surface

### POST /api/chat/message

This is the primary chat endpoint. The payload is a Pydantic schema with a required `message` field and an optional `conversation_id`.

Example response:

```json
{
  "response": "AI response text",
  "conversation_id": 1,
  "title": "How to explain the workflow"
}
```

### GET /api/chat/history/{conversation_id}

This reads historical role/message rows for a stored conversation and returns them in a frontend-friendly shape.

### POST /api/documents

This endpoint accepts a multipart file upload and stores the document locally.

Request: Multipart form data with a single `file` field

Example response:

```json
{
  "document_id": "abc123def456..."
}
```

Notes:
- Only PDF files are accepted
- The backend validates both the MIME value and the PDF file signature before storing
- Files must open successfully in PyMuPDF or the upload is rejected
- File extension is preserved in the stored document ID
- Document ID is generated using SHA256 hash of file contents
- Maximum upload size is enforced via `MAX_FILE_SIZE`

## Key backend files

- `app/main.py` — application startup, middleware setup, and router registration
- `app/api/chat.py` — chat endpoint definition and request handling
- `app/api/document_api.py` — document upload endpoint and file handling
- `app/services/chatservice.py` — conversation logic, title classification, title generation, and model streaming integration
- `app/services/summaryservice.py` — conversation-summary support for larger histories
- `app/services/documentservice.py` — document upload and ID generation logic
- `app/validation/pdf_validator.py` — PDF validation checks for MIME, size, header signature, and PyMuPDF readability
- `app/storage/document_storage.py` — abstract storage interface
- `app/storage/local_doc_storage.py` — local filesystem storage implementation
- `app/dependencies/document_dependencies.py` — dependency injection setup for document storage and service initialization
- `app/config.py` — environment-based settings for model, document storage, and PDF validation configuration
- `app/db/database.py` — SQLite initialization and connection management
- `app/db/conversationdao.py` — conversation title and message CRUD helpers

## Configuration

The backend expects the following environment variables in a `.env` file:

```env
MODEL_API_URL=http://localhost:11434
MODEL_NAME=phi4-mini:latest
MESSAGE_THRESHOLD=5
DOCUMENT_STORAGE_TYPE=local
DOCUMENT_STORAGE_PATH=./storage/documents
ALLOWED_CONTENT_TYPE=application/pdf
MAX_FILE_SIZE=20971520
```

- `MODEL_API_URL` — URL of the Ollama API server
- `MODEL_NAME` — Model identifier to use (e.g., phi, mistral, llama2)
- `MESSAGE_THRESHOLD` — Number of messages before triggering conversation summarization
- `DOCUMENT_STORAGE_TYPE` — Storage backend type (currently supports "local")
- `DOCUMENT_STORAGE_PATH` — Local directory for storing uploaded documents
- `ALLOWED_CONTENT_TYPE` — Restricts uploads to PDF content type
- `MAX_FILE_SIZE` — Maximum accepted document size, in bytes (default: 20 MB)

## Development commands

```bash
cd backend
uv run fastapi dev
```

The API will be available at:

- http://localhost:8000

## Notes

This backend is not a generic FastAPI starter. It is a purpose-built API for an AI chat workflow, with conversation state management, local model integration, title generation, history restore, and recent-chat support wired into the request path.
