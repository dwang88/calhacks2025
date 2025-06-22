"use client"

import { CustomAreaChart } from "./area-chart"

const budgetVsSecondaryData = [
  { date: "02 Mon", primary: 33, secondary: 25 },
  { date: "03 Tue", primary: 30, secondary: 20 },
  { date: "04 Wed", primary: 29, secondary: 25 },
  { date: "05 Thu", primary: 26, secondary: 26 },
  { date: "06 Fri", primary: 27, secondary: 24 },
  { date: "07 Sat", primary: 27, secondary: 20 },
  { date: "08 Sun", primary: 32, secondary: 31 },
]

const budgetVsInvoiceData = [
  { date: "02 Mon", primary: 34, secondary: 24 },
  { date: "03 Tue", primary: 30, secondary: 20 },
  { date: "04 Wed", primary: 29, secondary: 25 },
  { date: "05 Thu", primary: 26, secondary: 24 },
  { date: "06 Fri", primary: 27, secondary: 23 },
  { date: "07 Sat", primary: 27, secondary: 30 },
  { date: "08 Sun", primary: 32, secondary: 31 },
]

export function ChartsSection() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      <CustomAreaChart
        title="Budget vs. Secondary"
        data={budgetVsSecondaryData}
        colors={{
          primary: "#E3F0FF",
          secondary: "#FFE9E9",
        }}
        labels={{
          primary: "Budget",
          secondary: "Secondary",
        }}
      />
      <CustomAreaChart
        title="Budget vs. Invoice"
        data={budgetVsInvoiceData}
        colors={{
          primary: "#FFF8E6",
          secondary: "#E8FFE9",
        }}
        labels={{
          primary: "Budget",
          secondary: "Invoice",
        }}
      />
    </div>
  )
}
