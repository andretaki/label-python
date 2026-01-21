'use client'

import { useState, useEffect, useCallback } from 'react'
import { generateDefaultLot, isValidLotNumber } from '@/lib/lot'
import { printLabel } from '@/lib/agent'
import { LotSelector } from './LotSelector'
import { QuantityInput } from './QuantityInput'
import { PrintButton } from './PrintButton'

interface Product {
  sku: string
  productName: string
  gradeOrConcentration?: string
  upcGtin12: string
  hazcomApplicable: boolean
}

/**
 * Main product search component with barcode scanning support.
 * Auto-submits when a 12-digit UPC is entered (barcode scanner behavior).
 */
export function ProductSearch() {
  const [query, setQuery] = useState('')
  const [product, setProduct] = useState<Product | null>(null)
  const [lotNumber, setLotNumber] = useState(generateDefaultLot())
  const [quantity, setQuantity] = useState(1)
  const [loading, setLoading] = useState(false)
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [searchResults, setSearchResults] = useState<Product[]>([])

  // Search for products by name or UPC
  const searchProducts = useCallback(async (searchQuery: string) => {
    if (!searchQuery || searchQuery.length < 2) {
      setSearchResults([])
      return
    }

    setSearching(true)
    try {
      // Check if it's a UPC (12 digits)
      const isUpc = /^\d{12}$/.test(searchQuery)
      const endpoint = isUpc
        ? `/api/products?upc=${searchQuery}`
        : `/api/products?q=${encodeURIComponent(searchQuery)}`

      const res = await fetch(endpoint)
      if (!res.ok) throw new Error('Search failed')

      const data = await res.json()

      if (isUpc && data) {
        // UPC lookup returns single product - select it immediately
        setProduct(data)
        setSearchResults([])
        setQuery(data.productName)
      } else if (Array.isArray(data)) {
        setSearchResults(data)
      }
    } catch {
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }, [])

  // Debounced search on query change
  useEffect(() => {
    // Auto-search when 12 digits entered (barcode scanner)
    if (/^\d{12}$/.test(query)) {
      searchProducts(query)
      return
    }

    // Debounce text search
    const timer = setTimeout(() => {
      if (query.length >= 2) {
        searchProducts(query)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [query, searchProducts])

  // Select a product from search results
  const selectProduct = (p: Product) => {
    setProduct(p)
    setQuery(p.productName)
    setSearchResults([])
    setError(null)
  }

  // Handle print
  const handlePrint = async () => {
    if (!product) {
      setError('Please select a product first')
      return
    }

    if (!isValidLotNumber(lotNumber)) {
      setError('Invalid lot number format (MMYYAL)')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await printLabel({
        sku: product.sku,
        lot_number: lotNumber,
        quantity,
      })

      if (result.success) {
        setSuccess(`Printed ${quantity} label(s) for ${product.sku}`)
        // Log to database
        await fetch('/api/print', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sku: product.sku,
            productName: product.productName,
            lotNumber,
            quantity,
            status: 'success',
            jobId: result.job_id,
          }),
        })
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Print failed'
      setError(message)
      // Log failure
      await fetch('/api/print', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sku: product.sku,
          productName: product.productName,
          lotNumber,
          quantity,
          status: 'failed',
          errorMessage: message,
        }),
      })
    } finally {
      setLoading(false)
    }
  }

  // Clear selection
  const clearProduct = () => {
    setProduct(null)
    setQuery('')
    setSearchResults([])
    setError(null)
    setSuccess(null)
  }

  return (
    <div className="space-y-6">
      {/* Product Search */}
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Product (search or scan barcode)
        </label>
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              if (product) setProduct(null)
            }}
            placeholder="Enter product name or scan UPC..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-alliance-purple focus:border-transparent text-lg"
            autoFocus
          />
          {searching && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <div className="w-5 h-5 border-2 border-alliance-purple border-t-transparent rounded-full animate-spin" />
            </div>
          )}
        </div>

        {/* Search Results Dropdown */}
        {searchResults.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
            {searchResults.map((p) => (
              <button
                key={p.sku}
                onClick={() => selectProduct(p)}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-0"
              >
                <div className="font-medium text-gray-900">{p.productName}</div>
                <div className="text-sm text-gray-500 flex gap-4">
                  <span>SKU: {p.sku}</span>
                  {p.gradeOrConcentration && <span>{p.gradeOrConcentration}</span>}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected Product Display */}
      {product && (
        <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-between">
          <div>
            <div className="font-semibold text-lg text-gray-900">{product.productName}</div>
            <div className="text-sm text-gray-600 flex gap-4">
              <span>SKU: {product.sku}</span>
              {product.gradeOrConcentration && <span>{product.gradeOrConcentration}</span>}
              {product.hazcomApplicable && (
                <span className="text-orange-600 font-medium">HazCom</span>
              )}
            </div>
          </div>
          <button
            onClick={clearProduct}
            className="text-gray-400 hover:text-gray-600 p-2"
            title="Clear selection"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Lot Number and Quantity Row */}
      <div className="grid grid-cols-2 gap-6">
        <LotSelector value={lotNumber} onChange={setLotNumber} />
        <QuantityInput value={quantity} onChange={setQuantity} />
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-700">
          {success}
        </div>
      )}

      {/* Print Button */}
      <PrintButton
        onClick={handlePrint}
        loading={loading}
        disabled={!product || loading}
      />
    </div>
  )
}
