import fs from 'node:fs';
import path from 'node:path';

const sampleFiles = [
  'media/vehicles/photos/maruti-suzuki-swift-real.jpg',
  'media/vehicles/photos/maruti-suzuki-swift-zxi-dual-tone-2025-side.jpg',
  'media/vehicles/photos/maruti-suzuki-swift-zxi-dual-tone-2025-interior.jpg',
  'media/services/gallery/express-foam-wash-vacuum-service.jpg',
  'media/services/gallery/stage-1-paint-gloss-polish-wax-service.jpg'
];

for (const f of sampleFiles) {
  const p = path.join(process.cwd(), f);
  if (fs.existsSync(p)) {
    const stats = fs.statSync(p);
    const head = fs.readFileSync(p, { length: 30 });
    console.log(f, '->', stats.size, 'bytes', '| starts with:', head.toString('ascii').slice(0, 20));
  } else {
    console.log(f, '-> NOT FOUND');
  }
}
