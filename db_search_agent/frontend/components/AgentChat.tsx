"use client";

import { useState, useRef, useEffect } from "react";
import { useAgent } from "@/hooks/useAgent";

interface Message {
  role: "user" | "agent";
  content: string;
  timestamp: Date;
  images?: string[];
}

export default function AgentChat() {
  const { messages, loading, error, queryAgent, clearMessages } = useAgent();
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setIsTyping(true);

    try {
      await queryAgent(userMessage);
    } catch (err) {
      console.error("Failed to send message:", err);
    } finally {
      setIsTyping(false);
    }
  };

  const displayMessages: Message[] = messages.map((msg) => ({
    ...msg,
    timestamp: new Date(),
  }));

  return (
    <div className="flex flex-col h-full max-h-[600px] bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b bg-blue-600 text-white rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Product Assistant</h2>
            <p className="text-sm text-blue-100">
              Ask me anything about our products!
            </p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="px-3 py-1 text-sm bg-blue-700 hover:bg-blue-800 rounded transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {displayMessages.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <p className="text-lg mb-2">👋 Hello! I'm your product assistant.</p>
            <p className="text-sm">
              Try asking me: "Find me red t-shirts" or "What products are in stock?"
            </p>
          </div>
        )}

        {displayMessages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
              {message.images && message.images.length > 0 && (
                <div className={`mt-3 grid gap-2 ${
                  message.images.length === 1 
                    ? 'grid-cols-1' 
                    : message.images.length === 2 
                    ? 'grid-cols-2' 
                    : 'grid-cols-2 md:grid-cols-3'
                }`}>
                  {message.images.map((imageUrl, imgIndex) => (
                    <div key={imgIndex} className="rounded-lg overflow-hidden bg-gray-200">
                      <img
                        src={imageUrl}
                        alt={`Product image ${imgIndex + 1}`}
                        className="w-full h-auto object-cover cursor-pointer hover:opacity-90 transition-opacity"
                        loading="lazy"
                        onClick={() => window.open(imageUrl, '_blank')}
                        onError={(e) => {
                          // Hide image on error
                          (e.target as HTMLImageElement).style.display = 'none';
                        }}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about products..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Example: "Show me products under $50" or "Find red t-shirts"
        </p>
      </form>
    </div>
  );
}

