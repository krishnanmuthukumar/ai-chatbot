import type { RecentChat } from "./types";

function Sidebar({ recentChats, onNewChat, onSelectRecent, isSidebarOpen, onToggleSidebar }: { recentChats: RecentChat[]; onNewChat: () => void; onSelectRecent: (chatId: string) => void; isSidebarOpen: boolean; onToggleSidebar: () => void }) {

    return (
        <div className="h-full bg-white text-slate-800">
            <header className="bg-sky-700 h-10 flex items-center justify-between shrink-0 px-2 gap-3">
                <div className="flex items-center gap-2 text-xl font-bold text-white">
                    <img className="w-6 h-6 cursor-pointer" src="/src/assets/chat-icon.png" alt="" onClick={onToggleSidebar} />
                    <a id="left-panel-title" href="#" className={isSidebarOpen ? "" : "hidden"}>
                        Chat Bot
                    </a>
                </div>
            </header>

            {isSidebarOpen && (
                <div id="new-chat-row" className="p-2 flex flex-col gap-2">
                    <button
                        className="flex items-center gap-2 px-2 py-2 hover:bg-sky-50 border border-slate-200 text-left w-full"
                        onClick={onNewChat}
                    >
                        <img className="w-6 h-6" src="/src/assets/new-chat.png" alt="" />
                        <span className="text-sm text-slate-700">New Chat</span>
                    </button>

                    <div className="flex items-center gap-2 px-2 py-2 hover:bg-sky-50 border border-slate-200">
                        <span className="text-sm text-slate-700">Recent Chat</span>
                    </div>

                    <div className="mt-3 space-y-2">
                        {recentChats.length === 0 && (
                            <div className="rounded p-2 text-sm text-slate-500">No recent chats</div>
                        )}
                        {recentChats.map((chat) => (
                            <button key={chat.id} className="rounded p-2 text-sm border border-slate-200 bg-slate-50 truncate w-full text-left hover:bg-sky-50" onClick={() => onSelectRecent(chat.id)}>
                                {chat.title}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default Sidebar;