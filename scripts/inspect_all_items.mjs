import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

const BASE_DIR = process.cwd();
const DB_PATH = path.join(BASE_DIR, 'db.sqlite3');
const db = new DatabaseSync(DB_PATH);

console.log('Vehicles:', db.prepare('SELECT count(*) c FROM vehicles_vehicle').get().c);
console.log('Vehicle Images:', db.prepare('SELECT count(*) c FROM vehicles_vehicleimage').get().c);
console.log('Products (Spare Parts):', db.prepare('SELECT count(*) c FROM products_product').get().c);
console.log('Product Images:', db.prepare('SELECT count(*) c FROM products_productimage').get().c);
console.log('Services:', db.prepare('SELECT count(*) c FROM services_service').get().c);
console.log('Offers:', db.prepare('SELECT count(*) c FROM offers_offer').get().c);

// Check placeholders in Product Images:
const svgProdImgs = db.prepare("SELECT count(*) c FROM products_productimage WHERE image LIKE '%.svg'").get().c;
console.log('Product Images with .svg placeholder:', svgProdImgs);

// Check placeholders in Vehicle Images:
const svgVehImgs = db.prepare("SELECT count(*) c FROM vehicles_vehicleimage WHERE image LIKE '%.svg'").get().c;
console.log('Vehicle Images with .svg placeholder:', svgVehImgs);

// Check placeholders in Services:
const svgServices = db.prepare("SELECT count(*) c FROM services_service WHERE image LIKE '%.svg'").get().c;
console.log('Services with .svg placeholder:', svgServices);

// Check tables with parts
const allTables = db.prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").all();
console.log('All tables:', allTables.map(t => t.name));

// Let's sample some products
const sampleProducts = db.prepare("SELECT id, name, slug, part_type FROM products_product LIMIT 10").all();
console.log('\nSample products:', sampleProducts);
