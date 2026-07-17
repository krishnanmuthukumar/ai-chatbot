import type { Message } from "../components/types";

export const sendMessageAPI = async (input: string): Promise<Message> => {
    try {
        const response = await fetch('http://localhost:8000/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: input }),
            signal: AbortSignal.timeout(180000)
        });

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();
        const responseText = typeof data === 'string' ? data : 'No response received.';

        return {
            id: crypto.randomUUID(), // Generates a safe, unique string ID
            text: responseText, // Use the actual AI response
            sender: 'ai',
        }
    } catch (error) {
        console.error('Error sending message:', error);
        return {
            id: crypto.randomUUID(),
            text: "Failed to connect to the server. Please try again.",
            sender: 'ai',
        };
    }
};