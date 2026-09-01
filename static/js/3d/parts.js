/**
 * 3D AUTOMOTIVE STUDIO — PARTS SWAPPER & PROCEDURAL GENERATOR
 * Handles dynamically attaching and replacing 3D components
 * (Wheels, Spoilers, Diffusers, Grilles, Exhausts).
 */

class PartsManager {
  constructor(scene, materialManager) {
    this.scene = scene;
    this.materials = materialManager;
    this.slots = {
      wheels: [],
      spoiler: null,
      diffuser: null,
      front_splitter: null,
    };
  }

  createProceduralWheel(radius = 0.38, width = 0.24, rimStyle = 'multi_spoke', finishMat = null) {
    const wheelGroup = new THREE.Group();
    const rimMat = finishMat || this.materials.chromeMaterial;

    // Outer Tyre Rubber
    const tyreGeo = new THREE.CylinderGeometry(radius, radius, width, 32);
    const tyre = new THREE.Mesh(tyreGeo, this.materials.rubberMaterial);
    tyre.rotation.z = Math.PI / 2;
    tyre.castShadow = true;
    wheelGroup.add(tyre);

    // Rim Outer Barrel
    const rimRadius = radius * 0.76;
    const rimGeo = new THREE.CylinderGeometry(rimRadius, rimRadius, width + 0.01, 32, 1, true);
    const rim = new THREE.Mesh(rimGeo, rimMat);
    rim.rotation.z = Math.PI / 2;
    wheelGroup.add(rim);

    // Spokes & Center Hub
    const hubGeo = new THREE.CylinderGeometry(rimRadius * 0.28, rimRadius * 0.28, width + 0.02, 16);
    const hub = new THREE.Mesh(hubGeo, rimMat);
    hub.rotation.z = Math.PI / 2;
    wheelGroup.add(hub);

    const numSpokes = rimStyle === '5_spoke' ? 5 : (rimStyle === 'mesh' ? 10 : 8);
    for (let i = 0; i < numSpokes; i++) {
      const angle = (i / numSpokes) * Math.PI * 2;
      const spokeGeo = new THREE.BoxGeometry(width + 0.02, rimRadius * 0.6, 0.035);
      const spoke = new THREE.Mesh(spokeGeo, rimMat);
      spoke.position.set(0, Math.sin(angle) * (rimRadius * 0.45), Math.cos(angle) * (rimRadius * 0.45));
      spoke.rotation.x = angle;
      wheelGroup.add(spoke);
    }

    // Steel Brake Disc Rotor inside
    const rotorGeo = new THREE.CylinderGeometry(rimRadius * 0.72, rimRadius * 0.72, 0.02, 24);
    const rotor = new THREE.Mesh(rotorGeo, this.materials.rotorSteelMaterial);
    rotor.rotation.z = Math.PI / 2;
    wheelGroup.add(rotor);

    // Red Brembo Brake Caliper
    const caliperGeo = new THREE.BoxGeometry(0.06, rimRadius * 0.4, 0.08);
    const caliper = new THREE.Mesh(caliperGeo, this.materials.caliperRedMaterial);
    caliper.position.set(0, rimRadius * 0.45, 0);
    wheelGroup.add(caliper);

    return wheelGroup;
  }

  createSpoiler(type = 'gt_wing') {
    const spoilerGroup = new THREE.Group();
    const carbonMat = this.materials.carbonFiberMaterial;

    if (type === 'ducktail') {
      const lipGeo = new THREE.BoxGeometry(1.3, 0.05, 0.18);
      const lip = new THREE.Mesh(lipGeo, carbonMat);
      lip.position.set(0, 1.02, -1.8);
      lip.rotation.x = -0.2;
      spoilerGroup.add(lip);
    } else {
      // GT Wing with Endplates and Dual Upright Mounts
      const wingGeo = new THREE.BoxGeometry(1.45, 0.04, 0.28);
      const wing = new THREE.Mesh(wingGeo, carbonMat);
      wing.position.set(0, 1.25, -1.85);
      wing.castShadow = true;
      spoilerGroup.add(wing);

      // Left & Right Mounts
      const mountGeo = new THREE.BoxGeometry(0.03, 0.28, 0.12);
      const leftMount = new THREE.Mesh(mountGeo, this.materials.glossBlackMaterial);
      leftMount.position.set(-0.45, 1.1, -1.85);
      const rightMount = new THREE.Mesh(mountGeo, this.materials.glossBlackMaterial);
      rightMount.position.set(0.45, 1.1, -1.85);
      spoilerGroup.add(leftMount);
      spoilerGroup.add(rightMount);

      // Carbon Endplates
      const endplateGeo = new THREE.BoxGeometry(0.02, 0.16, 0.32);
      const leftEnd = new THREE.Mesh(endplateGeo, carbonMat);
      leftEnd.position.set(-0.73, 1.25, -1.85);
      const rightEnd = new THREE.Mesh(endplateGeo, carbonMat);
      rightEnd.position.set(0.73, 1.25, -1.85);
      spoilerGroup.add(leftEnd);
      spoilerGroup.add(rightEnd);
    }

    return spoilerGroup;
  }
}

window.PartsManager = PartsManager;
