import { DatabaseSync } from 'node:sqlite';
const db = new DatabaseSync('db.sqlite3');

const sec = db.prepare("SELECT image, image_type, count(*) as c FROM vehicles_vehicleimage GROUP BY image_type").all();
console.log('Vehicle image types:', sec);

const sampleSec = db.prepare("SELECT v.model, vi.image_type, vi.image FROM vehicles_vehicleimage vi JOIN vehicles_vehicle v ON vi.vehicle_id = v.id WHERE vi.is_primary = 0 LIMIT 15").all();
console.log('Sample secondary:', sampleSec);
