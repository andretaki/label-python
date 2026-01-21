import { ProductSearch } from '@/components/ProductSearch'
import { AgentStatus } from '@/components/AgentStatus'

export default function PrintPage() {
  return (
    <div className="space-y-8">
      {/* Status bar */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Print Labels</h2>
        <AgentStatus />
      </div>

      {/* Main print interface */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <ProductSearch />
      </div>

      {/* Quick help */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
        <p className="font-medium mb-1">Quick Start</p>
        <ul className="list-disc list-inside space-y-1 text-blue-700">
          <li>Search by product name or scan a UPC barcode</li>
          <li>Lot number auto-fills to current month (MMYYAL format)</li>
          <li>Click Print to send labels directly to the printer</li>
        </ul>
      </div>
    </div>
  )
}
