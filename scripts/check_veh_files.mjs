import fs from 'node:fs';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';

const BASE_DIR = process.cwd();
const DB_PATH = path.join(BASE_DIR, 'db.sqlite3');
const db = new DatabaseSync(DB_PATH);

const vehicles = db.prepare("SELECT v.id, b.name as brand, v.model, vi.image FROM vehicles_vehicle v JOIN vehicles_brand b ON v.brand_id = b.id LEFT JOIN vehicles_vehicleimage vi ON vi.vehicle_id = v.id AND vi.is_primary = 1 ORDER BY v.id").all();

let missingCount = 0;
let existingCount = 0;
for (const v of vehicles) {
  if (!v.image) {
    missingCount++;
  } else {
    const fullPath = path.join(BASE_DIR, 'media', v.image);
    if (!fs.existsSync(fullPath)) {
      missingCount++;
    } else {
      existingCount++;
    }
  }
}
console.log(`Vehicles: ${vehicles.length} total. Existing real files: ${existingCount}, Missing files: ${missingCount}`);

// Let's also check secondary images:
const allVehImgs = db.prepare("SELECT vi.id, vi.image, vi.is_primary FROM vehicles_vehicleimage vi").all();
let secMissing = 0;
let secExisting = 0;
for (const img of allVehImgs) {
  if (!img.image) {
    secMissing++;
  } else {
    const p = path.join(BASE_DIR, 'media', img.image);
    if (!fs.existsSync(p)) {
      secMissing++;
    } else {
      secExisting++;
    }
  }
}
console.log(`Vehicle Images in DB: ${allVehImgs.length}. File exists: ${secExisting}, File missing: ${secMissing}`);
