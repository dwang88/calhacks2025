"use client"

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TimePeriodSelector } from "./time-period-selector"
import { useState } from "react"

interface DataPoint {
  date: string
  primary: number
  secondary: number
}

interface AreaChartProps {
  title: string
  data: DataPoint[]
  colors: {
    primary: string
    secondary: string
  }
  labels: {
    primary: string
    secondary: string
  }
}

interface CustomTooltipProps {
  active?: boolean
  payload?: any[]
  colors: {
    primary: string
    secondary: string
  }
}

const CustomTooltip = ({ active, payload, colors }: CustomTooltipProps) => {
  if (!active || !payload || !payload.length) return null

  return (
    <div className="rounded-lg border bg-white p-2 shadow-sm">
      <div className="grid grid-cols-2 gap-2">
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="h-2 w-2 rounded-full"
              style={{
                backgroundColor: index === 0 ? colors.primary : colors.secondary,
              }}
            />
            <span className="text-sm font-medium">{`${entry.value}k`}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function CustomAreaChart({ title, data, colors, labels }: AreaChartProps) {
  const [period, setPeriod] = useState("This Week")

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-8">
        <CardTitle className="text-base font-medium">{title}</CardTitle>
        <TimePeriodSelector value={period} onChange={setPeriod} />
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex items-center justify-start gap-4">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full" style={{ backgroundColor: colors.primary }} />
            <span className="text-sm text-gray-600">{labels.primary}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full" style={{ backgroundColor: colors.secondary }} />
            <span className="text-sm text-gray-600">{labels.secondary}</span>
          </div>
        </div>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
              <defs>
                <linearGradient id={`gradient-${title}-1`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={colors.primary} stopOpacity={0.2} />
                  <stop offset="100%" stopColor={colors.primary} stopOpacity={0} />
                </linearGradient>
                <linearGradient id={`gradient-${title}-2`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={colors.secondary} stopOpacity={0.2} />
                  <stop offset="100%" stopColor={colors.secondary} stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} tickMargin={8} />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 12 }}
                tickMargin={8}
                tickFormatter={(value) => `${value}k`}
              />
              <Tooltip content={(props) => <CustomTooltip {...props} colors={colors} />} />
              <Area
                type="monotone"
                dataKey="primary"
                stroke={colors.primary}
                strokeWidth={2}
                fill={`url(#gradient-${title}-1)`}
              />
              <Area
                type="monotone"
                dataKey="secondary"
                stroke={colors.secondary}
                strokeWidth={2}
                fill={`url(#gradient-${title}-2)`}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
