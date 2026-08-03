import Header from "./Header";
import Footer from "./Footer";
import Conversation from "./Conversation";
import { useState } from "react";
import type { Message } from "./types";
import { sendMessageAPI } from "../services/api";
import { useEffect } from "react";
import Sidebar from "./Sidebar";

const ChatLayout = () => {

    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [conversation_id, setConversationId] = useState<string | null>(
        () => localStorage.getItem('conversation_id')
    );

    useEffect(() => {
        localStorage.removeItem("conversation_id");
    }, []);

    const handleConversationIdChange = (id: string | null) => {
        if (id !== null) {
            localStorage.setItem('conversation_id', id);
            setConversationId(id);
        }
    };

    const sendMessage = async (message: string) => {
        const conversationId = conversation_id ?? localStorage.getItem("conversation_id")
        const newMessage: Message = {
            id: crypto.randomUUID(),
            conversation_id: conversationId,
            text: message,
            sender: 'user',
        };
        setMessages(prevMessages => [...prevMessages, newMessage]);

        setIsLoading(true);
        try {
            if (conversationId === null) {
                const initialResponse = await sendMessageAPI(newMessage);
                handleConversationIdChange(initialResponse.conversation_id); // Set the conversation ID from the initial response
                setMessages(prevMessages => [...prevMessages, initialResponse]);
                setIsLoading(false);
                return;
            } else {
                const aiResponse = await sendMessageAPI(newMessage);
                setMessages(prevMessages => [...prevMessages, aiResponse]);
                setIsLoading(false);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }


    };


    return (
        <div className="flex justify-center h-screen bg-slate-100">
            <div className="flex w-[700px] h-[500px] border border-slate-300 rounded-md">
                <Sidebar />
                <div className="flex flex-1 flex-col min-h-0">
                    <Header />
                    <main className="flex-1 min-h-0">
                        <Conversation items={messages} isLoading={isLoading} />
                    </main>
                    <Footer onSend={sendMessage} />
                </div>
            </div>
        </div>
    )
}

export default ChatLayout;