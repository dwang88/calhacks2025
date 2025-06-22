"use client"

import { useState } from "react"
import { ChevronDown } from "lucide-react"

interface TimePeriodSelectorProps {
  value: string
  onChange: (value: string) => void
}

export function TimePeriodSelector({ value, onChange }: TimePeriodSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)

  const periods = ["This Week", "Last Week", "This Month", "Last Month", "This Quarter"]

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:text-gray-900"
      >
        {value}
        <ChevronDown className="w-4 h-4" />
      </button>

      {isOpen && (
        <div className="absolute right-0 z-10 mt-1 w-40 bg-white border rounded-md shadow-lg">
          {periods.map((period) => (
            <button
              key={period}
              onClick={() => {
                onChange(period)
                setIsOpen(false)
              }}
              className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
            >
              {period}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
