import { NextRequest, NextResponse } from 'next/server'
import { db, products } from '@/lib/db'
import { eq, ilike, or } from 'drizzle-orm'

/**
 * GET /api/products
 *
 * Search products by name or lookup by UPC.
 *
 * Query params:
 * - q: Search query (partial match on product name or SKU)
 * - upc: Exact UPC lookup (12 digits)
 */
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const query = searchParams.get('q')
  const upc = searchParams.get('upc')

  try {
    // UPC lookup - return single product
    if (upc) {
      if (!/^\d{12}$/.test(upc)) {
        return NextResponse.json(
          { error: 'Invalid UPC format (must be 12 digits)' },
          { status: 400 }
        )
      }

      const [product] = await db
        .select()
        .from(products)
        .where(eq(products.upcGtin12, upc))
        .limit(1)

      if (!product) {
        return NextResponse.json(
          { error: 'Product not found' },
          { status: 404 }
        )
      }

      return NextResponse.json(product)
    }

    // Text search - return array of matches
    if (query && query.length >= 2) {
      const searchPattern = `%${query}%`

      const results = await db
        .select({
          sku: products.sku,
          productName: products.productName,
          gradeOrConcentration: products.gradeOrConcentration,
          upcGtin12: products.upcGtin12,
          hazcomApplicable: products.hazcomApplicable,
        })
        .from(products)
        .where(
          or(
            ilike(products.productName, searchPattern),
            ilike(products.sku, searchPattern)
          )
        )
        .limit(10)

      return NextResponse.json(results)
    }

    // No query - return empty array
    return NextResponse.json([])

  } catch (error) {
    console.error('Product search error:', error)
    return NextResponse.json(
      { error: 'Database error' },
      { status: 500 }
    )
  }
}
