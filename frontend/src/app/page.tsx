"use client";

import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            AI Agent Chatbot
          </h1>
          <p className="text-gray-600">
            Test the AI agent with web search capabilities
          </p>
        </div>
        <ChatInterface />
      </div>
    </main>
  );
}
