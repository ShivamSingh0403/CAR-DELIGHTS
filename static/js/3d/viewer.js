/**
 * 3D AUTOMOTIVE STUDIO — MASTER VIEWER & WEBGL ENGINE
 * Core Three.js render loop, tone mapping, antialiasing and animation loop.
 */

class StudioViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      console.warn('3D customizer container element not found:', containerId);
      return;
    }

    this.width = this.container.clientWidth || window.innerWidth;
    this.height = this.container.clientHeight || 550;

    // 1. Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x07090E);

    // 2. Renderer
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance",
      preserveDrawingBuffer: true
    });
    this.renderer.setSize(this.width, this.height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.container.appendChild(this.renderer.domElement);

    // 3. Camera & Controls
    this.cameraManager = new StudioCamera(this.renderer.domElement, this.width, this.height);

    // 4. Lighting & Environment
    this.lighting = new StudioLighting(this.scene);

    // 5. Material & Parts Managers
    this.materialManager = new MaterialManager();
    this.partsManager = new PartsManager(this.scene, this.materialManager);

    // 6. Vehicle Loader
    this.vehicleLoader = new VehicleLoader(this.scene, this.materialManager, this.partsManager);

    this.isAutoRotating = true;

    // Bind Event Listeners
    window.addEventListener('resize', this.onResize.bind(this));

    // Start Render Loop
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  animate() {
    requestAnimationFrame(this.animate);

    if (this.isAutoRotating && this.vehicleLoader.currentVehicleGroup) {
      this.vehicleLoader.currentVehicleGroup.rotation.y += 0.003;
    }

    this.cameraManager.update();
    this.renderer.render(this.scene, this.cameraManager.camera);
  }

  onResize() {
    if (!this.container) return;
    this.width = this.container.clientWidth;
    this.height = this.container.clientHeight;
    this.cameraManager.resize(this.width, this.height);
    this.renderer.setSize(this.width, this.height);
  }

  toggleAutoRotate(state) {
    this.isAutoRotating = state !== undefined ? state : !this.isAutoRotating;
    return this.isAutoRotating;
  }

  takeSnapshot() {
    return this.renderer.domElement.toDataURL('image/jpeg', 0.85);
  }
}

window.StudioViewer = StudioViewer;
