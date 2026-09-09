import { DatabaseSync } from 'node:sqlite';
const db = new DatabaseSync('db.sqlite3');

const allVehImgs = db.prepare("SELECT id, vehicle_id, image, image_type, license_status FROM vehicles_vehicleimage").all();
console.log('Total vehicle images:', allVehImgs.length);
const svgVeh = allVehImgs.filter(i => i.image && i.image.endsWith('.svg'));
console.log('Vehicle images with .svg:', svgVeh.length);

const allProdImgs = db.prepare("SELECT id, product_id, image, image_type FROM products_productimage").all();
console.log('Total product images:', allProdImgs.length);
const svgProd = allProdImgs.filter(i => i.image && i.image.endsWith('.svg'));
console.log('Product images with .svg:', svgProd.length);

const allServices = db.prepare("SELECT id, name, image FROM services_service").all();
console.log('Total services:', allServices.length);
const svgServ = allServices.filter(s => s.image && s.image.endsWith('.svg'));
console.log('Services with .svg:', svgServ.length);

// Check if any offers have svg
const allOffers = db.prepare("SELECT id, title, banner_image FROM offers_offer").all();
console.log('Total offers:', allOffers.length);
const svgOffers = allOffers.filter(o => o.banner_image && o.banner_image.endsWith('.svg'));
console.log('Offers with .svg:', svgOffers.length);
