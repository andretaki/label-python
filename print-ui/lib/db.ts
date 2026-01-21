/**
 * Database connection using Drizzle ORM with Neon PostgreSQL.
 */

import { neon } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-http'
import * as schema from './schema'

// Create the Neon client
const sql = neon(process.env.DATABASE_URL!)

// Create the Drizzle database instance
export const db = drizzle(sql, { schema })

// Re-export schema for convenience
export * from './schema'
