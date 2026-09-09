import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

const BASE_DIR = process.cwd();
const DB_PATH = path.join(BASE_DIR, 'db.sqlite3');
const db = new DatabaseSync(DB_PATH);

const vehicles = db.prepare(`
  SELECT v.id, b.name as brand, v.model, vi.image, vi.source, vi.source_url
  FROM vehicles_vehicle v
  JOIN vehicles_brand b ON v.brand_id = b.id
  LEFT JOIN vehicles_vehicleimage vi ON vi.vehicle_id = v.id AND vi.is_primary = 1
  ORDER BY v.id
`).all();

console.log('Vehicles total:', vehicles.length);
let placeholderVehicles = 0;
for (const v of vehicles) {
  if (!v.image || v.image.includes('placeholder') || v.image.endsWith('.svg')) {
    placeholderVehicles++;
    console.log('Placeholder vehicle:', v.brand, v.model, v.image);
  }
}
console.log('Placeholder vehicles count:', placeholderVehicles);

// Let's sample 5 vehicles and their sources
console.log('Sample vehicle sources:');
vehicles.slice(0, 5).forEach(v => console.log(v.brand, v.model, '->', v.image, '| source:', v.source));
