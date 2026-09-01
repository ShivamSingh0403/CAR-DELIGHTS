/**
 * 3D AUTOMOTIVE STUDIO — CAMERA & PRESETS
 * Manages Perspective Camera, Orbit Controls, and smooth viewpoint transitions.
 */

class StudioCamera {
  constructor(domElement, width, height) {
    this.domElement = domElement;
    this.camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
    this.camera.position.set(4.5, 2.0, 5.0);

    if (typeof THREE.OrbitControls !== 'undefined') {
      this.controls = new THREE.OrbitControls(this.camera, this.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.maxPolarAngle = Math.PI / 2 - 0.05; // Do not go below floor
      this.controls.minDistance = 2.5;
      this.controls.maxDistance = 12.0;
      this.controls.target.set(0, 0.6, 0);
      this.controls.update();
    }

    this.presets = {
      perspective: { pos: [4.5, 2.0, 5.0], target: [0, 0.6, 0] },
      front: { pos: [0, 1.2, 5.5], target: [0, 0.6, 0] },
      rear: { pos: [0, 1.4, -5.5], target: [0, 0.6, 0] },
      side_left: { pos: [-5.8, 1.2, 0], target: [0, 0.6, 0] },
      side_right: { pos: [5.8, 1.2, 0], target: [0, 0.6, 0] },
      top: { pos: [0, 7.5, 0.1], target: [0, 0.5, 0] },
      wheel: { pos: [2.2, 0.6, 2.2], target: [1.0, 0.4, 1.3] },
    };
  }

  setPreset(presetName) {
    const p = this.presets[presetName];
    if (!p) return;

    this.camera.position.set(p.pos[0], p.pos[1], p.pos[2]);
    if (this.controls) {
      this.controls.target.set(p.target[0], p.target[1], p.target[2]);
      this.controls.update();
    }
  }

  update() {
    if (this.controls) {
      this.controls.update();
    }
  }

  resize(width, height) {
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
  }
}

window.StudioCamera = StudioCamera;
