/**
 * Database schema for the Label Print Station.
 *
 * Tables:
 * - products: Product catalog (replaces JSON files)
 * - print_jobs: Audit log of all print operations
 */

import {
  pgTable,
  serial,
  varchar,
  text,
  boolean,
  smallint,
  timestamp,
  uuid,
  integer,
  index,
} from 'drizzle-orm/pg-core'

/**
 * Products table - single source of truth for product data.
 * Replaces the JSON files used by the label renderer.
 */
export const products = pgTable('products', {
  id: serial('id').primaryKey(),
  sku: varchar('sku', { length: 50 }).unique().notNull(),
  productName: varchar('product_name', { length: 255 }).notNull(),
  gradeOrConcentration: varchar('grade_or_concentration', { length: 100 }),
  productFamily: varchar('product_family', { length: 50 }),
  packageType: varchar('package_type', { length: 50 }).notNull(),
  netContentsUs: varchar('net_contents_us', { length: 50 }).notNull(),
  netContentsMetric: varchar('net_contents_metric', { length: 50 }).notNull(),
  casNumber: varchar('cas_number', { length: 20 }),
  upcGtin12: varchar('upc_gtin12', { length: 12 }).unique().notNull(),

  // GHS/HazCom
  hazcomApplicable: boolean('hazcom_applicable').default(false),
  ghsPictograms: text('ghs_pictograms').array(),
  signalWord: varchar('signal_word', { length: 20 }),
  hazardStatements: text('hazard_statements').array(),
  precautionStatements: text('precaution_statements').array(),

  // DOT
  dotRegulated: boolean('dot_regulated').default(false),
  unNumber: varchar('un_number', { length: 10 }),
  properShippingName: varchar('proper_shipping_name', { length: 255 }),
  hazardClass: varchar('hazard_class', { length: 10 }),
  packingGroup: varchar('packing_group', { length: 5 }),

  // NFPA
  nfpaHealth: smallint('nfpa_health'),
  nfpaFire: smallint('nfpa_fire'),
  nfpaReactivity: smallint('nfpa_reactivity'),
  nfpaSpecial: varchar('nfpa_special', { length: 10 }),

  // URLs
  sdsUrl: text('sds_url'),

  // Timestamps
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow(),
}, (table) => [
  index('idx_products_upc').on(table.upcGtin12),
  index('idx_products_sku').on(table.sku),
])

/**
 * Print jobs table - audit log for all print operations.
 * Tracks who printed what, when, and whether it succeeded.
 */
export const printJobs = pgTable('print_jobs', {
  id: uuid('id').primaryKey().defaultRandom(),
  sku: varchar('sku', { length: 50 }).notNull(),
  productName: varchar('product_name', { length: 255 }).notNull(),
  lotNumber: varchar('lot_number', { length: 20 }).notNull(),
  quantity: integer('quantity').notNull(),
  status: varchar('status', { length: 20 }).notNull(), // 'success', 'failed'
  errorMessage: text('error_message'),
  printerName: varchar('printer_name', { length: 100 }),
  printedAt: timestamp('printed_at', { withTimezone: true }).defaultNow(),
  printedBy: varchar('printed_by', { length: 100 }), // Future: operator login
}, (table) => [
  index('idx_print_jobs_date').on(table.printedAt),
  index('idx_print_jobs_sku').on(table.sku),
])

// Type exports for use in application code
export type Product = typeof products.$inferSelect
export type NewProduct = typeof products.$inferInsert
export type PrintJob = typeof printJobs.$inferSelect
export type NewPrintJob = typeof printJobs.$inferInsert
