import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  className?: string;
}

export function LoadingSpinner({ 
  size = "md", 
  text = "Loading...", 
  className = "" 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6", 
    lg: "w-8 h-8"
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-600`} />
      {text && (
        <span className="text-sm font-medium text-gray-600">{text}</span>
      )}
    </div>
  );
}

export function LoadingDots() {
  return (
    <div className="flex items-center gap-1">
      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
      <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
    </div>
  );
}

export function LoadingPulse() {
  return (
    <div className="flex items-center gap-2">
      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
      <span className="text-sm font-medium text-gray-600">Processing...</span>
    </div>
  );
} 