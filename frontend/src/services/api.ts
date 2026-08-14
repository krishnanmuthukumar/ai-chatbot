import type { Message } from "../components/types";

export interface HistoryResponse {
    conversation_id: number | string | null;
    messages: Message[];
}

export const getConversationHistoryAPI = async (conversationId: string | number): Promise<Message[]> => {
    try {
        const response = await fetch(`http://localhost:8000/api/chat/history/${conversationId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            signal: AbortSignal.timeout(180000)
        });

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();
        const loadedMessages = Array.isArray(data.messages) ? data.messages : [];

        return loadedMessages.map((item: any) => ({
            id: item.id ?? crypto.randomUUID(),
            conversation_id: item.conversation_id ?? conversationId,
            text: item.text ?? '',
            sender: item.sender === 'user' ? 'user' : 'ai',
        }));
    } catch (error) {
        console.error('Error loading conversation history:', error);
        return [];
    }
};

export const sendMessageAPI = async (input: Message): Promise<Message> => {
    try {
        console.log("input.text", input.text, "conversation_id", input.conversation_id)
        const response = await fetch('http://localhost:8000/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: input.text, conversation_id: input.conversation_id }),
            signal: AbortSignal.timeout(180000)
        });

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();
        const responseText = typeof data === 'object' && data !== null && 'response' in data ? data.response : 'No response received.';
        const newConversationId = typeof data === 'object' && data !== null && 'conversation_id' in data ? data.conversation_id : null;
        const title = typeof data === 'object' && data !== null && 'title' in data ? data.title : null;

        return {
            id: crypto.randomUUID(),
            conversation_id: newConversationId,
            text: responseText,
            sender: 'ai',
            title: title ?? null,
        }
    } catch (error) {
        console.error('Error sending message:', error);
        return {
            id : crypto.randomUUID(),
            conversation_id : null,
            text: "Failed to connect to the server. Please try again.",
            sender: 'ai',
            title: null,
        };
    }
};