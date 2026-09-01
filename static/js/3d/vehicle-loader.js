/**
 * 3D AUTOMOTIVE STUDIO — VEHICLE LOADER & REALISTIC MESH BUILDER
 * Constructs realistic procedural vehicles or loads glTF/GLB models.
 */

class VehicleLoader {
  constructor(scene, materialManager, partsManager) {
    this.scene = scene;
    this.materials = materialManager;
    this.parts = partsManager;
    this.currentVehicleGroup = null;
    this.wheels = [];
    this.spoilerMesh = null;
  }

  loadVehicle(vehicleData, paintData, onComplete) {
    // Remove previous vehicle if any
    if (this.currentVehicleGroup) {
      this.scene.remove(this.currentVehicleGroup);
      this.currentVehicleGroup = null;
      this.wheels = [];
      this.spoilerMesh = null;
    }

    const group = new THREE.Group();
    this.currentVehicleGroup = group;

    // Apply Paint to Material Manager
    if (paintData) {
      this.materials.applyPaint(paintData);
    }

    // Build realistic physical automotive geometry
    this.buildRealisticVehicleMesh(group, vehicleData);

    this.scene.add(group);

    if (typeof onComplete === 'function') {
      onComplete(group);
    }
  }

  buildRealisticVehicleMesh(group, vehicleData) {
    const isSUV = ['SUV', 'XUV', 'MUV', 'MPV'].includes(vehicleData.body_type);
    const isCoupe = ['Sports', 'Coupe', 'Convertible'].includes(vehicleData.body_type);

    const bodyHeight = isSUV ? 1.05 : (isCoupe ? 0.68 : 0.82);
    const groundClearance = isSUV ? 0.42 : (isCoupe ? 0.28 : 0.32);
    const bodyLength = 4.2;
    const bodyWidth = 1.85;

    // 1. Main Lower Body Shell / Chassis
    const lowerBodyGeo = new THREE.BoxGeometry(bodyWidth, bodyHeight * 0.55, bodyLength);
    const lowerBody = new THREE.Mesh(lowerBodyGeo, this.materials.carBodyPaint);
    lowerBody.position.set(0, groundClearance + bodyHeight * 0.28, 0);
    lowerBody.castShadow = true;
    lowerBody.receiveShadow = true;
    group.add(lowerBody);

    // 2. Cabin Greenhouse / Roof
    const roofLength = isCoupe ? 2.1 : (isSUV ? 2.8 : 2.4);
    const roofWidth = bodyWidth * 0.86;
    const roofHeight = bodyHeight * 0.52;
    const cabinZOffset = isCoupe ? -0.2 : (isSUV ? -0.1 : 0);

    const cabinGeo = new THREE.BoxGeometry(roofWidth, roofHeight, roofLength);
    const cabin = new THREE.Mesh(cabinGeo, this.materials.carBodyPaint);
    cabin.position.set(0, groundClearance + (bodyHeight * 0.55) + (roofHeight * 0.45), cabinZOffset);
    cabin.castShadow = true;
    group.add(cabin);

    // 3. Front Windshield (Slanted Glass)
    const windshieldGeo = new THREE.PlaneGeometry(roofWidth * 0.94, roofHeight * 1.15);
    const windshield = new THREE.Mesh(windshieldGeo, this.materials.glassMaterial);
    windshield.position.set(0, groundClearance + (bodyHeight * 0.55) + (roofHeight * 0.42), cabinZOffset + (roofLength * 0.5) + 0.1);
    windshield.rotation.x = -Math.PI / 4;
    group.add(windshield);

    // 4. Rear Windshield (Slanted Glass)
    const rearGlassGeo = new THREE.PlaneGeometry(roofWidth * 0.94, roofHeight * 1.1);
    const rearGlass = new THREE.Mesh(rearGlassGeo, this.materials.glassMaterial);
    rearGlass.position.set(0, groundClearance + (bodyHeight * 0.55) + (roofHeight * 0.42), cabinZOffset - (roofLength * 0.5) - 0.08);
    rearGlass.rotation.x = Math.PI / 4;
    group.add(rearGlass);

    // 5. Side Windows (Left & Right)
    const sideGlassGeo = new THREE.PlaneGeometry(roofLength * 0.92, roofHeight * 0.75);
    const leftGlass = new THREE.Mesh(sideGlassGeo, this.materials.glassMaterial);
    leftGlass.position.set(-roofWidth * 0.505, groundClearance + (bodyHeight * 0.55) + (roofHeight * 0.45), cabinZOffset);
    leftGlass.rotation.y = -Math.PI / 2;
    group.add(leftGlass);

    const rightGlass = new THREE.Mesh(sideGlassGeo, this.materials.glassMaterial);
    rightGlass.position.set(roofWidth * 0.505, groundClearance + (bodyHeight * 0.55) + (roofHeight * 0.45), cabinZOffset);
    rightGlass.rotation.y = Math.PI / 2;
    group.add(rightGlass);

    // 6. Front Grille & Matrix LED Headlights
    const grilleGeo = new THREE.BoxGeometry(bodyWidth * 0.7, 0.22, 0.08);
    const grille = new THREE.Mesh(grilleGeo, this.materials.glossBlackMaterial);
    grille.position.set(0, groundClearance + 0.28, bodyLength * 0.5 + 0.02);
    group.add(grille);

    // Left & Right LED Headlamps
    const headlampGeo = new THREE.BoxGeometry(0.38, 0.12, 0.08);
    const leftHeadlamp = new THREE.Mesh(headlampGeo, this.materials.ledHeadlightMaterial);
    leftHeadlamp.position.set(-bodyWidth * 0.38, groundClearance + 0.38, bodyLength * 0.5 + 0.02);
    const rightHeadlamp = new THREE.Mesh(headlampGeo, this.materials.ledHeadlightMaterial);
    rightHeadlamp.position.set(bodyWidth * 0.38, groundClearance + 0.38, bodyLength * 0.5 + 0.02);
    group.add(leftHeadlamp);
    group.add(rightHeadlamp);

    // 7. Rear OLED Sequential Taillights & Gloss Black Diffuser
    const taillampGeo = new THREE.BoxGeometry(bodyWidth * 0.9, 0.08, 0.06);
    const taillights = new THREE.Mesh(taillampGeo, this.materials.ledTaillightMaterial);
    taillights.position.set(0, groundClearance + 0.42, -bodyLength * 0.5 - 0.02);
    group.add(taillights);

    const diffuserGeo = new THREE.BoxGeometry(bodyWidth * 0.8, 0.18, 0.15);
    const diffuser = new THREE.Mesh(diffuserGeo, this.materials.glossBlackMaterial);
    diffuser.position.set(0, groundClearance + 0.08, -bodyLength * 0.5);
    group.add(diffuser);

    // 8. Add 4 Precision 3D Wheels at Corners
    const wheelY = groundClearance * 0.95;
    const wheelX = bodyWidth * 0.48;
    const wheelFrontZ = bodyLength * 0.32;
    const wheelRearZ = -bodyLength * 0.32;

    const wheelPositions = [
      { x: -wheelX, y: wheelY, z: wheelFrontZ, flip: false },
      { x: wheelX, y: wheelY, z: wheelFrontZ, flip: true },
      { x: -wheelX, y: wheelY, z: wheelRearZ, flip: false },
      { x: wheelX, y: wheelY, z: wheelRearZ, flip: true },
    ];

    this.wheels = [];
    wheelPositions.forEach(pos => {
      const wheel = this.parts.createProceduralWheel(0.36, 0.22, 'multi_spoke', this.materials.chromeMaterial);
      wheel.position.set(pos.x, pos.y, pos.z);
      if (pos.flip) {
        wheel.rotation.y = Math.PI;
      }
      group.add(wheel);
      this.wheels.push(wheel);
    });

    // 9. Initial Aerodynamic Spoiler
    this.updateSpoiler(isCoupe ? 'gt_wing' : 'ducktail');
  }

  updateSpoiler(spoilerType) {
    if (this.spoilerMesh && this.currentVehicleGroup) {
      this.currentVehicleGroup.remove(this.spoilerMesh);
      this.spoilerMesh = null;
    }
    if (spoilerType && spoilerType !== 'none') {
      this.spoilerMesh = this.parts.createSpoiler(spoilerType);
      this.currentVehicleGroup.add(this.spoilerMesh);
    }
  }

  updateWheels(rimStyle = 'multi_spoke', finish = 'chrome') {
    let finishMat = this.materials.chromeMaterial;
    if (finish === 'gloss_black' || finish === 'black') finishMat = this.materials.glossBlackMaterial;
    if (finish === 'bronze') finishMat = this.materials.satinBronzeMaterial;

    if (this.currentVehicleGroup && this.wheels.length === 4) {
      const positions = this.wheels.map(w => ({ pos: w.position.clone(), rotY: w.rotation.y }));
      
      this.wheels.forEach(w => this.currentVehicleGroup.remove(w));
      this.wheels = [];

      positions.forEach(p => {
        const wheel = this.parts.createProceduralWheel(0.36, 0.22, rimStyle, finishMat);
        wheel.position.copy(p.pos);
        wheel.rotation.y = p.rotY;
        this.currentVehicleGroup.add(wheel);
        this.wheels.push(wheel);
      });
    }
  }
}

window.VehicleLoader = VehicleLoader;
