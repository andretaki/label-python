import { NextRequest, NextResponse } from 'next/server'
import { db, printJobs } from '@/lib/db'
import { desc, eq } from 'drizzle-orm'

/**
 * GET /api/history
 *
 * Get recent print job history.
 *
 * Query params:
 * - limit: Number of records (default 50, max 200)
 * - sku: Filter by SKU
 */
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const limitParam = searchParams.get('limit')
  const skuFilter = searchParams.get('sku')

  const limit = Math.min(parseInt(limitParam || '50', 10), 200)

  try {
    let query = db
      .select()
      .from(printJobs)
      .orderBy(desc(printJobs.printedAt))
      .limit(limit)

    if (skuFilter) {
      query = db
        .select()
        .from(printJobs)
        .where(eq(printJobs.sku, skuFilter))
        .orderBy(desc(printJobs.printedAt))
        .limit(limit)
    }

    const jobs = await query

    return NextResponse.json(jobs)

  } catch (error) {
    console.error('History fetch error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch history' },
      { status: 500 }
    )
  }
}
