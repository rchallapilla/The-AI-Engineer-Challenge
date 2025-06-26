'use client';

import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
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

      if (!response.ok) {
        throw new Error('Failed to get response from the server');
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      let accumulatedResponse = '';
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Convert the Uint8Array to text
        const text = new TextDecoder().decode(value);
        accumulatedResponse += text;

        // Update the last message with the accumulated response
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1].content = accumulatedResponse;
          return newMessages;
        });
      }
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

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-purple-900 to-slate-900 text-white">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
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
                  {message.role === 'user' ? 'You' : 'Asimov-Vedanta Guide'}
                </p>
                <p className="leading-relaxed">{message.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="text-center text-purple-300">
              <div className="inline-block animate-pulse">Processing through the cosmic network...</div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the intersection of robotics and consciousness..."
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
