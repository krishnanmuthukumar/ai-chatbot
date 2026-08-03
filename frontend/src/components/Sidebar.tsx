import { useState } from "react";

function Sidebar() {

    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    return (
        <aside className="w-64 h-full bg-sky-700 text-white p-4">
            <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="w-full p-2 text-left text-sm font-semibold"
            >
                {isSidebarOpen ? "<<" : ">>"}
            </button>

            {isSidebarOpen && (
                <div className="p-3">
                    <div className="text-sm font-medium">Recent Chats</div>
                    <div className="mt-3 space-y-2">
                        <div className="rounded p-2 text-sm">Chat 1</div>
                        <div className="rounded p-2 text-sm">Chat 2</div>
                    </div>
                </div>
            )}
        </aside>
    );
}

export default Sidebar;