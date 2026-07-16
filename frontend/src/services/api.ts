import type { Message } from "../components/types";

export const sendMessageAPI = (input: string): Message => {
    return {
        id: crypto.randomUUID(), // Generates a safe, unique string ID
        text: `response from server ${input}`, // Placeholder for actual AI response logic
        sender: 'ai',
    };
};