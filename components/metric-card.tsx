import type React from "react"

interface MetricCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  color: "green" | "blue" | "purple" | "yellow"
}

export function MetricCard({ title, value, icon, color }: MetricCardProps) {
  const colorClasses = {
    green: "bg-green-100 text-green-600",
    blue: "bg-blue-100 text-blue-600",
    purple: "bg-purple-100 text-purple-600",
    yellow: "bg-yellow-100 text-yellow-600",
  }

  return (
    <div className="flex items-center gap-3 p-4 border rounded-lg">
      <div className={`p-2 rounded-lg ${colorClasses[color]}`}>{icon}</div>
      <div>
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-xl font-semibold">{value}</p>
      </div>
    </div>
  )
}
