import { useRef, useState } from "react";

function Footer({ onSend, onUploadDocument, isUploadEnabled = false }: { onSend: (message: string) => void; onUploadDocument: (file: File) => Promise<void>; isUploadEnabled?: boolean }) {
    const [input, setInput] = useState('');
    const [uploadMessage, setUploadMessage] = useState('');
    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const handleKeyDown = (event: any) => {
        if (event.key === 'Enter') {
            if (input.trim() === '') return; // Prevent sending empty messages
            onSend(input);
            setInput('');
        }
    };

    const handleUploadClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = event.target.files?.[0];
        if (!selectedFile) {
            return;
        }

        if (selectedFile.type !== 'application/pdf') {
            setUploadMessage('Please select a PDF file.');
            event.target.value = '';
            return;
        }

        setUploadMessage('Uploading PDF...');
        try {
            await onUploadDocument(selectedFile);
            setUploadMessage(`Uploaded: ${selectedFile.name}`);
        } catch (error) {
            setUploadMessage('Failed to upload PDF.');
            console.error(error);
        } finally {
            event.target.value = '';
        }
    };

    return (
        <div className="p-2">
            <div className="flex gap-2 items-center">
                {isUploadEnabled && (
                    <div className="relative flex-shrink-0">
                        <button
                            type="button"
                            onClick={handleUploadClick}
                            aria-label="Upload PDF"
                            title="Upload PDF"
                            className="flex h-10 w-10 items-center justify-center rounded-md border border-slate-300 bg-slate-100 text-xl font-medium text-slate-700 transition hover:bg-slate-200"
                        >
                            +
                        </button>
                        <span className="pointer-events-none absolute -top-2 left-1/2 -translate-x-1/2 -translate-y-full rounded bg-slate-800 px-2 py-1 text-[10px] font-medium text-white opacity-0 transition-opacity group-hover:opacity-100">
                            PDF only
                        </span>
                    </div>
                )}
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="application/pdf"
                    className="hidden"
                    onChange={handleFileChange}
                />
                <input
                    className="block bg-white w-full border border-slate-300 rounded-md placeholder:italic placeholder:text-slate-400 p-2"
                    placeholder="ask anything" type="text" name="input" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}
                ></input>
            </div>
            {isUploadEnabled && (
                uploadMessage ? (
                    <p className="mt-1 text-xs text-slate-600">{uploadMessage}</p>
                ) : (
                    <p className="mt-1 text-[10px] uppercase tracking-wide text-slate-400">PDF only</p>
                )
            )}
        </div>
    );
}

export default Footer;