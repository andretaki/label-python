import { NextRequest, NextResponse } from 'next/server'
import { db, printJobs } from '@/lib/db'

/**
 * POST /api/print
 *
 * Log a print job to the database (audit trail).
 * The actual printing is done directly by the client calling the print agent.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const {
      sku,
      productName,
      lotNumber,
      quantity,
      status,
      errorMessage,
      jobId,
      printerName,
    } = body

    // Validate required fields
    if (!sku || !productName || !lotNumber || !quantity || !status) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Insert print job record
    const [job] = await db
      .insert(printJobs)
      .values({
        sku,
        productName,
        lotNumber,
        quantity,
        status, // 'success' or 'failed'
        errorMessage: errorMessage || null,
        printerName: printerName || null,
        // printedBy will be set once we have auth
      })
      .returning()

    return NextResponse.json({
      success: true,
      jobId: job.id,
    })

  } catch (error) {
    console.error('Print log error:', error)
    return NextResponse.json(
      { error: 'Failed to log print job' },
      { status: 500 }
    )
  }
}
