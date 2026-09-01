/**
 * 3D AUTOMOTIVE STUDIO — MATERIALS & SHADERS
 * Creates PBR Physical Materials with Clearcoat, Metallic flakes,
 * Carbon Fiber weaves, Glass, Chrome, and Rubber.
 */

class MaterialManager {
  constructor() {
    this.materials = {};
    this.initDefaultMaterials();
  }

  initDefaultMaterials() {
    // Default Car Paint: High-Gloss Metallic Red
    this.carBodyPaint = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color('#DC2626'),
      metalness: 0.85,
      roughness: 0.15,
      clearcoat: 1.0,
      clearcoatRoughness: 0.05,
      reflectivity: 0.9,
    });

    // Glass / Windshield
    this.glassMaterial = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color('#0F172A'),
      metalness: 0.1,
      roughness: 0.05,
      transmission: 0.85,
      transparent: true,
      opacity: 0.65,
      ior: 1.5,
    });

    // Mirror Chrome / Liquid Metal
    this.chromeMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#FFFFFF'),
      metalness: 0.98,
      roughness: 0.05,
    });

    // Gloss Black Rims / Trims
    this.glossBlackMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#0A0A0A'),
      metalness: 0.8,
      roughness: 0.2,
    });

    // Satin Bronze
    this.satinBronzeMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#78350F'),
      metalness: 0.75,
      roughness: 0.35,
    });

    // Tyre Rubber
    this.rubberMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#18181B'),
      metalness: 0.1,
      roughness: 0.85,
    });

    // Brembo Red Brake Caliper
    this.caliperRedMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#EF4444'),
      metalness: 0.6,
      roughness: 0.3,
    });

    // Drilled Disc Rotor (Steel)
    this.rotorSteelMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#CBD5E1'),
      metalness: 0.9,
      roughness: 0.25,
    });

    // Headlight LED (Emissive Glow)
    this.ledHeadlightMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#FFFFFF'),
      emissive: new THREE.Color('#E0F2FE'),
      emissiveIntensity: 2.0,
      roughness: 0.1,
    });

    // Taillight LED (Red Glow)
    this.ledTaillightMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#DC2626'),
      emissive: new THREE.Color('#EF4444'),
      emissiveIntensity: 2.5,
      roughness: 0.1,
    });

    // Carbon Fiber Aerokit Material
    this.carbonFiberMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#18181B'),
      metalness: 0.6,
      roughness: 0.4,
    });
  }

  applyPaint(paintData) {
    if (!paintData || !this.carBodyPaint) return;
    
    this.carBodyPaint.color = new THREE.Color(paintData.hex_color || '#DC2626');
    this.carBodyPaint.metalness = paintData.metalness !== undefined ? paintData.metalness : 0.8;
    this.carBodyPaint.roughness = paintData.roughness !== undefined ? paintData.roughness : 0.2;
    this.carBodyPaint.clearcoat = paintData.clearcoat !== undefined ? paintData.clearcoat : 1.0;
    this.carBodyPaint.needsUpdate = true;
  }
}

window.MaterialManager = MaterialManager;
