"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SystemStatus } from "@/components/status-indicator";
import {
  Send,
  Globe,
  TestTube,
  User,
  Sparkles,
  Clock,
  Code,
  Activity,
  Bot,
  Plus,
  ArrowUp,
} from "lucide-react";
import { LoadingPulse } from "@/components/loading-spinner";
import JsonDataViewer from "@/components/json-data-viewer";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  data?: any;
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isChatExpanded, setIsChatExpanded] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const messagesRef = useRef(messages);

  useEffect(() => {
    messagesRef.current = messages;
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const currentInput = input;
    const isFirstMessage = messages.length === 0;

    // Expand the chat view on the first message
    if (isFirstMessage && !isChatExpanded) {
      setIsChatExpanded(true);
    }
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: currentInput,
      timestamp: new Date(),
    };

    const newMessages = [...messagesRef.current, userMessage];
    
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: newMessages.map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.message,
        timestamp: new Date(),
        data: data.data,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "❌ Sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getMessageIcon = (role: "user" | "assistant") => {
    if (role === "user") return <User className="w-4 h-4" />;
    return <Bot className="w-4 h-4" />;
  };

  const formatMessage = (content: string) => {
    return content.split("\n").map((line, index) => {
      if (line.startsWith("**") && line.endsWith("**")) {
        return (
          <strong key={index} className="font-semibold">
            {line.slice(2, -2)}
          </strong>
        );
      }
      if (line.startsWith("*") && line.endsWith("*")) {
        return (
          <em key={index} className="italic">
            {line.slice(1, -1)}
          </em>
        );
      }
      return <p key={index} className="mb-2 last:mb-0">{line}</p>;
    });
  };

  return (
    <div className="min-h-screen bg-[#f7f7f8] flex items-center justify-center p-4">
      {/* Subtle background pattern */}
      <div className="fixed inset-0 opacity-50 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,rgba(156,146,172,0.03)_1px,transparent_0)] bg-[length:20px_20px]"></div>
      </div>
      
      <div className="absolute top-6">
        <SystemStatus />
      </div>

      <div className="relative z-10 w-full max-w-5xl mx-auto">
        {!isChatExpanded ? (
          <div className="text-center">
            <h1 className="text-6xl font-bold text-gray-800 mb-8" style={{ fontFamily: "'Poppins', sans-serif" }}>Couch</h1>
            <div
              className="bg-white border border-gray-200/80 shadow-md rounded-2xl p-4 w-full max-w-3xl mx-auto text-left"
            >
              <textarea
                placeholder="Ask me to battle test a website..."
                className="w-full bg-transparent outline-none resize-none text-lg text-gray-700 placeholder:text-gray-400"
                rows={3}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <div className="flex justify-between items-center mt-3">
                <div className="flex gap-2 items-center">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="rounded-full text-gray-500 hover:bg-gray-100 hover:text-gray-800"
                  >
                    <Plus className="h-5 w-5" />
                  </Button>
                  <Button
                    variant="ghost"
                    className="rounded-full text-gray-500 hover:bg-gray-100 hover:text-gray-800 px-4"
                  >
                    <Globe className="h-4 w-4 mr-2" />
                    Public
                  </Button>
                </div>
                <Button
                  size="icon"
                  className="rounded-full bg-gray-800 hover:bg-gray-900 text-white w-9 h-9"
                  onClick={sendMessage}
                  disabled={isLoading}
                >
                  <ArrowUp className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <Card className="bg-white border border-gray-200/80 shadow-lg rounded-2xl w-full">
            <CardHeader className="border-b border-gray-200/80 p-4">
              <CardTitle className="flex items-center gap-3 text-base text-gray-800">
                <div className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="font-bold text-lg" style={{ fontFamily: "'Poppins', sans-serif" }}>Couch</div>
              </CardTitle>
            </CardHeader>

            <CardContent className="p-4">
              <ScrollArea
                className="h-[calc(100vh-280px)] min-h-[400px] mb-4 pr-4 custom-scrollbar"
                ref={scrollRef}
              >
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${
                        message.role === "user" ? "justify-end" : "justify-start"
                      } animate-in slide-in-from-bottom-2 duration-300`}
                    >
                      {message.role === "assistant" && (
                        <div className="flex-shrink-0 w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center self-start">
                          {getMessageIcon(message.role)}
                        </div>
                      )}

                      <div
                        className={`max-w-[80%] p-4 rounded-xl ${
                          message.role === "user"
                            ? "bg-gray-800 text-white"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        <div className="space-y-2">
                          <div className="text-sm leading-relaxed prose prose-sm max-w-none">
                            {formatMessage(message.content)}
                          </div>

                          {message.data && (
                            <div className="mt-3 pt-3 border-t border-gray-200/80">
                              <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                                <Code className="w-3 h-3" />
                                Technical Details
                              </div>
                              <JsonDataViewer data={message.data} />
                            </div>
                          )}

                          <div className="flex items-center gap-1 text-xs opacity-60 pt-1">
                            <Clock className="w-3 h-3" />
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      </div>

                      {message.role === "user" && (
                        <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center self-end">
                          {getMessageIcon(message.role)}
                        </div>
                      )}
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex gap-3 justify-start animate-in slide-in-from-bottom-2 duration-300">
                      <div className="flex-shrink-0 w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-gray-100 p-4 rounded-xl">
                        <LoadingPulse />
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <Input
                    placeholder="Ask me to test a website..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="h-12 pl-4 pr-12 text-base border-gray-200 focus:border-gray-400 focus:ring-2 focus:ring-gray-200/50 rounded-lg transition-all duration-200"
                    disabled={isLoading}
                  />
                  <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400">
                    <Sparkles className="w-4 h-4" />
                  </div>
                </div>
                <Button
                  onClick={sendMessage}
                  disabled={isLoading || !input.trim()}
                  size="lg"
                  className="h-12 px-5 bg-gray-800 hover:bg-gray-900 rounded-lg transition-all"
                >
                  <Send className="w-4 h-4 text-white" />
                </Button>
              </div>

              <div className="mt-3 flex flex-wrap gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setInput("Test https://google.com")}
                  className="text-sm text-gray-500 bg-gray-100 hover:bg-gray-200 hover:text-gray-800"
                >
                  <Globe className="w-3 h-3 mr-2" />
                  Test Google
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setInput("Scrape localhost:3001")}
                  className="text-sm text-gray-500 bg-gray-100 hover:bg-gray-200 hover:text-gray-800"
                >
                  <Activity className="w-3 h-3 mr-2" />
                  Test Localhost
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() =>
                    setInput("Generate tests for https://example.com")
                  }
                  className="text-sm text-gray-500 bg-gray-100 hover:bg-gray-200 hover:text-gray-800"
                >
                  <TestTube className="w-3 h-3 mr-2" />
                  Generate Tests
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
