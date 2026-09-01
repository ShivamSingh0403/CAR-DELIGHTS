/**
 * 3D AUTOMOTIVE STUDIO — LIGHTING & ENVIRONMENT
 * Studio Key, Fill, Rim, Ambient and Floor Reflections.
 */

class StudioLighting {
  constructor(scene) {
    this.scene = scene;
    this.initLights();
    this.initShowroomFloor();
  }

  initLights() {
    // Soft Ambient Hemisphere Light (Sky & Ground bounce)
    this.hemiLight = new THREE.HemisphereLight(0xFFFFFF, 0x1E293B, 0.8);
    this.scene.add(this.hemiLight);

    // Key Directional Light (Studio Top-Front)
    this.keyLight = new THREE.DirectionalLight(0xFFFFFF, 2.2);
    this.keyLight.position.set(5, 8, 5);
    this.keyLight.castShadow = true;
    this.keyLight.shadow.mapSize.width = 2048;
    this.keyLight.shadow.mapSize.height = 2048;
    this.keyLight.shadow.bias = -0.0001;
    this.scene.add(this.keyLight);

    // Rim / Backlight (Highlights vehicle curves and spoiler)
    this.rimLight = new THREE.DirectionalLight(0x38BDF8, 1.8);
    this.rimLight.position.set(-6, 5, -6);
    this.scene.add(this.rimLight);

    // Soft Front Fill Light
    this.fillLight = new THREE.DirectionalLight(0xFFFFFF, 1.0);
    this.fillLight.position.set(0, 3, 6);
    this.scene.add(this.fillLight);
  }

  initShowroomFloor() {
    // Showroom Reflective Floor with Shadow Catcher
    const floorGeo = new THREE.PlaneGeometry(50, 50);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x07090E,
      metalness: 0.8,
      roughness: 0.3,
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.01;
    floor.receiveShadow = true;
    this.scene.add(floor);

    // Grid Floor Overlay for high-tech look
    const grid = new THREE.GridHelper(30, 30, 0xE50914, 0x1E293B);
    grid.position.y = 0;
    this.scene.add(grid);
  }
}

window.StudioLighting = StudioLighting;
