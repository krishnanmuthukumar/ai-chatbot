# Frontend Overview

This frontend provides the user-facing chat experience for the AI chatbot application. It is built with React, TypeScript, and Vite, and is designed to send user prompts to the backend API and display the chatbot response in a conversational layout.

## What the frontend does

The current interface includes:

- a chat header with the application branding
- a conversation area for user and AI messages
- message bubbles with distinct styling for each sender
- a loading state while the backend is generating a response
- auto-scrolling to the latest message in the conversation
- a footer input area for sending new prompts

## Main application flow

1. A user types a message in the input area.
2. The frontend appends the user message to the conversation.
3. The message is sent to the backend endpoint at `/api/chat/message` with `conversation_id` if one exists.
4. If no conversation ID exists, the backend creates a new conversation and returns `conversation_id`.
5. The frontend stores the backend `conversation_id` in local storage and reuses it for subsequent requests.
6. The backend returns the AI-generated response text.
7. The frontend renders the assistant reply and updates the chat view.

## Key frontend files

- `src/App.tsx` — application entrypoint
- `src/components/ChatLayout.tsx` — orchestrates message state and API calls
- `src/components/Conversation.tsx` — renders the conversation list and loading indicator
- `src/components/Header.tsx` — top branding area
- `src/components/Footer.tsx` — input and send controls
- `src/services/api.ts` — API integration layer for chat requests

## Development commands

```bash
npm install
npm run dev
```

To build the production bundle:

```bash
npm run build
```

## Notes

This frontend is intentionally focused on a lightweight chat UI rather than a generic starter template. The codebase reflects a practical conversational interface for an AI assistant, with a direct connection to the FastAPI backend.

