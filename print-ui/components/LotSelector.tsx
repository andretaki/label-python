'use client'

import { getMonthOptions, getRunLetterOptions, parseLotNumber } from '@/lib/lot'

interface LotSelectorProps {
  value: string
  onChange: (lot: string) => void
}

/**
 * Lot number selector with dropdowns for month, year, run letter, and location.
 * Format: MMYYAL (e.g., 0126AL = January 2026, Run A, Location L)
 */
export function LotSelector({ value, onChange }: LotSelectorProps) {
  const parsed = parseLotNumber(value)
  const now = new Date()

  const month = parsed?.month ?? now.getMonth() + 1
  const year = parsed?.year ?? now.getFullYear()
  const runLetter = parsed?.runLetter ?? 'A'
  const location = parsed?.location ?? 'L'

  const updateLot = (
    newMonth: number,
    newYear: number,
    newRun: string,
    newLoc: string
  ) => {
    const m = String(newMonth).padStart(2, '0')
    const y = String(newYear).slice(-2)
    onChange(`${m}${y}${newRun}${newLoc}`)
  }

  const monthOptions = getMonthOptions()
  const runOptions = getRunLetterOptions()

  // Year options: current year +/- 1
  const yearOptions = [year - 1, year, year + 1].map((y) => ({
    value: y,
    label: String(y),
  }))

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Lot Number
      </label>
      <div className="flex gap-2">
        {/* Month */}
        <select
          value={month}
          onChange={(e) => updateLot(parseInt(e.target.value), year, runLetter, location)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-alliance-purple focus:border-transparent"
        >
          {monthOptions.map((opt) => (
            <option key={opt.value} value={parseInt(opt.value)}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Year */}
        <select
          value={year}
          onChange={(e) => updateLot(month, parseInt(e.target.value), runLetter, location)}
          className="w-24 px-3 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-alliance-purple focus:border-transparent"
        >
          {yearOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Run Letter */}
        <select
          value={runLetter}
          onChange={(e) => updateLot(month, year, e.target.value, location)}
          className="w-20 px-3 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-alliance-purple focus:border-transparent"
        >
          {runOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Location (fixed to L for now) */}
        <div className="w-12 px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-center text-gray-600">
          L
        </div>
      </div>
      <p className="mt-1 text-xs text-gray-500">
        Format: {value} (MMYYAL)
      </p>
    </div>
  )
}
