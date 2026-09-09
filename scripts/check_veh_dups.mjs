import { DatabaseSync } from 'node:sqlite';
const db = new DatabaseSync('db.sqlite3');

const vehImgs = db.prepare("SELECT vi.image, vi.source_url, v.id, b.name as brand, v.model FROM vehicles_vehicleimage vi JOIN vehicles_vehicle v ON vi.vehicle_id = v.id JOIN vehicles_brand b ON v.brand_id = b.id WHERE vi.is_primary = 1").all();
const urls = new Set();
const dups = [];
for (const v of vehImgs) {
  if (urls.has(v.source_url)) {
    dups.push(v);
  } else if (v.source_url) {
    urls.add(v.source_url);
  }
}
console.log(`Vehicles primary images: ${vehImgs.length}, unique source URLs: ${urls.size}, duplicates: ${dups.length}`);
