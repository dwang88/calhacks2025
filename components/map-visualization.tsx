"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface DataPoint {
  id: string
  lat: number
  lng: number
  type: "distributor" | "hospital"
  value: number
}

// Sample data points - in a real application, these would be more accurate
const dataPoints: DataPoint[] = [
  { id: "1", lat: 28.7041, lng: 77.1025, type: "distributor", value: 20 },
  { id: "2", lat: 28.7041, lng: 77.1025, type: "hospital", value: 200 },
  // Add more data points for different regions
]

export function MapVisualization() {
  return (
    <Card className="mt-6">
      <CardHeader className="flex flex-row items-center justify-between pb-8">
        <CardTitle className="text-base font-medium">Distribution Network</CardTitle>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-purple-200" />
            <span className="text-sm text-gray-600">Distributors</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-pink-200" />
            <span className="text-sm text-gray-600">Hospitals</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative aspect-[4/3] w-full">
          <svg viewBox="0 0 900 900" className="h-full w-full" fill="none" stroke="currentColor" strokeWidth="1">
            {/* Simplified India map outline */}
            <path
              d="M450,100 L500,150 L550,200 L600,250 L650,300 L700,350 L750,400 L800,450 L750,500 L700,550 L650,600 L600,650 L550,700 L500,750 L450,800 L400,750 L350,700 L300,650 L250,600 L200,550 L150,500 L200,450 L250,400 L300,350 L350,300 L400,250 L450,200 Z"
              className="fill-white stroke-gray-200"
            />

            {/* Data point circles */}
            {dataPoints.map((point) => (
              <g
                key={point.id}
                transform={`translate(${point.lng}, ${point.lat})`}
                className="transition-opacity hover:opacity-80"
              >
                <circle
                  r={point.type === "distributor" ? 15 : 20}
                  className={`${point.type === "distributor" ? "fill-purple-200" : "fill-pink-200"}`}
                />
                <text className="text-xs fill-gray-600" textAnchor="middle" dy=".3em">
                  {point.value}
                </text>
              </g>
            ))}
          </svg>
        </div>
      </CardContent>
    </Card>
  )
}
