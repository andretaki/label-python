'use client'

import { useEffect, useState } from 'react'
import { checkAgentHealth, type HealthResponse } from '@/lib/agent'

/**
 * Agent status indicator showing whether the print agent is online.
 * Polls the agent health endpoint every 10 seconds.
 */
export function AgentStatus() {
  const [status, setStatus] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function check() {
      const health = await checkAgentHealth()
      setStatus(health)
      setLoading(false)
    }

    check()
    const interval = setInterval(check, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-gray-500">
        <div className="w-3 h-3 rounded-full bg-gray-300 animate-pulse" />
        <span className="text-sm">Checking printer...</span>
      </div>
    )
  }

  if (!status) {
    return (
      <div className="flex items-center gap-2 text-red-600">
        <div className="w-3 h-3 rounded-full bg-red-500 status-offline" />
        <span className="text-sm font-medium">Agent Offline</span>
      </div>
    )
  }

  const isOk = status.status === 'ok'

  return (
    <div className={`flex items-center gap-2 ${isOk ? 'text-green-600' : 'text-yellow-600'}`}>
      <div className={`w-3 h-3 rounded-full ${isOk ? 'bg-green-500 status-online' : 'bg-yellow-500'}`} />
      <span className="text-sm font-medium">
        {isOk ? 'Ready' : 'Degraded'}
      </span>
      <span className="text-xs text-gray-500">
        {status.printer}
      </span>
    </div>
  )
}
