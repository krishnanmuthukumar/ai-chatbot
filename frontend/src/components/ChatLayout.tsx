import Header from "./Header";
import Footer from "./Footer";
import Conversation from "./Conversation";
import { useState } from "react";
import type { Message, RecentChat } from "./types";
import { sendMessageAPI, getConversationHistoryAPI, uploadDocumentAPI } from "../services/api";
import { useEffect } from "react";
import Sidebar from "./Sidebar";

const ChatLayout = () => {

    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [conversation_id, setConversationId] = useState<string | null>(
        () => localStorage.getItem('conversation_id')
    );
    const [recentChats, setRecentChats] = useState<RecentChat[]>(() => {
        const stored = localStorage.getItem('recentChats');
        if (!stored) {
            return [];
        }

        try {
            return JSON.parse(stored) as RecentChat[];
        } catch (error) {
            console.error('Unable to parse recent chats from localStorage', error);
            return [];
        }
    });

    useEffect(() => {
        localStorage.removeItem("conversation_id");
    }, []);

    const handleConversationIdChange = (id: string | null) => {
        if (id !== null) {
            localStorage.setItem('conversation_id', id);
            setConversationId(id);
        }
    };

    const addRecentChat = (chatId: string | null, title?: string | null) => {
        if (!chatId || !title || !title.trim()) {
            return;
        }

        const titleSource = title.trim();
        const shortTitle = titleSource.length > 44 ? `${titleSource.slice(0, 44)}...` : titleSource;

        setRecentChats((current) => {
            const updated = [
                { id: chatId, title: shortTitle, updatedAt: Date.now() },
                ...current.filter((chat) => chat.id !== chatId)
            ];

            localStorage.setItem('recentChats', JSON.stringify(updated.slice(0, 10)));
            return updated.slice(0, 10);
        });
    };

    const restoreConversation = async (chatId: string) => {
        const conversationMessages = await getConversationHistoryAPI(chatId);

        if (conversationMessages.length > 0) {
            setMessages(conversationMessages);
            setConversationId(chatId);
            localStorage.setItem('conversation_id', chatId);
        } else {
            setMessages([]);
        }

        setIsLoading(false);
    };

    const startNewChat = () => {
        if (conversation_id) {
            const existingTitle = recentChats.find((chat) => chat.id === conversation_id)?.title;
            addRecentChat(conversation_id, existingTitle);
        }

        setMessages([]);
        setIsLoading(false);
        setConversationId(null);
        localStorage.removeItem('conversation_id');
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
                handleConversationIdChange(initialResponse.conversation_id);
                setMessages(prevMessages => [...prevMessages, initialResponse]);
                addRecentChat(initialResponse.conversation_id, initialResponse.title);
                setIsLoading(false);
                return;
            } else {
                const aiResponse = await sendMessageAPI(newMessage);
                setMessages(prevMessages => [...prevMessages, aiResponse]);
                addRecentChat(aiResponse.conversation_id, aiResponse.title);
                setIsLoading(false);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }


    };

    const uploadDocument = async (file: File) => {
        const uploaded = await uploadDocumentAPI(file);

        if (!uploaded) {
            throw new Error('Document upload failed');
        }
    };


    return (
        <div className="flex justify-center h-screen bg-slate-100">
            <div className={`grid ${isSidebarOpen ? 'grid-cols-[340px_minmax(420px,1fr)]' : 'grid-cols-[48px_minmax(420px,1fr)]'} items-stretch h-screen transition-all duration-300`}>
                <aside className="overflow-hidden min-h-0 h-full border border-slate-300 bg-white shadow-sm">
                    <Sidebar
                        recentChats={recentChats}
                        onNewChat={startNewChat}
                        onSelectRecent={restoreConversation}
                        isSidebarOpen={isSidebarOpen}
                        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
                    />
                </aside>
                <section className="flex flex-col gap-4 min-w-0 h-full border border-slate-300 bg-white shadow-sm">
                    <Header />
                    <main className="flex-1 min-h-0">
                        <Conversation items={messages} isLoading={isLoading} />
                    </main>
                    <Footer onSend={sendMessage} onUploadDocument={uploadDocument} isUploadEnabled={false} />
                </section>
            </div>
        </div>
    )
}

export default ChatLayout;