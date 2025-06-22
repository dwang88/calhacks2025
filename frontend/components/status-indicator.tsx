import { CheckCircle, AlertCircle, Clock, Wifi, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface StatusIndicatorProps {
  status: "online" | "offline" | "processing" | "error";
  message?: string;
  showIcon?: boolean;
}

export function StatusIndicator({
  status,
  message,
  showIcon = true,
}: StatusIndicatorProps) {
  const statusConfig = {
    online: {
      icon: <CheckCircle className="w-3 h-3" />,
      color: "bg-green-500",
      text: "text-green-700",
      bg: "bg-green-50",
      border: "border-green-200",
      label: "Online",
    },
    offline: {
      icon: <WifiOff className="w-3 h-3" />,
      color: "bg-gray-500",
      text: "text-gray-700",
      bg: "bg-gray-50",
      border: "border-gray-200",
      label: "Offline",
    },
    processing: {
      icon: <Clock className="w-3 h-3" />,
      color: "bg-yellow-500",
      text: "text-yellow-700",
      bg: "bg-yellow-50",
      border: "border-yellow-200",
      label: "Processing",
    },
    error: {
      icon: <AlertCircle className="w-3 h-3" />,
      color: "bg-red-500",
      text: "text-red-700",
      bg: "bg-red-50",
      border: "border-red-200",
      label: "Error",
    },
  };

  const config = statusConfig[status];

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full ${config.bg} ${config.border} border`}
    >
      {showIcon && (
        <div
          className={`w-2 h-2 rounded-full ${config.color} animate-pulse`}
        ></div>
      )}
      <span className={`text-xs font-medium ${config.text}`}>
        {message || config.label}
      </span>
    </div>
  );
}

export function SystemStatus() {
  return (
    <div className="flex items-center gap-4 text-sm">
      <StatusIndicator status="online" message="System Operational" />
    </div>
  );
}
