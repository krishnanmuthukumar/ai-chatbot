import { useState } from "react";

function Footer({ onSend }: { onSend: (message: string) => void }) {
    const [input, setInput] = useState('');

    const handleKeyDown = (event: any) => {
        if (event.key === 'Enter') {
            if (input.trim() === '') return; // Prevent sending empty messages
            onSend(input);
            setInput('');
        }
    };

    return (
        <div className="p-2">
            <input
                className="block bg-white w-full border border-slate-300 rounded-md placeholder:italic placeholder:text-slate-400 p-2"
                placeholder="ask anything" type="text" name="input" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}
            ></input>
        </div>
    );
}

export default Footer;