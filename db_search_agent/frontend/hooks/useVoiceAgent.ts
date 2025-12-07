"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { startAudioRecorderWorklet, stopMicrophone } from "@/lib/audio-recorder";
import { startAudioPlayerWorklet, base64ToArrayBuffer } from "@/lib/audio-player";

interface UseVoiceAgentOptions {
  sessionId?: string;
}

interface Message {
  role: "user" | "agent";
  content: string;
  timestamp: Date;
  isTranscript?: boolean;
}

export function useVoiceAgent(options: UseVoiceAgentOptions = {}) {
  const { sessionId: initialSessionId } = options;
  const [sessionId] = useState(
    initialSessionId || `session-${Date.now()}-${Math.random()}`
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isAgentResponding, setIsAgentResponding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const websocketRef = useRef<WebSocket | null>(null);
  const audioPlayerNodeRef = useRef<AudioWorkletNode | null>(null);
  const audioRecorderNodeRef = useRef<AudioWorkletNode | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const currentMessageIdRef = useRef<string | null>(null);
  const currentUserTranscriptIdRef = useRef<string | null>(null);

  const connectWebSocket = useCallback(
    async (isAudio: boolean) => {
      try {
        const agentServerUrl =
          process.env.NEXT_PUBLIC_AGENT_SERVER_URL || "http://localhost:8000";
        
        // Convert HTTP/HTTPS URL to WebSocket URL
        const wsProtocol = agentServerUrl.startsWith("https") ? "wss:" : "ws:";
        const wsHost = agentServerUrl.replace(/^https?:\/\//, "");
        const wsUrl = `${wsProtocol}//${wsHost}/ws/${sessionId}?is_audio=${isAudio}`;

        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log("WebSocket connection opened");
          setIsConnected(true);
          setError(null);
        };

        ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          console.log("[AGENT TO CLIENT]", message);

          // Handle turn complete
          if (message.turn_complete === true) {
            currentMessageIdRef.current = null;
            currentUserTranscriptIdRef.current = null; // Reset user transcript accumulation
            setIsRecording(false);
            setIsAgentResponding(false);
            return;
          }

          // Handle interrupt
          if (message.interrupted === true) {
            if (audioPlayerNodeRef.current) {
              audioPlayerNodeRef.current.port.postMessage({ command: "endOfAudio" });
            }
            setIsAgentResponding(false);
            return;
          }
          
          // If we receive any agent message, mark as responding
          if (message.mime_type === "text/plain" || message.mime_type === "audio/pcm") {
            if (message.role !== "user" && !message.is_user_transcript) {
              setIsAgentResponding(true);
            }
          }

          // Handle audio data
          if (message.mime_type === "audio/pcm" && audioPlayerNodeRef.current) {
            const audioData = base64ToArrayBuffer(message.data);
            audioPlayerNodeRef.current.port.postMessage(audioData);
          }

          // Handle text (transcript or regular text)
          if (message.mime_type === "text/plain") {
            // Check if this is a user transcript (input transcription)
            if (message.is_user_transcript && message.role === "user") {
              // Accumulate user transcripts into a single message
              if (currentUserTranscriptIdRef.current === null) {
                // Start a new user transcript message
                currentUserTranscriptIdRef.current = Math.random().toString(36).substring(7);
                const userMessage: Message = {
                  role: "user",
                  content: message.data,
                  timestamp: new Date(),
                  isTranscript: true,
                };
                setMessages((prev) => [...prev, userMessage]);
              } else {
                // Append to existing user transcript
                setMessages((prev) => {
                  const updated = [...prev];
                  const lastMessage = updated[updated.length - 1];
                  if (lastMessage && lastMessage.role === "user" && lastMessage.isTranscript) {
                    // Add space if needed
                    lastMessage.content += (lastMessage.content && !lastMessage.content.endsWith(" ") ? " " : "") + message.data;
                  }
                  return updated;
                });
              }
              return; // Don't process as agent message
            }
            
            // Reset user transcript ID when turn completes
            if (message.turn_complete) {
              currentUserTranscriptIdRef.current = null;
            }
            
            // Handle agent messages (output transcript or regular text)
            const messageRole = message.role || "agent";
            // Create new message for new turn
            if (currentMessageIdRef.current === null) {
              currentMessageIdRef.current = Math.random().toString(36).substring(7);
              const newMessage: Message = {
                role: messageRole as "user" | "agent",
                content: message.data,
                timestamp: new Date(),
                isTranscript: message.is_transcript || false,
              };
              setMessages((prev) => [...prev, newMessage]);
            } else {
              // Append to existing message (only if same role)
              setMessages((prev) => {
                const updated = [...prev];
                const lastMessage = updated[updated.length - 1];
                if (lastMessage && lastMessage.role === messageRole) {
                  lastMessage.content += message.data;
                } else {
                  // Different role, create new message
                  currentMessageIdRef.current = Math.random().toString(36).substring(7);
                  const newMessage: Message = {
                    role: messageRole as "user" | "agent",
                    content: message.data,
                    timestamp: new Date(),
                    isTranscript: message.is_transcript || false,
                  };
                  updated.push(newMessage);
                }
                return updated;
              });
            }
          }
        };

        ws.onclose = () => {
          console.log("WebSocket connection closed");
          setIsConnected(false);
          // Attempt to reconnect after 5 seconds
          setTimeout(() => {
            if (isAudio) {
              connectWebSocket(true);
            }
          }, 5000);
        };

        ws.onerror = (e) => {
          console.error("WebSocket error:", e);
          setError("Connection error. Please try again.");
        };

        websocketRef.current = ws;
      } catch (err) {
        console.error("Failed to connect WebSocket:", err);
        setError(err instanceof Error ? err.message : "Failed to connect");
      }
    },
    [sessionId]
  );

  // Helper function to convert ArrayBuffer to base64
  const arrayBufferToBase64 = useCallback((buffer: ArrayBuffer): string => {
    let binary = "";
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }, []);

  const startAudio = useCallback(async () => {
    try {
      // Start audio output
      const [playerNode, playerContext] = await startAudioPlayerWorklet();
      audioPlayerNodeRef.current = playerNode;

      // Start audio input
      const [recorderNode, recorderContext, stream] = await startAudioRecorderWorklet(
        (pcmData) => {
          // Send audio data to server
          if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
            const base64Data = arrayBufferToBase64(pcmData);
            websocketRef.current.send(
              JSON.stringify({
                mime_type: "audio/pcm",
                data: base64Data,
              })
            );
          }
        }
      );
      audioRecorderNodeRef.current = recorderNode;
      micStreamRef.current = stream;

      // Connect WebSocket in audio mode
      await connectWebSocket(true);
      setIsRecording(true);
    } catch (err) {
      console.error("Failed to start audio:", err);
      setError(err instanceof Error ? err.message : "Failed to start audio");
    }
  }, [connectWebSocket, arrayBufferToBase64]);

  const stopAudio = useCallback(() => {
    if (micStreamRef.current) {
      stopMicrophone(micStreamRef.current);
      micStreamRef.current = null;
    }
    if (audioRecorderNodeRef.current) {
      audioRecorderNodeRef.current.disconnect();
      audioRecorderNodeRef.current = null;
    }
    if (audioPlayerNodeRef.current) {
      audioPlayerNodeRef.current.disconnect();
      audioPlayerNodeRef.current = null;
    }
    setIsRecording(false);
  }, []);

  const sendTextMessage = useCallback(
    (message: string) => {
      if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
        // Add user message to UI
        const userMessage: Message = {
          role: "user",
          content: message,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);

        // Send to server
        websocketRef.current.send(
          JSON.stringify({
            mime_type: "text/plain",
            data: message,
          })
        );
      }
    },
    []
  );

  const disconnect = useCallback(() => {
    stopAudio();
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
    setIsConnected(false);
  }, [stopAudio]);

  const interruptAgent = useCallback(() => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      // Send interrupt signal to server
      websocketRef.current.send(
        JSON.stringify({
          action: "interrupt",
          mime_type: "interrupt",
        })
      );
      console.log("[CLIENT TO AGENT]: Sent interrupt signal");
      
      // Stop audio playback immediately
      if (audioPlayerNodeRef.current) {
        audioPlayerNodeRef.current.port.postMessage({ command: "endOfAudio" });
      }
      
      setIsAgentResponding(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    sessionId,
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
  };
}

