import { Header } from "./components/header"
import { FilterBar } from "./components/filters"
import { MetricCard } from "./components/metric-card"
import { StatsCard } from "./components/stats-card"
import { ChartsSection } from "./components/charts-section"
import { MapVisualization } from "./components/map-visualization"
import {
  OrdersIcon,
  OpenOrdersIcon,
  ClosedOrdersIcon,
  StockIcon,
  ReturnOrdersIcon,
  InwardsIcon,
} from "./components/icons"

export default function Dashboard() {
  const metrics = [
    { title: "Total Orders", value: "57", icon: <OrdersIcon />, color: "green" as const },
    { title: "Open Orders", value: "24", icon: <OpenOrdersIcon />, color: "blue" as const },
    { title: "Closed Orders", value: "33", icon: <ClosedOrdersIcon />, color: "green" as const },
    { title: "Stock Value", value: "₹15.23k", icon: <StockIcon />, color: "purple" as const },
    { title: "Return Orders", value: "05", icon: <ReturnOrdersIcon />, color: "yellow" as const },
    { title: "Inwards", value: "01", icon: <InwardsIcon />, color: "blue" as const },
  ]

  const stats = [
    { title: "Total Hospitals", value: "28,900" },
    { title: "Near Expiry Products", value: "250" },
    { title: "Total Outstanding Amount", value: "₹10,20,000" },
  ]

  return (
    <div className="p-6">
      <Header />
      <FilterBar />

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        {metrics.map((metric) => (
          <MetricCard key={metric.title} {...metric} />
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {stats.map((stat) => (
          <StatsCard key={stat.title} {...stat} />
        ))}
      </div>

      <ChartsSection />
      <MapVisualization />
    </div>
  )
}
