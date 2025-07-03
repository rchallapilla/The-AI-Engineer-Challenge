'use client';

import { useState, useRef } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface UploadedPDF {
  filename: string;
  status: string;
}

export default function PDFChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedPDFs, setUploadedPDFs] = useState<UploadedPDF[]>([]);
  const [selectedPDF, setSelectedPDF] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please select a PDF file.');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/upload_pdf`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload PDF');
      }

      const result = await response.json();
      setUploadedPDFs(prev => [...prev, {
        filename: result.filename,
        status: result.status
      }]);
      setSelectedPDF(result.filename);
      
      // Add success message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `✅ PDF "${result.filename}" uploaded and indexed successfully! You can now ask questions about this document.`,
        timestamp: new Date()
      }]);

    } catch (error) {
      console.error('Upload error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ Error uploading PDF: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      }]);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !selectedPDF) return;

    const userMessage: Message = { 
      role: 'user', 
      content: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/pdf_chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: input,
          pdf_filename: selectedPDF,
          model: "gpt-4o-mini"
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get response');
      }

      const result = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: result.answer,
        timestamp: new Date()
      }]);

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `❌ Error: ${error instanceof Error ? error.message : 'Failed to connect to the backend'}`,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-purple-900 to-slate-900 text-white">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-amber-400 via-purple-400 to-cyan-400">
            PDF RAG Chat System
          </h1>
          <p className="text-purple-200 mt-2">Upload a PDF and chat with it using AI-powered retrieval</p>
        </header>

        {/* PDF Upload Section */}
        <div className="bg-black/40 backdrop-blur-lg rounded-lg p-6 mb-6 border border-purple-500/30">
          <h2 className="text-xl font-semibold mb-4 text-purple-300">Upload PDF</h2>
          
          <div className="flex items-center gap-4 mb-4">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
              id="pdf-upload"
            />
            <label
              htmlFor="pdf-upload"
              className="px-6 py-3 bg-gradient-to-r from-amber-600 to-purple-600 rounded-lg font-semibold hover:from-amber-700 hover:to-purple-700 transition-all cursor-pointer border border-purple-500/30"
            >
              {isUploading ? 'Uploading...' : 'Choose PDF File'}
            </label>
            {isUploading && (
              <div className="text-purple-300 animate-pulse">Processing PDF...</div>
            )}
          </div>

          {/* Uploaded PDFs List */}
          {uploadedPDFs.length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold mb-2 text-purple-300">Uploaded PDFs:</h3>
              <div className="space-y-2">
                {uploadedPDFs.map((pdf, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      selectedPDF === pdf.filename
                        ? 'bg-purple-600/80 border-purple-400'
                        : 'bg-black/20 border-purple-500/30 hover:bg-purple-600/40'
                    }`}
                    onClick={() => setSelectedPDF(pdf.filename)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{pdf.filename}</span>
                      <span className={`text-sm px-2 py-1 rounded ${
                        pdf.status === 'indexed' 
                          ? 'bg-green-600/80 text-green-100' 
                          : 'bg-yellow-600/80 text-yellow-100'
                      }`}>
                        {pdf.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Chat Section */}
        <div className="bg-black/40 backdrop-blur-lg rounded-lg p-6 mb-6 h-[50vh] overflow-y-auto border border-purple-500/30">
          {messages.length === 0 ? (
            <div className="text-center text-purple-300 mt-8">
              <p>Upload a PDF and start asking questions!</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`mb-4 ${
                  message.role === 'user' ? 'text-right' : 'text-left'
                }`}
              >
                <div
                  className={`inline-block p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-amber-600/80 ml-auto'
                      : 'bg-purple-600/80'
                  } max-w-[80%] border border-purple-500/30`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm opacity-75">
                      {message.role === 'user' ? 'You' : 'AI Assistant'}
                    </p>
                    <p className="text-xs opacity-50">{formatTime(message.timestamp)}</p>
                  </div>
                  <div className="leading-relaxed whitespace-pre-wrap">{message.content}</div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="text-center text-purple-300">
              <div className="inline-block animate-pulse">Searching through PDF and generating response...</div>
            </div>
          )}
        </div>

        {/* Chat Input */}
        <form onSubmit={handleSubmit} className="flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={selectedPDF ? `Ask a question about "${selectedPDF}"...` : "Upload a PDF first to start chatting..."}
            disabled={!selectedPDF}
            className="flex-1 p-4 rounded-lg bg-black/40 backdrop-blur-lg text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 border border-purple-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isLoading || !selectedPDF || !input.trim()}
            className="px-6 py-4 bg-gradient-to-r from-amber-600 to-purple-600 rounded-lg font-semibold hover:from-amber-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed border border-purple-500/30"
          >
            {isLoading ? 'Sending...' : 'Ask'}
          </button>
        </form>

        {/* Navigation */}
        <div className="mt-8 text-center">
          <a
            href="/"
            className="text-purple-300 hover:text-purple-100 transition-colors underline"
          >
            ← Back to Asimov-Vedanta Chat
          </a>
        </div>
      </div>
    </div>
  );
} 