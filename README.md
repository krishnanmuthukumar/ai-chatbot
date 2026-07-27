# AI Chatbot

A modern full-stack conversational AI application that combines a React frontend, a FastAPI backend, and a local language model served through Ollama.

## Overview

This project delivers a simple but scalable chatbot experience where users can send natural-language prompts through a responsive web interface, and the backend forwards those requests to a local AI model for inference.

The solution is designed to demonstrate a practical end-to-end architecture for:

- interactive frontend conversations
- API-driven backend orchestration
- local model hosting with Ollama
- modular service-based application structure

## Features

- Clean and responsive user interface built with React + Vite
- Fast API endpoints for chat interactions
- Conversation-aware request handling with persisted session state
- Historical messages retrieved by `conversation_id` and sent to the LLM with role context
- Local AI inference using the Phi-4 Mini model
- Containerized Ollama setup for easy model serving

## Technology Stack

- Frontend: React, TypeScript, Vite
- Backend: Python, FastAPI
- AI Runtime: Ollama
- Model: Phi-4 Mini
- Containerization: Docker Compose

## Architecture

The application follows a simple three-layer structure:

1. Frontend
   - Handles user input and displays chatbot responses
2. Backend
   - Exposes REST APIs and coordinates chat requests
3. AI Layer
   - Runs the language model locally using Ollama

## Project Structure

```text
ai-chatbot/
├── backend/        # FastAPI application
├── frontend/       # React + Vite frontend
├── docker/         # Docker setup for local model serving
└── README.md       # Project overview
```

## Quick Start

### 1. Start the local Ollama service

```bash
cd docker/ollama
docker compose up -d
```

This starts the Ollama container and pulls the Phi-4 Mini model for local inference.

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

## API Endpoint

The backend includes a chat route for sending user messages:

```text
POST /api/chat/message
```

The endpoint accepts a JSON body containing `message` and an optional `conversation_id`. If no `conversation_id` is provided, the backend creates a new conversation and returns a structured JSON response with `text` and `conversation_id`.

Example response:

```json
{
  "text": "AI response text",
  "conversation_id": 1
}
```

## Development Notes

- The frontend stores `conversation_id` in local storage and reuses it for subsequent chat requests.
- The frontend is configured for modern React development with Vite.
- The backend is built using FastAPI for low-latency API responses.
- Ollama provides a lightweight local deployment path for running the AI model without external cloud dependencies.

## Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## License

This project is currently maintained for development and demonstration purposes.

