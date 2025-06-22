export function Header() {
  const navItems = [
    { name: "Distributer", active: true },
    { name: "Sales", active: false },
    { name: "Inventory", active: false },
    { name: "Products", active: false },
  ]

  return (
    <header className="flex items-center justify-between mb-6">
      <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
      <nav className="flex gap-4">
        {navItems.map((item) => (
          <button
            key={item.name}
            className={`px-4 py-2 rounded-md transition-colors ${
              item.active ? "bg-blue-500 text-white" : "text-gray-700 hover:bg-gray-100"
            }`}
          >
            {item.name}
          </button>
        ))}
      </nav>
    </header>
  )
}
