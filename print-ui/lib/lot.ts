/**
 * Lot number generation utilities.
 *
 * Format: MMYYAL where:
 * - MM = 2-digit month (01-12)
 * - YY = 2-digit year
 * - A = production run letter (A-Z)
 * - L = plant location code (default: L for Taylor)
 */

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

/**
 * Generate a default lot number for today's date.
 * Uses 'A' as run letter and 'L' as location.
 */
export function generateDefaultLot(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const year = String(now.getFullYear()).slice(-2)
  return `${month}${year}AL`
}

/**
 * Parse a lot number into its components.
 */
export function parseLotNumber(lot: string): {
  month: number
  year: number
  runLetter: string
  location: string
} | null {
  const match = lot.match(/^(\d{2})(\d{2})([A-Z])([A-Z])$/)
  if (!match) return null

  return {
    month: parseInt(match[1], 10),
    year: 2000 + parseInt(match[2], 10),
    runLetter: match[3],
    location: match[4],
  }
}

/**
 * Validate a lot number format.
 */
export function isValidLotNumber(lot: string): boolean {
  return /^\d{2}\d{2}[A-Z][A-Z]$/.test(lot) && parseLotNumber(lot) !== null
}

/**
 * Get month options for lot number selector.
 */
export function getMonthOptions(): { value: string; label: string }[] {
  return MONTHS.map((name, i) => ({
    value: String(i + 1).padStart(2, '0'),
    label: name,
  }))
}

/**
 * Get run letter options (A-Z).
 */
export function getRunLetterOptions(): { value: string; label: string }[] {
  return Array.from({ length: 26 }, (_, i) => {
    const letter = String.fromCharCode(65 + i)
    return { value: letter, label: letter }
  })
}
