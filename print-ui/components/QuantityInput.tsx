'use client'

interface QuantityInputProps {
  value: number
  onChange: (qty: number) => void
  min?: number
  max?: number
}

/**
 * Quantity input with increment/decrement buttons.
 */
export function QuantityInput({
  value,
  onChange,
  min = 1,
  max = 100,
}: QuantityInputProps) {
  const decrement = () => onChange(Math.max(min, value - 1))
  const increment = () => onChange(Math.min(max, value + 1))

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const num = parseInt(e.target.value, 10)
    if (!isNaN(num)) {
      onChange(Math.max(min, Math.min(max, num)))
    }
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Quantity
      </label>
      <div className="flex items-center">
        <button
          type="button"
          onClick={decrement}
          disabled={value <= min}
          className="px-4 py-2 border border-gray-300 rounded-l-lg bg-gray-50 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed text-xl font-medium"
        >
          -
        </button>
        <input
          type="number"
          value={value}
          onChange={handleChange}
          min={min}
          max={max}
          className="w-20 px-3 py-2 border-y border-gray-300 text-center text-lg font-medium focus:ring-2 focus:ring-alliance-purple focus:border-transparent"
        />
        <button
          type="button"
          onClick={increment}
          disabled={value >= max}
          className="px-4 py-2 border border-gray-300 rounded-r-lg bg-gray-50 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed text-xl font-medium"
        >
          +
        </button>
      </div>
      <p className="mt-1 text-xs text-gray-500">
        Labels to print ({min}-{max})
      </p>
    </div>
  )
}
