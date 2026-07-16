import Header from "./Header";
import Footer from "./Footer";
import Conversation from "./Conversation";
import { useState } from "react";
import type { Message } from "./types";
import { sendMessageAPI } from "../services/api";

const ChatLayout = () => {

    const [messages, setMessages] = useState<Message[]>([]);

    const sendMessage = (message: string) => {
        const newMessage: Message = {
            id: crypto.randomUUID(), // Generates a safe, unique string ID
            text: message,
            sender: 'user',
        };
        setMessages(prevMessages => [...prevMessages, newMessage]);

        const aiResponse = sendMessageAPI(message);
        
        setMessages(prevMessages => [...prevMessages, aiResponse]);
    };


    return (
        <div className="flex justify-center h-screen bg-slate-100">
            <div className="w-96 h-96 border border-slate-300 rounded-md flex flex-col ">
                <Header />
                <main>
                    <Conversation items={messages} />
                </main>
                <Footer onSend={sendMessage} />
            </div>
        </div>
    )
}

export default ChatLayout;