/**
 * Print agent client for communicating with the local FastAPI print agent.
 */

const AGENT_URL = process.env.NEXT_PUBLIC_PRINT_AGENT_URL || 'http://localhost:8080'

export interface PrintRequest {
  sku: string
  lot_number: string
  quantity: number
}

export interface PrintResponse {
  success: boolean
  message: string
  job_id?: string
  sku?: string
  lot_number?: string
  quantity?: number
}

export interface HealthResponse {
  status: 'ok' | 'degraded'
  printer: string
  agent_version: string
}

/**
 * Check if the print agent is online and responsive.
 */
export async function checkAgentHealth(): Promise<HealthResponse | null> {
  try {
    const res = await fetch(`${AGENT_URL}/health`, {
      method: 'GET',
      cache: 'no-store',
    })
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  }
}

/**
 * Send a print request to the agent.
 */
export async function printLabel(request: PrintRequest): Promise<PrintResponse> {
  const res = await fetch(`${AGENT_URL}/print`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Print failed: ${res.status}`)
  }

  return await res.json()
}
