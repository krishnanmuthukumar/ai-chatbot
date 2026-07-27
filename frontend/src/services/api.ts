import type { Message } from "../components/types";

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

        return {
            id: crypto.randomUUID(),
            conversation_id: newConversationId, // Store the conversation ID from the response
            text: responseText, // Use the actual AI response
            sender: 'ai',
        }
    } catch (error) {
        console.error('Error sending message:', error);
        return {
            id : crypto.randomUUID(),
            conversation_id : null,
            text: "Failed to connect to the server. Please try again.",
            sender: 'ai',
        };
    }
};