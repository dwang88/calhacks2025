"use client"

import { useState } from "react"

interface FilterOption {
  label: string
  value: string
}

interface FilterProps {
  label: string
  options: FilterOption[]
  value: string
  onChange: (value: string) => void
}

function Filter({ label, options, value, onChange }: FilterProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 border rounded-md hover:border-gray-400"
      >
        <span className="text-gray-700">{value || label}</span>
        <svg
          className={`w-5 h-5 transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg">
          {options.map((option) => (
            <button
              key={option.value}
              onClick={() => {
                onChange(option.value)
                setIsOpen(false)
              }}
              className="w-full px-4 py-2 text-left hover:bg-gray-50"
            >
              {option.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export function FilterBar() {
  const [filters, setFilters] = useState({
    timeline: "",
    accounts: "",
    salesPerson: "",
    product: "",
  })

  const handleFilterChange = (filterName: string) => (value: string) => {
    setFilters((prev) => ({ ...prev, [filterName]: value }))
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="flex items-center gap-2 p-3 border rounded-md cursor-pointer hover:border-gray-400">
        <span className="text-gray-700">Timeline</span>
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>

      <Filter
        label="Accounts"
        options={[
          { label: "All Accounts", value: "all" },
          { label: "Active Accounts", value: "active" },
          { label: "Inactive Accounts", value: "inactive" },
        ]}
        value={filters.accounts}
        onChange={handleFilterChange("accounts")}
      />

      <Filter
        label="Sales Person"
        options={[
          { label: "All Sales Persons", value: "all" },
          { label: "North Region", value: "north" },
          { label: "South Region", value: "south" },
          { label: "East Region", value: "east" },
          { label: "West Region", value: "west" },
        ]}
        value={filters.salesPerson}
        onChange={handleFilterChange("salesPerson")}
      />

      <Filter
        label="Product"
        options={[
          { label: "All Products", value: "all" },
          { label: "In Stock", value: "in-stock" },
          { label: "Out of Stock", value: "out-of-stock" },
          { label: "Low Stock", value: "low-stock" },
        ]}
        value={filters.product}
        onChange={handleFilterChange("product")}
      />
    </div>
  )
}
