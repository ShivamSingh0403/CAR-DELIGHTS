/**
 * CAR DELIGHTS — 3D CUSTOMIZATION STUDIO ORCHESTRATOR
 * Integrates Three.js 3D Viewport with HTML Controls, Live Server-side
 * Pricing in INR (₹), Paint Swapping, Parts Selection, and Build Saving.
 */

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('customizer-canvas-container');
  if (!container) return; // Not on customizer page

  window.customizerApp = new CustomizerApp();
});

class CustomizerApp {
  constructor() {
    this.viewer = new StudioViewer('customizer-canvas-container');
    this.currentVehicleId = document.getElementById('vehicle-selector')?.value || 1;
    this.selectedPaintId = null;
    this.selectedParts = {}; // slot -> part_id
    this.configData = null;

    this.initUI();
    this.loadVehicleConfig(this.currentVehicleId);
  }

  initUI() {
    // 1. Vehicle Selector Change
    const vehicleSelect = document.getElementById('vehicle-selector');
    if (vehicleSelect) {
      vehicleSelect.addEventListener('change', (e) => {
        this.currentVehicleId = e.target.value;
        this.selectedParts = {};
        this.loadVehicleConfig(this.currentVehicleId);
      });
    }

    // 2. Camera Viewport Controls
    document.querySelectorAll('.viewport-control-btn[data-camera-preset]').forEach(btn => {
      btn.addEventListener('click', () => {
        const preset = btn.dataset.cameraPreset;
        this.viewer.cameraManager.setPreset(preset);
      });
    });

    // 3. Auto-Rotate Toggle
    const rotateBtn = document.getElementById('btn-toggle-rotate');
    if (rotateBtn) {
      rotateBtn.addEventListener('click', () => {
        const isRotating = this.viewer.toggleAutoRotate();
        rotateBtn.classList.toggle('active', isRotating);
        rotateBtn.innerHTML = isRotating ? '<i class="bi bi-pause-fill"></i>' : '<i class="bi bi-play-fill"></i>';
      });
    }

    // 4. Tab Switching Handler
    document.querySelectorAll('.customizer-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const targetSelector = btn.getAttribute('data-bs-target') || btn.getAttribute('href');
        document.querySelectorAll('.customizer-tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.tab-pane').forEach(p => {
          p.classList.remove('show', 'active');
        });
        if (targetSelector) {
          const targetPane = document.querySelector(targetSelector);
          if (targetPane) targetPane.classList.add('show', 'active');
        }
      });
    });

    // 5. Before / After Comparison Toggle
    const compareBtn = document.getElementById('btn-toggle-compare');
    if (compareBtn) {
      let isOriginal = false;
      compareBtn.addEventListener('click', () => {
        isOriginal = !isOriginal;
        compareBtn.classList.toggle('btn-cd-primary', isOriginal);
        compareBtn.classList.toggle('btn-cd-outline', !isOriginal);
        compareBtn.textContent = isOriginal ? 'Show Customized View' : 'Compare with Stock';

        if (isOriginal) {
          // Reset to factory paint (White) and stock rims
          this.viewer.materialManager.applyPaint({ hex_color: '#F8FAFC', metalness: 0.7, roughness: 0.2, clearcoat: 0.8 });
          this.viewer.vehicleLoader.updateWheels('5_spoke', 'silver');
          this.viewer.vehicleLoader.updateSpoiler('none');
        } else {
          // Restore selected customized state
          this.applySelectedCustomizations();
        }
      });
    }

    // 6. Save Build Button
    const saveBuildBtn = document.getElementById('btn-save-build');
    if (saveBuildBtn) {
      saveBuildBtn.addEventListener('click', () => this.saveBuild(false));
    }

    // 7. Add Build to Cart Button
    const addBuildToCartBtn = document.getElementById('btn-add-build-cart');
    if (addBuildToCartBtn) {
      addBuildToCartBtn.addEventListener('click', () => this.saveBuild(true));
    }
  }

  loadVehicleConfig(vehicleId) {
    const loadingOverlay = document.getElementById('customizer-loading-overlay');
    if (loadingOverlay) {
      loadingOverlay.classList.remove('d-none');
      loadingOverlay.classList.add('d-flex');
    }

    fetch(`/customizer/api/config/${vehicleId}/`)
      .then(res => res.json())
      .then(data => {
        if (loadingOverlay) {
          loadingOverlay.classList.remove('d-flex');
          loadingOverlay.classList.add('d-none');
        }
        if (data.status === 'success') {
          this.configData = data;
          this.renderVehicle(data.vehicle, data.paints);
          this.renderPaintStudio(data.paints);
          this.renderPartsTabs(data.parts);
          this.recalculatePrice();
        }
      })
      .catch(err => {
        if (loadingOverlay) {
          loadingOverlay.classList.remove('d-flex');
          loadingOverlay.classList.add('d-none');
        }
        console.error('Error loading customizer configuration:', err);
      });
  }

  renderVehicle(vehicle, paints) {
    // Select first paint or red metallic
    const defaultPaint = paints.find(p => p.finish_type === 'Metallic') || paints[0];
    this.selectedPaintId = defaultPaint ? defaultPaint.id : null;

    this.viewer.vehicleLoader.loadVehicle(vehicle, defaultPaint);

    // Update UI headers
    const titleElem = document.getElementById('active-vehicle-title');
    const priceElem = document.getElementById('active-vehicle-base-price');
    if (titleElem) titleElem.textContent = vehicle.name;
    if (priceElem) priceElem.textContent = vehicle.formatted_price;

    const badge3D = document.getElementById('badge-3d-status');
    if (badge3D) {
      badge3D.textContent = vehicle.is_3d_available ? '3D Customization Available' : '3D High-Fidelity Render';
    }

    const v3dText = document.getElementById('customizer-3d-text');
    const v3dIcon = document.getElementById('customizer-3d-icon');
    if (v3dText && v3dIcon) {
      if (vehicle.is_3d_available) {
        v3dText.textContent = '3D WebGL Simulation Active';
        v3dIcon.className = 'bi bi-box-fill text-cyan';
      } else {
        v3dText.textContent = '3D ASSET NOT AVAILABLE — Real Catalog Media Active';
        v3dIcon.className = 'bi bi-image text-warning';
      }
    }
  }

  renderPaintStudio(paints) {
    const container = document.getElementById('paint-swatches-grid');
    if (!container) return;

    container.innerHTML = '';
    paints.forEach(paint => {
      const swatch = document.createElement('div');
      swatch.className = `paint-swatch ${paint.id === this.selectedPaintId ? 'active' : ''}`;
      swatch.style.backgroundColor = paint.hex_color;
      swatch.title = `${paint.name} (${paint.finish_type}) - ${paint.formatted_price}`;

      swatch.addEventListener('click', () => {
        document.querySelectorAll('.paint-swatch').forEach(s => s.classList.remove('active'));
        swatch.classList.add('active');

        this.selectedPaintId = paint.id;
        this.viewer.materialManager.applyPaint(paint);

        const label = document.getElementById('selected-paint-name');
        if (label) label.textContent = `${paint.name} (${paint.finish_type}) • ${paint.formatted_price}`;

        this.recalculatePrice();
      });

      container.appendChild(swatch);
    });
  }

  renderPartsTabs(partsBySlot) {
    // Wheels Tab
    const wheelsList = document.getElementById('parts-list-wheels');
    if (wheelsList) {
      wheelsList.innerHTML = '';
      const wheels = partsBySlot.wheels || [];
      if (wheels.length === 0) {
        wheelsList.innerHTML = '<div class="text-muted small p-2">Standard OEM Performance Alloys active.</div>';
      }
      wheels.forEach(w => {
        const item = document.createElement('div');
        item.className = 'card-cd p-2 mb-2 d-flex flex-row align-items-center gap-2 cursor-pointer';
        item.style.cursor = 'pointer';
        item.innerHTML = `
          <img src="${w.image}" width="48" height="48" class="rounded" style="object-fit:cover;">
          <div class="flex-grow-1 overflow-hidden">
            <div class="fw-bold text-truncate small">${w.name}</div>
            <div class="text-warning small">${w.formatted_price}</div>
          </div>
          <input type="radio" name="slot_wheels" value="${w.id}" class="form-check-input">
        `;
        item.addEventListener('click', () => {
          item.querySelector('input').checked = true;
          this.selectedParts['wheel'] = w.id;
          this.viewer.vehicleLoader.updateWheels('mesh', 'gloss_black');
          this.recalculatePrice();
        });
        wheelsList.appendChild(item);
      });
    }

    // Aerodynamics / Spoilers Tab
    const spoilerList = document.getElementById('parts-list-spoilers');
    if (spoilerList) {
      spoilerList.innerHTML = '';
      const spoilers = partsBySlot.spoiler || [];
      spoilers.forEach(s => {
        const item = document.createElement('div');
        item.className = 'card-cd p-2 mb-2 d-flex flex-row align-items-center gap-2 cursor-pointer';
        item.style.cursor = 'pointer';
        item.innerHTML = `
          <img src="${s.image}" width="48" height="48" class="rounded" style="object-fit:cover;">
          <div class="flex-grow-1 overflow-hidden">
            <div class="fw-bold text-truncate small">${s.name}</div>
            <div class="text-danger small">${s.formatted_price}</div>
          </div>
          <input type="radio" name="slot_spoiler" value="${s.id}" class="form-check-input">
        `;
        item.addEventListener('click', () => {
          item.querySelector('input').checked = true;
          this.selectedParts['spoiler'] = s.id;
          this.viewer.vehicleLoader.updateSpoiler('gt_wing');
          this.recalculatePrice();
        });
        spoilerList.appendChild(item);
      });
    }
  }

  applySelectedCustomizations() {
    if (this.configData && this.selectedPaintId) {
      const paint = this.configData.paints.find(p => p.id === this.selectedPaintId);
      if (paint) this.viewer.materialManager.applyPaint(paint);
    }
    if (this.selectedParts['wheel']) {
      this.viewer.vehicleLoader.updateWheels('mesh', 'gloss_black');
    }
    if (this.selectedParts['spoiler']) {
      this.viewer.vehicleLoader.updateSpoiler('gt_wing');
    }
  }

  recalculatePrice() {
    fetch('/customizer/api/calculate-price/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        vehicle_id: this.currentVehicleId,
        paint_id: this.selectedPaintId,
        part_ids: this.selectedParts
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        const priceLabel = document.getElementById('live-total-build-price');
        if (priceLabel) priceLabel.textContent = data.formatted_total;

        const breakdownList = document.getElementById('build-breakdown-list');
        if (breakdownList) {
          let html = '';
          data.breakdown.forEach(item => {
            html += `<li class="d-flex justify-content-between py-1 border-bottom border-secondary small">
              <span>${item.label}</span>
              <span class="fw-bold">${formatINR(item.amount)}</span>
            </li>`;
          });
          breakdownList.innerHTML = html;
        }
      }
    })
    .catch(err => console.error('Price recalculation error:', err));
  }

  saveBuild(addToCart = false) {
    const snapshot = this.viewer.takeSnapshot();
    const buildNameInput = document.getElementById('custom-build-name-input');
    const buildName = buildNameInput ? buildNameInput.value : 'My Dream Custom Build';

    fetch('/customizer/api/save-build/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        vehicle_id: this.currentVehicleId,
        name: buildName,
        paint_id: this.selectedPaintId,
        part_ids: this.selectedParts,
        snapshot_image: snapshot,
        add_to_cart: addToCart
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        showToast(data.message, 'success');
        if (addToCart) {
          setTimeout(() => { window.location.href = '/cart/'; }, 800);
        } else {
          setTimeout(() => { window.location.href = '/garage/saved-builds/'; }, 800);
        }
      } else {
        showToast(data.message || 'Could not save build', 'error');
      }
    })
    .catch(err => {
      showToast('Network error while saving build.', 'error');
    });
  }
}
