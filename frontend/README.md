# Frontend Overview

This frontend provides the user-facing chat experience for the AI chatbot application. It is built with React, TypeScript, and Vite, and is designed to send user prompts to the backend API, restore prior conversation state, and render the chatbot response inside a responsive conversation layout.

## Current Layout

The main shell is controlled by `ChatLayout`, which brings together the conversation experience and the left-hand navigation:

- a responsive two-column layout with a visible sidebar and main conversation column
- a collapsed layout mode that shrinks the sidebar to a narrow rail using CSS grid column switching
- a `Header` section at the top of the chat workspace
- a `Conversation` area that continuously renders the message list and the loading indicator
- a bottom `Footer` input area that accepts new prompts and sends them to the API layer

The `Sidebar` component provides the contextual navigation in the workspace:

- a top header area with the brand and collapse trigger
- a `New Chat` button which resets the UI state and drops the current conversation context
- a `Recent Chat` list read from the browser’s local storage
- click-through restore support for a historical conversation via the backend history endpoint

## What the frontend does

The current interface includes:

- a chat header with the application branding
- a conversation area for user and AI messages
- message bubbles with distinct styling for each sender
- a loading state while the backend is generating a response
- auto-scrolling to the latest message in the conversation
- a footer input area for sending new prompts
- a local recent-chat list that is refreshed after every successful first-response title payload
- backend history fetch and replay when the user selects one of the recent chats from the sidebar

## Main application flow

1. A user types a message in the input area.
2. The frontend appends the user message to the conversation.
3. The message is sent to the backend endpoint at `/api/chat/message` with `conversation_id` if one exists.
4. If no conversation ID exists, the backend creates a new conversation and returns `conversation_id`.
5. The frontend stores the backend `conversation_id` in local storage and reuses it for subsequent requests.
6. The backend returns the AI-generated response text and an optional title payload for a fresh conversation.
7. The frontend renders the assistant reply and updates the recent-chat list from the response payload when the title is available.
8. Selecting a recent chat calls the restore-history API and repopulates the conversation messages from the backend.

## Key frontend files

- `src/App.tsx` — application entrypoint
- `src/components/ChatLayout.tsx` — orchestrates layout state, message state, recents, new-chat reset, and API restore logic
- `src/components/Sidebar.tsx` — renders the recent-chat rail and new-chat control
- `src/components/Conversation.tsx` — renders the conversation list and loading indicator
- `src/components/Header.tsx` — top branding area
- `src/components/Footer.tsx` — input and send controls
- `src/services/api.ts` — API integration layer for chat requests and conversation history retrieval
- `src/components/types.ts` — shared frontend message and recent-chat interfaces

## Data flow and browser state

The selected chat context is synchronized through browser local storage:

- `conversation_id` keeps the currently active backend conversation id
- `recentChats` stores the list of recent chat titles and ids in the browser
- `restoreConversation()` loads the message payload from `GET /api/chat/history/{conversation_id}` and rehydrates the UI

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

This frontend is intentionally focused on a lightweight chat UI rather than a generic starter template. The current implementation is a practical conversational interface for an AI assistant, with a direct connection to the FastAPI backend, restore support for old conversations, and a title-driven recent-chat model that now follows the API response contract.
