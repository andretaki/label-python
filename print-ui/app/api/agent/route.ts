import { NextResponse } from 'next/server'

const AGENT_URL = process.env.PRINT_AGENT_URL || 'http://localhost:8080'

/**
 * GET /api/agent
 *
 * Proxy to print agent health check.
 * This is useful for server-side health checks or when the client
 * can't reach the agent directly.
 */
export async function GET() {
  try {
    const res = await fetch(`${AGENT_URL}/health`, {
      method: 'GET',
      cache: 'no-store',
    })

    if (!res.ok) {
      return NextResponse.json(
        { status: 'offline', error: 'Agent returned error' },
        { status: 503 }
      )
    }

    const health = await res.json()
    return NextResponse.json(health)

  } catch {
    return NextResponse.json(
      { status: 'offline', error: 'Agent unreachable' },
      { status: 503 }
    )
  }
}
