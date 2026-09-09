import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

const BASE_DIR = process.cwd();
const DB_PATH = path.join(BASE_DIR, 'db.sqlite3');
const db = new DatabaseSync(DB_PATH);

console.log('--- VEHICLE IMAGES SAMPLE ---');
const sampleVehImgs = db.prepare("SELECT id, vehicle_id, image, image_type, license_status FROM vehicles_vehicleimage LIMIT 10").all();
console.log(sampleVehImgs);

const vehWithReal = db.prepare("SELECT count(DISTINCT vehicle_id) as count FROM vehicles_vehicleimage WHERE license_status = 'REAL_PHOTO'").get();
console.log('Vehicles with REAL_PHOTO:', vehWithReal.count);

console.log('--- PRODUCT IMAGES (SPARE PARTS) ---');
const prodImgsCount = db.prepare("SELECT count(*) as count FROM products_productimage").get();
console.log('Total Product Images:', prodImgsCount.count);

const svgProdCount = db.prepare("SELECT count(*) as count FROM products_productimage WHERE image LIKE '%.svg'").get();
console.log('Product Images with .svg:', svgProdCount.count);

const sampleProdImgs = db.prepare("SELECT pi.id, pi.product_id, p.name, pi.image, pi.image_type FROM products_productimage pi JOIN products_product p ON pi.product_id = p.id LIMIT 10").all();
console.log(sampleProdImgs);

console.log('--- SERVICES ---');
const servicesCount = db.prepare("SELECT count(*) as count FROM services_service").get();
console.log('Total Services:', servicesCount.count);
const sampleServices = db.prepare("SELECT id, name, image FROM services_service LIMIT 10").all();
console.log(sampleServices);
