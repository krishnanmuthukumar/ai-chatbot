import chaticon from "../assets/chat-icon.png";

function Header() {
    return (
         <div className="bg-sky-700 h-10 flex items-center">
            <div className="flex items-center gap-2 text-xl font-bold text-white px-2">
                <img className="w-6 h-6" src={chaticon} />
                <a href="#">
                    AI Chatbot
                </a>
            </div>
        </div>
    )
}

export default Header;