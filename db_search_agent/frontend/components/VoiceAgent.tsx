"use client";

import { useState, useRef, useEffect } from "react";
import { useVoiceAgent } from "@/hooks/useVoiceAgent";

export default function VoiceAgent() {
  const {
    messages,
    isConnected,
    isRecording,
    isAgentResponding,
    error,
    startAudio,
    stopAudio,
    sendTextMessage,
    interruptAgent,
    disconnect,
    clearMessages,
  } = useVoiceAgent();

  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !isConnected) return;

    sendTextMessage(input.trim());
    setInput("");
  };

  const handleStartAudio = async () => {
    try {
      await startAudio();
    } catch (err) {
      console.error("Failed to start audio:", err);
    }
  };

  const handleStopAudio = () => {
    stopAudio();
  };

  return (
    <div className="flex flex-col h-full max-h-[600px] bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b bg-blue-600 text-white rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Voice Product Assistant</h2>
            <p className="text-sm text-blue-100">
              {isConnected
                ? isRecording
                  ? "🎤 Listening..."
                  : "Connected - Ready to chat"
                : "Click 'Start Voice' to begin"}
            </p>
          </div>
          <div className="flex gap-2">
            {!isRecording ? (
              <button
                onClick={handleStartAudio}
                disabled={!isConnected && false}
                className="px-4 py-2 text-sm bg-green-600 hover:bg-green-700 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                🎤 Start Voice
              </button>
            ) : (
              <button
                onClick={handleStopAudio}
                className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 rounded transition-colors"
              >
                ⏹ Stop Voice
              </button>
            )}
            {isAgentResponding && (
              <button
                onClick={interruptAgent}
                className="px-4 py-2 text-sm bg-orange-600 hover:bg-orange-700 rounded transition-colors"
                title="Stop agent response"
              >
                ⏸ Stop Response
              </button>
            )}
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
      </div>

      {/* Connection Status */}
      <div className="px-4 py-2 border-b bg-gray-50">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? "bg-green-500" : "bg-red-500"
            }`}
          />
          <span className="text-sm text-gray-600">
            {isConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <p className="text-lg mb-2">🎤 Voice Product Assistant</p>
            <p className="text-sm mb-4">
              Click "Start Voice" to begin a voice conversation, or type a message below.
            </p>
            <p className="text-xs text-gray-400">
              Try asking: "Find me red t-shirts" or "What products are in stock?"
            </p>
          </div>
        )}

        {messages.map((message, index) => (
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
              {message.isTranscript && (
                <span className={`text-xs block mb-1 ${
                  message.role === "user" 
                    ? "text-blue-100" 
                    : "text-gray-500"
                }`}>
                  {message.role === "user" ? "🎤 Audio transcript:" : "🔊 Audio transcript:"}
                </span>
              )}
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
              <span className="text-xs opacity-70 mt-1 block">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}

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
            placeholder={
              isRecording
                ? "Speaking... (or type a message)"
                : "Type a message or start voice..."
            }
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={!isConnected}
          />
          <button
            type="submit"
            disabled={!isConnected || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          {isRecording
            ? "🎤 Voice mode active - speak naturally or type to send a message"
            : "Type a message or click 'Start Voice' to use voice mode"}
        </p>
      </form>
    </div>
  );
}

