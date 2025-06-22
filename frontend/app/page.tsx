"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { LoadingDots, LoadingPulse } from "@/components/loading-spinner";
import { SystemStatus } from "@/components/status-indicator";
import {
  Loader2,
  Send,
  Globe,
  TestTube,
  User,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
  Shield,
  Code,
  Github,
  ExternalLink,
  TrendingUp,
  Activity,
  ConciergeBell,
} from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  data?: any;
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        '🚀 **Welcome to Website Testing Assistant!**\n\nI\'m your AI-powered testing companion that can:\n\n✨ **Scrape & Analyze** websites for issues\n🧪 **Generate Playwright tests** automatically\n⚡ **Run tests** and report results\n📋 **Create GitHub issues** for problems found\n\nTry asking me: *"Test https://example.com"* or *"Scrape localhost:3001"*',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<"online" | "offline">(
    "online"
  );
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Check system status
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/");
        if (response.ok) {
          setSystemStatus("online");
        } else {
          setSystemStatus("offline");
        }
      } catch (error) {
        setSystemStatus("offline");
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map((msg) => ({
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
    if (role === "user") return <User className="w-5 h-5" />;
    return <ConciergeBell className="w-6 h-6 text-white" />;
  };

  const formatMessage = (content: string) => {
    // Convert markdown-style formatting to JSX
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
      if (line.startsWith("✨")) {
        return (
          <div key={index} className="flex items-center gap-2 text-green-600">
            <Sparkles className="w-4 h-4" />
            {line.slice(1)}
          </div>
        );
      }
      if (line.startsWith("🧪")) {
        return (
          <div key={index} className="flex items-center gap-2 text-blue-600">
            <TestTube className="w-4 h-4" />
            {line.slice(1)}
          </div>
        );
      }
      if (line.startsWith("⚡")) {
        return (
          <div key={index} className="flex items-center gap-2 text-yellow-600">
            <Zap className="w-4 h-4" />
            {line.slice(1)}
          </div>
        );
      }
      if (line.startsWith("📋")) {
        return (
          <div key={index} className="flex items-center gap-2 text-purple-600">
            <Github className="w-4 h-4" />
            {line.slice(1)}
          </div>
        );
      }
      if (line.startsWith("🚀")) {
        return (
          <div key={index} className="flex items-center gap-2 text-orange-600">
            <ExternalLink className="w-4 h-4" />
            {line.slice(1)}
          </div>
        );
      }
      return <span key={index}>{line}</span>;
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 p-4">
        <div className="max-w-6xl mx-auto">
          {/* Enhanced Header */}
          <div className="text-center mb-8">
            <h1 className="text-6xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 bg-clip-text text-transparent mb-4 pt-12">
              Website Testing Assistant
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              AI-powered website integrity testing with automated test
              generation, execution, and GitHub issue creation
            </p>

            {/* System Status */}
            <div className="mt-6">
              <SystemStatus />
            </div>

            {/* Feature badges */}
            <div className="flex flex-wrap justify-center gap-3 mt-6">
              <Badge
                variant="secondary"
                className="bg-white/80 backdrop-blur-sm"
              >
                <Sparkles className="w-3 h-3 mr-1" />
                AI-Powered
              </Badge>
              <Badge
                variant="secondary"
                className="bg-white/80 backdrop-blur-sm"
              >
                <TestTube className="w-3 h-3 mr-1" />
                Automated Testing
              </Badge>
              <Badge
                variant="secondary"
                className="bg-white/80 backdrop-blur-sm"
              >
                <Github className="w-3 h-3 mr-1" />
                GitHub Integration
              </Badge>
              <Badge
                variant="secondary"
                className="bg-white/80 backdrop-blur-sm"
              >
                <Shield className="w-3 h-3 mr-1" />
                Security Focused
              </Badge>
              <Badge
                variant="secondary"
                className="bg-white/80 backdrop-blur-sm"
              >
                <TrendingUp className="w-3 h-3 mr-1" />
                Real-time Analysis
              </Badge>
            </div>
          </div>

          {/* Enhanced Chat Interface */}
          <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-2xl">
            <CardHeader className="border-b border-gray-100">
              <CardTitle className="flex items-center gap-3 text-2xl">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <ConciergeBell className="w-6 h-6 text-white" />
                </div>
                <div>
                  <div>Chat Interface</div>
                  <div className="text-sm font-normal text-gray-500 mt-1">
                    Ask me to test, scrape, or generate tests for any website
                  </div>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {/* Messages */}
              <ScrollArea className="h-[500px] mb-6" ref={scrollRef}>
                <div className="space-y-6 pr-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-4 ${
                        message.role === "user"
                          ? "justify-end"
                          : "justify-start"
                      } animate-in slide-in-from-bottom-2 duration-300`}
                    >
                      {message.role === "assistant" && (
                        <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                          {getMessageIcon(message.role)}
                        </div>
                      )}

                      <div
                        className={`max-w-[85%] p-6 rounded-2xl shadow-lg ${
                          message.role === "user"
                            ? "bg-gradient-to-r from-blue-600 to-blue-700 text-white"
                            : "bg-white border border-gray-100"
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          {message.role === "user" && (
                            <div className="flex-shrink-0 w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                              {getMessageIcon(message.role)}
                            </div>
                          )}

                          <div className="flex-1 space-y-3">
                            <div className="prose prose-sm max-w-none">
                              {formatMessage(message.content)}
                            </div>

                            {/* Enhanced data display */}
                            {message.data && (
                              <div className="mt-4 pt-4 border-t border-gray-200">
                                <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                                  <Code className="w-3 h-3" />
                                  Technical Details
                                </div>
                                <div className="bg-gray-50 p-4 rounded-lg text-xs font-mono overflow-x-auto border">
                                  <pre className="whitespace-pre-wrap">
                                    {JSON.stringify(message.data, null, 2)}
                                  </pre>
                                </div>
                              </div>
                            )}

                            <div className="flex items-center gap-2 text-xs opacity-70">
                              <Clock className="w-3 h-3" />
                              {message.timestamp.toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex gap-4 justify-start animate-in slide-in-from-bottom-2 duration-300">
                      <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                        <ConciergeBell className="w-5 h-5 text-white" />
                      </div>
                      <div className="bg-white border border-gray-100 p-6 rounded-2xl shadow-lg">
                        <div className="flex items-center gap-3">
                          <LoadingPulse />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              {/* Enhanced Input */}
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <Input
                    placeholder="Try: 'Test https://example.com' or 'Scrape localhost:3001'"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="h-14 pl-4 pr-12 text-base border-2 border-gray-200 focus:border-blue-500 rounded-xl shadow-sm transition-all duration-200"
                    disabled={isLoading}
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                    <Sparkles className="w-5 h-5" />
                  </div>
                </div>
                <Button
                  onClick={sendMessage}
                  disabled={isLoading || !input.trim()}
                  size="lg"
                  className="h-14 px-8 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl shadow-lg transition-all duration-200 transform hover:scale-105"
                >
                  <Send className="w-5 h-5" />
                </Button>
              </div>

              {/* Quick actions */}
              <div className="mt-6 flex flex-wrap gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInput("Test https://google.com")}
                  className="text-sm bg-white/50 backdrop-blur-sm hover:bg-white/80"
                >
                  <Globe className="w-4 h-4 mr-2" />
                  Test Google
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInput("Scrape localhost:3001")}
                  className="text-sm bg-white/50 backdrop-blur-sm hover:bg-white/80"
                >
                  <Activity className="w-4 h-4 mr-2" />
                  Test Localhost
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setInput("Generate tests for https://example.com")
                  }
                  className="text-sm bg-white/50 backdrop-blur-sm hover:bg-white/80"
                >
                  <TestTube className="w-4 h-4 mr-2" />
                  Generate Tests
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Footer */}
          <div className="text-center mt-8 text-gray-500">
            <p className="text-sm">
              Built with Next.js, FastAPI, and AI-powered testing automation
            </p>
            <p className="text-xs mt-2 opacity-70">
              CalHacks 2025 Demo • Powered by Claude AI
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
