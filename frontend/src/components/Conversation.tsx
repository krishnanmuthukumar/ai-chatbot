import { useEffect, useRef } from "react";
import type { Message } from "./types";

function Conversation({ items }: { items: Message[] }) {
    const latestMsgRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        latestMsgRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [items]);

    return (
        <div className="w-full h-60 overflow-y-auto p-3 flex flex-col gap-2">
            {items.map((item) => {
                const isUser = item.sender === 'user';
                return (
                    <div key={item.id} className={`flex flex-col  max-w-[85%] ${isUser ? 'items-end ml-auto' : 'items-start'}`}>
                        <div className={`text-sm p-3 rounded-lg my-1 ${isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
                            {item.text}
                        </div>
                    </div>
                );
            })}
            <div ref={latestMsgRef} />
        </div>
    );
}

export default Conversation;