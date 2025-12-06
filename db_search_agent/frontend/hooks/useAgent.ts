"use client";

import { useState, useCallback } from "react";
import { api } from "@/lib/api";

interface UseAgentOptions {
  sessionId?: string;
}

export function useAgent(options: UseAgentOptions = {}) {
  const { sessionId: initialSessionId } = options;
  const [sessionId] = useState(
    initialSessionId || `session-${Date.now()}-${Math.random()}`
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<
    Array<{ role: "user" | "agent"; content: string }>
  >([]);

  const queryAgent = useCallback(
    async (message: string) => {
      if (!message.trim()) return;

      setLoading(true);
      setError(null);

      // Add user message to history
      const userMessage = { role: "user" as const, content: message };
      setMessages((prev) => [...prev, userMessage]);

      try {
        // Direct connection to agent server (bypasses Express backend)
        const data = await api.agent.query(message, sessionId);
        
        const agentMessage = {
          role: "agent" as const,
          content: data.response || "No response from agent",
        };
        setMessages((prev) => [...prev, agentMessage]);
        return agentMessage.content;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to query agent";
        setError(errorMessage);
        console.error("Agent query error:", err);
        
        // Add error message to chat
        const errorMsg = {
          role: "agent" as const,
          content: `Sorry, I encountered an error: ${errorMessage}`,
        };
        setMessages((prev) => [...prev, errorMsg]);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    sessionId,
    messages,
    loading,
    error,
    queryAgent,
    clearMessages,
  };
}

