import VoiceAgent from "@/components/VoiceAgent";

export default function VoicePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Voice Product Assistant</h1>
          <p className="text-gray-600">
            Talk naturally with our AI assistant to find products, check availability, and more!
          </p>
        </div>
        <div className="h-[600px]">
          <VoiceAgent />
        </div>
      </div>
    </div>
  );
}

