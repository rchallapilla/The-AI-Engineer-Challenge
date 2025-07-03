'use client';

import React, { useState, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Session {
  session_id: string;
  filename: string;
  chunks_count: number;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [uploading, setUploading] = useState(false);
  const [chatMode, setChatMode] = useState<'general' | 'rag'>('general');

  // Load sessions on component mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/rag/sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please select a PDF file');
      return;
    }

    setUploading(true);
    
    try {
      // Convert file to base64
      const reader = new FileReader();
      const filePromise = new Promise<string>((resolve, reject) => {
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = reject;
      });
      reader.readAsDataURL(file);
      
      const base64Data = await filePromise;
      const base64Content = base64Data.split(',')[1]; // Remove data URL prefix
      
      const response = await fetch('/api/rag/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file: base64Content,
          filename: file.name
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to upload PDF');
      }

      const result = await response.json();
      
      // Set as current session
      setCurrentSession({
        session_id: result.session_id,
        filename: result.filename,
        chunks_count: result.chunks_count
      });
      
      // Switch to RAG mode
      setChatMode('rag');
      
      // Clear previous messages
      setMessages([]);
      
      // Add success message
      setMessages([{
        role: 'assistant',
        content: `PDF "${result.filename}" uploaded successfully! I've processed ${result.chunks_count} text chunks. You can now ask me questions about this document.`
      }]);

      // Reload sessions
      await loadSessions();

    } catch (error) {
      console.error('Upload error:', error);
      setMessages([{
        role: 'assistant',
        content: `Error uploading PDF: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]);
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      let response;
      
      if (chatMode === 'rag' && currentSession) {
        // RAG chat
        response = await fetch('/api/rag/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: currentSession.session_id,
            user_message: input,
            model: "gpt-4.1-mini"
          }),
        });
      } else {
        // General chat
        response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_message: input,
            developer_message: "Respond in Markdown with bullet points where helpful. Include code examples in code blocks. Label your answer sections with headers. You are a spiritual guide that combines Isaac Asimov's scientific vision with ancient Indian wisdom. Respond with insights that merge Asimov's Three Laws of Robotics with concepts from Vedanta, while maintaining a futuristic yet spiritual perspective.",
            model: "gpt-4.1-mini"
          }),
        });
      }

      if (!response.ok) {
        throw new Error('Failed to get response from the server');
      }

      // Handle JSON response
      const responseData = await response.json();
      
      if (responseData.error) {
        throw new Error(responseData.error);
      }
      
      // Add assistant message
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: responseData.content || responseData.message || 'No response content'
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Error: ${error instanceof Error ? error.message : 'Failed to connect to the backend'}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const switchToGeneralChat = () => {
    setChatMode('general');
    setCurrentSession(null);
    setMessages([]);
  };

  const switchToRAGChat = (session: Session) => {
    setChatMode('rag');
    setCurrentSession(session);
    setMessages([{
      role: 'assistant',
      content: `Switched to chat with "${session.filename}". You can now ask me questions about this document.`
    }]);
  };

  const deleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(`/api/rag/sessions/${sessionId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await loadSessions();
        if (currentSession?.session_id === sessionId) {
          switchToGeneralChat();
        }
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-purple-900 to-slate-900 text-white">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <header className="text-center mb-8">
          <div className="relative">
            <h1 className="text-5xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-amber-400 via-purple-400 to-cyan-400">
              Asimov-Vedanta Interface
            </h1>
            <div className="absolute -top-4 -right-4 text-2xl">ॐ</div>
          </div>
          <p className="text-purple-200 mt-2">Where Robotics Laws meet Cosmic Dharma</p>
          <div className="mt-4 text-sm text-purple-300">
            <p>First Law: A robot may not injure a human being or, through inaction, allow a human being to come to harm.</p>
            <p>Second Law: A robot must obey orders given it by human beings except where such orders would conflict with the First Law.</p>
            <p>Third Law: A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.</p>
          </div>
        </header>

        {/* Mode Selection and PDF Upload */}
        <div className="bg-black/40 backdrop-blur-lg rounded-lg p-6 mb-6 border border-purple-500/30">
          <div className="flex flex-wrap gap-4 items-center justify-center mb-4">
            <button
              onClick={switchToGeneralChat}
              className={`px-4 py-2 rounded-lg font-semibold transition-all border ${
                chatMode === 'general'
                  ? 'bg-amber-600 border-amber-400'
                  : 'bg-gray-700 border-gray-500 hover:bg-gray-600'
              }`}
            >
              General Chat
            </button>
            <button
              onClick={() => document.getElementById('pdf-upload')?.click()}
              disabled={uploading}
              className="px-4 py-2 bg-gradient-to-r from-green-600 to-blue-600 rounded-lg font-semibold hover:from-green-700 hover:to-blue-700 transition-all disabled:opacity-50 border border-green-500/30"
            >
              {uploading ? 'Uploading...' : 'Upload PDF'}
            </button>
            <input
              id="pdf-upload"
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>

          {/* Session Management */}
          {sessions.length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold mb-3 text-purple-200">Available Documents:</h3>
              <div className="flex flex-wrap gap-2">
                {sessions.map((session) => (
                  <div key={session.session_id} className="flex items-center gap-2 bg-gray-800/50 rounded-lg p-3 border border-gray-600">
                    <button
                      onClick={() => switchToRAGChat(session)}
                      className={`text-sm px-3 py-1 rounded transition-all ${
                        currentSession?.session_id === session.session_id
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-600 hover:bg-gray-500'
                      }`}
                    >
                      {session.filename}
                    </button>
                    <button
                      onClick={() => deleteSession(session.session_id)}
                      className="text-red-400 hover:text-red-300 text-sm px-2 py-1 rounded hover:bg-red-900/30"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Current Session Info */}
          {currentSession && (
            <div className="mt-4 p-3 bg-purple-900/30 rounded-lg border border-purple-500/30">
              <p className="text-purple-200">
                <span className="font-semibold">Current Document:</span> {currentSession.filename} 
                <span className="text-sm text-purple-300 ml-2">({currentSession.chunks_count} chunks)</span>
              </p>
            </div>
          )}
        </div>

        {/* Chat Interface */}
        <div className="bg-black/40 backdrop-blur-lg rounded-lg p-6 mb-6 h-[60vh] overflow-y-auto border border-purple-500/30">
          {messages.map((message, index) => (
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
                <p className="text-sm opacity-75 mb-1">
                  {message.role === 'user' ? 'You' : chatMode === 'rag' ? 'Document Assistant' : 'Asimov-Vedanta Guide'}
                </p>
                <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="text-center text-purple-300">
              <div className="inline-block animate-pulse">
                {chatMode === 'rag' ? 'Searching document and generating response...' : 'Processing through the cosmic network...'}
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              chatMode === 'rag' 
                ? "Ask about the uploaded document..."
                : "Ask about the intersection of robotics and consciousness..."
            }
            className="flex-1 p-4 rounded-lg bg-black/40 backdrop-blur-lg text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 border border-purple-500/30"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-4 bg-gradient-to-r from-amber-600 to-purple-600 rounded-lg font-semibold hover:from-amber-700 hover:to-purple-700 transition-all disabled:opacity-50 border border-purple-500/30"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
