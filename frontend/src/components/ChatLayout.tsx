import Header from "./Header";
import Footer from "./Footer";
import Conversation from "./Conversation";
import { useState } from "react";
import type { Message } from "./types";
import { sendMessageAPI } from "../services/api";

const ChatLayout = () => {

    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async (message: string) => {
        const newMessage: Message = {
            id: crypto.randomUUID(), // Generates a safe, unique string ID
            text: message,
            sender: 'user',
        };
        setMessages(prevMessages => [...prevMessages, newMessage]);

        setIsLoading(true);

        await new Promise((resolve) => setTimeout(resolve, 700));

        const aiResponse = await sendMessageAPI(message);
        setMessages(prevMessages => [...prevMessages, aiResponse]);
        setIsLoading(false);
    };


    return (
        <div className="flex justify-center h-screen bg-slate-100">
            <div className="w-96 h-96 border border-slate-300 rounded-md flex flex-col ">
                <Header />
                <main>
                    <Conversation items={messages} isLoading={isLoading} />
                </main>
                <Footer onSend={sendMessage} />
            </div>
        </div>
    )
}

export default ChatLayout;