#!/usr/bin/env node
/**
 * Sync Shopify product variants to Neon PostgreSQL.
 * Merges with chemical hazmat data from data/chemicals/*.json
 *
 * Usage:
 *   node scripts/sync-shopify.mjs
 *
 * Reads from ../.env for credentials
 */

import { neon } from '@neondatabase/serverless';
import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = join(__dirname, '..', '..');

// Load .env from project root
function loadEnv() {
  const envPath = join(ROOT_DIR, '.env');
  if (!existsSync(envPath)) {
    console.error('No .env file found at:', envPath);
    process.exit(1);
  }
  const content = readFileSync(envPath, 'utf-8');
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const match = trimmed.match(/^([^=]+)=["']?(.+?)["']?$/);
    if (match) {
      process.env[match[1]] = match[2];
    }
  }
}

loadEnv();

// Also load print-ui/.env.local for DATABASE_URL
const envLocalPath = join(__dirname, '..', '.env.local');
if (existsSync(envLocalPath)) {
  const content = readFileSync(envLocalPath, 'utf-8');
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const match = trimmed.match(/^([^=]+)=["']?(.+?)["']?$/);
    if (match && !process.env[match[1]]) {
      process.env[match[1]] = match[2];
    }
  }
}

const SHOPIFY_STORE = process.env.SHOPIFY_STORE;
const SHOPIFY_ACCESS_TOKEN = process.env.SHOPIFY_ACCESS_TOKEN;
const DATABASE_URL = process.env.DATABASE_URL;
const API_VERSION = '2024-01';

if (!SHOPIFY_STORE || !SHOPIFY_ACCESS_TOKEN || !DATABASE_URL) {
  console.error('Missing required environment variables:');
  if (!SHOPIFY_STORE) console.error('  - SHOPIFY_STORE');
  if (!SHOPIFY_ACCESS_TOKEN) console.error('  - SHOPIFY_ACCESS_TOKEN');
  if (!DATABASE_URL) console.error('  - DATABASE_URL');
  process.exit(1);
}

const sql = neon(DATABASE_URL);

// Load chemical hazmat data
function loadChemicals() {
  const chemDir = join(ROOT_DIR, 'data', 'chemicals');
  if (!existsSync(chemDir)) {
    console.warn('No chemicals directory found at:', chemDir);
    return new Map();
  }

  const chemicals = new Map();
  for (const file of readdirSync(chemDir)) {
    if (!file.endsWith('.json')) continue;
    try {
      const data = JSON.parse(readFileSync(join(chemDir, file), 'utf-8'));
      chemicals.set(data.chemical_id, data);
      // Also index by name and aliases for matching
      const nameLower = data.chemical_name.toLowerCase();
      chemicals.set(nameLower, data);
      for (const alias of data.aliases || []) {
        chemicals.set(alias.toLowerCase(), data);
      }
    } catch (e) {
      console.warn(`Failed to load ${file}:`, e.message);
    }
  }
  return chemicals;
}

// Load SKU mappings
function loadSkuMappings() {
  const mappingPath = join(ROOT_DIR, 'data', 'sku_mappings.json');
  if (!existsSync(mappingPath)) {
    return { mappings: [], prefix_rules: [] };
  }
  return JSON.parse(readFileSync(mappingPath, 'utf-8'));
}

// Match product to chemical by name or SKU
function matchChemical(productName, sku, chemicals, skuMappings) {
  // 1. Try exact SKU mapping
  for (const m of skuMappings.mappings || []) {
    if (sku === m.sku_pattern) {
      return chemicals.get(m.chemical_id);
    }
  }

  // 2. Try SKU prefix rules
  for (const rule of skuMappings.prefix_rules || []) {
    if (sku.startsWith(rule.prefix)) {
      return chemicals.get(rule.chemical_id);
    }
  }

  // 3. Try product name matching
  const nameLower = productName.toLowerCase();

  // Check for exact name match first
  if (chemicals.has(nameLower)) {
    return chemicals.get(nameLower);
  }

  // Check if product name contains chemical name
  for (const [key, chem] of chemicals) {
    if (typeof key === 'string' && nameLower.includes(key)) {
      return chem;
    }
  }

  return null;
}

// Size parsing patterns
const SIZE_PATTERNS = [
  /(\d+(?:\.\d+)?)\s*(gal(?:lon)?s?)/i,
  /(\d+(?:\.\d+)?)\s*(l(?:iter)?s?)/i,
  /(\d+(?:\.\d+)?)\s*(ml|milliliters?)/i,
  /(\d+(?:\.\d+)?)\s*(oz|ounces?|fl\.?\s*oz)/i,
  /(\d+(?:\.\d+)?)\s*(lb|lbs?|pounds?)/i,
  /(\d+(?:\.\d+)?)\s*(kg|kilograms?)/i,
  /(\d+(?:\.\d+)?)\s*(g|grams?)/i,
];

function parseSize(text) {
  for (const pattern of SIZE_PATTERNS) {
    const match = text.match(pattern);
    if (match) {
      const qty = parseFloat(match[1]);
      const unit = match[2].toLowerCase();

      if (unit.startsWith('gal')) {
        return { us: `${qty} Gallon${qty !== 1 ? 's' : ''}`, metric: `${(qty * 3.785).toFixed(2)} L` };
      }
      if (unit === 'l' || unit.startsWith('liter')) {
        return { us: `${(qty * 0.264).toFixed(2)} Gal`, metric: `${qty} L` };
      }
      if (unit === 'ml' || unit.startsWith('milli')) {
        return { us: `${(qty * 0.034).toFixed(1)} fl oz`, metric: `${qty} mL` };
      }
      if (unit.includes('oz')) {
        return { us: `${qty} fl oz`, metric: `${(qty * 29.57).toFixed(0)} mL` };
      }
      if (unit === 'lb' || unit.startsWith('lb') || unit.startsWith('pound')) {
        return { us: `${qty} lb`, metric: `${(qty * 0.454).toFixed(2)} kg` };
      }
      if (unit === 'kg' || unit.startsWith('kilo')) {
        return { us: `${(qty * 2.205).toFixed(2)} lb`, metric: `${qty} kg` };
      }
      if (unit === 'g' || unit.startsWith('gram')) {
        return { us: `${(qty * 0.035).toFixed(2)} oz`, metric: `${qty} g` };
      }
    }
  }
  return null;
}

function normalizeUpc(barcode) {
  if (!barcode) return null;
  const digits = barcode.replace(/\D/g, '');
  if (digits.length === 12) return digits;
  if (digits.length === 13) return digits.slice(1);
  return null;
}

function getPackageType(sizeText) {
  const lower = sizeText.toLowerCase();
  if (lower.includes('drum') || lower.includes('55 gal')) return 'Drum';
  if (lower.includes('tote') || lower.includes('275 gal') || lower.includes('330 gal')) return 'Tote';
  if (lower.includes('pail') || lower.includes('5 gal')) return 'Pail';
  if (lower.includes('jug') || lower.includes('1 gal')) return 'Jug';
  if (lower.includes('bottle')) return 'Bottle';
  if (lower.includes('bag')) return 'Bag';
  return 'Container';
}

async function fetchShopifyProducts() {
  const products = [];
  let nextUrl = `https://${SHOPIFY_STORE}/admin/api/${API_VERSION}/products.json?limit=250&fields=id,title,variants,options,product_type,tags`;

  while (nextUrl) {
    console.log(`Fetching: ${nextUrl.split('?')[0]}...`);

    const response = await fetch(nextUrl, {
      headers: {
        'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Shopify API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    products.push(...(data.products || []));

    const linkHeader = response.headers.get('Link') || '';
    const nextMatch = linkHeader.match(/<([^>]+)>;\s*rel="next"/);
    nextUrl = nextMatch ? nextMatch[1] : null;
  }

  return products;
}

async function syncToDatabase(products, chemicals, skuMappings) {
  let synced = 0;
  let skipped = 0;
  let withHazmat = 0;
  let errors = [];

  for (const product of products) {
    const productName = product.title?.trim();
    if (!productName) continue;

    for (const variant of product.variants || []) {
      const sku = variant.sku?.trim();
      if (!sku) {
        skipped++;
        continue;
      }

      let variantTitle = variant.title?.trim() || '';
      if (variantTitle.toLowerCase() === 'default title') variantTitle = '';

      const sizeSource = variantTitle || productName || sku;
      const size = parseSize(sizeSource);

      if (!size) {
        errors.push({ sku, reason: 'no size' });
        skipped++;
        continue;
      }

      const upc = normalizeUpc(variant.barcode);
      if (!upc) {
        errors.push({ sku, reason: 'no UPC' });
        skipped++;
        continue;
      }

      // Match to chemical for hazmat data
      const chemical = matchChemical(productName, sku, chemicals, skuMappings);

      let grade = '';
      const options = product.options || [];
      for (let i = 0; i < options.length; i++) {
        const optName = (options[i].name || '').toLowerCase();
        const optValue = variant[`option${i + 1}`] || '';
        if (optName.includes('grade') || optName.includes('concentration') || optName.includes('purity')) {
          grade = optValue;
          break;
        }
      }

      const packageType = getPackageType(sizeSource);
      const productFamily = chemical?.product_family || 'specialty';

      try {
        await sql`
          INSERT INTO products (
            sku, product_name, grade_or_concentration, product_family,
            package_type, net_contents_us, net_contents_metric,
            upc_gtin12, cas_number,
            hazcom_applicable, ghs_pictograms, signal_word,
            hazard_statements, precaution_statements,
            dot_regulated, un_number, proper_shipping_name, hazard_class, packing_group,
            nfpa_health, nfpa_fire, nfpa_reactivity, nfpa_special,
            sds_url
          ) VALUES (
            ${sku}, ${productName}, ${grade || chemical?.grade || null}, ${productFamily},
            ${packageType}, ${size.us}, ${size.metric},
            ${upc}, ${chemical?.cas_number || null},
            ${chemical?.hazcom_applicable ?? false},
            ${chemical?.ghs_pictograms || null},
            ${chemical?.signal_word || null},
            ${chemical?.hazard_statements || null},
            ${chemical?.precaution_statements || null},
            ${chemical?.dot_regulated ?? false},
            ${chemical?.un_number || null},
            ${chemical?.proper_shipping_name || null},
            ${chemical?.hazard_class || null},
            ${chemical?.packing_group || null},
            ${chemical?.nfpa_health ?? null},
            ${chemical?.nfpa_fire ?? null},
            ${chemical?.nfpa_reactivity ?? null},
            ${chemical?.nfpa_special || null},
            ${chemical?.sds_url || null}
          )
          ON CONFLICT (sku) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            grade_or_concentration = EXCLUDED.grade_or_concentration,
            product_family = EXCLUDED.product_family,
            package_type = EXCLUDED.package_type,
            net_contents_us = EXCLUDED.net_contents_us,
            net_contents_metric = EXCLUDED.net_contents_metric,
            upc_gtin12 = EXCLUDED.upc_gtin12,
            cas_number = EXCLUDED.cas_number,
            hazcom_applicable = EXCLUDED.hazcom_applicable,
            ghs_pictograms = EXCLUDED.ghs_pictograms,
            signal_word = EXCLUDED.signal_word,
            hazard_statements = EXCLUDED.hazard_statements,
            precaution_statements = EXCLUDED.precaution_statements,
            dot_regulated = EXCLUDED.dot_regulated,
            un_number = EXCLUDED.un_number,
            proper_shipping_name = EXCLUDED.proper_shipping_name,
            hazard_class = EXCLUDED.hazard_class,
            packing_group = EXCLUDED.packing_group,
            nfpa_health = EXCLUDED.nfpa_health,
            nfpa_fire = EXCLUDED.nfpa_fire,
            nfpa_reactivity = EXCLUDED.nfpa_reactivity,
            nfpa_special = EXCLUDED.nfpa_special,
            sds_url = EXCLUDED.sds_url,
            updated_at = NOW()
        `;
        synced++;
        if (chemical) withHazmat++;

        const hazFlag = chemical ? ' [HAZMAT]' : '';
        console.log(`✓ ${sku} - ${productName} (${size.us})${hazFlag}`);
      } catch (err) {
        errors.push({ sku, reason: err.message });
        skipped++;
      }
    }
  }

  return { synced, skipped, withHazmat, errors };
}

async function main() {
  console.log('=== Shopify → Neon Sync ===\n');
  console.log(`Store: ${SHOPIFY_STORE}`);

  // Load chemical data
  console.log('\nLoading chemical hazmat data...');
  const chemicals = loadChemicals();
  console.log(`Loaded ${chemicals.size / 3} chemicals (with aliases)\n`);

  const skuMappings = loadSkuMappings();
  console.log(`Loaded ${skuMappings.prefix_rules?.length || 0} SKU prefix rules\n`);

  try {
    const products = await fetchShopifyProducts();
    console.log(`\nFetched ${products.length} products from Shopify\n`);

    const { synced, skipped, withHazmat, errors } = await syncToDatabase(products, chemicals, skuMappings);

    console.log('\n=== Summary ===');
    console.log(`Synced: ${synced}`);
    console.log(`With hazmat data: ${withHazmat}`);
    console.log(`Skipped: ${skipped}`);

    if (errors.length > 0 && errors.length <= 10) {
      console.log('\nSkipped:');
      for (const err of errors) {
        console.log(`  ${err.sku}: ${err.reason}`);
      }
    } else if (errors.length > 10) {
      console.log(`\n${errors.length} skipped (no size or UPC)`);
    }

    const count = await sql`SELECT COUNT(*) as count FROM products`;
    const hazCount = await sql`SELECT COUNT(*) as count FROM products WHERE hazcom_applicable = true`;
    console.log(`\nTotal products: ${count[0].count}`);
    console.log(`With hazcom data: ${hazCount[0].count}`);

  } catch (err) {
    console.error('Sync failed:', err.message);
    process.exit(1);
  }
}

main();
