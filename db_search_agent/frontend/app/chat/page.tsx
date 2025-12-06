import AgentChat from "@/components/AgentChat";

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Chat with Product Assistant</h1>
          <p className="text-gray-600">
            Get help finding products, checking availability, and more!
          </p>
        </div>
        <div className="h-[600px]">
          <AgentChat />
        </div>
      </div>
    </div>
  );
}

