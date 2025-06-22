interface StatsCardProps {
  title: string
  value: string | number
}

export function StatsCard({ title, value }: StatsCardProps) {
  return (
    <div className="p-6 border rounded-lg">
      <h3 className="text-lg text-gray-600 mb-2">{title}</h3>
      <p className="text-3xl font-semibold">{value}</p>
    </div>
  )
}
