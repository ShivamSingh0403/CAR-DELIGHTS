/**
 * CAR DELIGHTS — MASTER JAVASCRIPT ENGINE
 * Handles Theme Toggling, AJAX Search Suggestions, Cart & Wishlist AJAX,
 * Dynamic Price Updates, and Toast Notifications.
 */

document.addEventListener('DOMContentLoaded', () => {
  initThemeSwitcher();
  initLiveSearch();
  initCartWishlistHandlers();
});

/* ============================================================
   1. THEME SWITCHER (Midnight Black / Clean White)
============================================================ */
function initThemeSwitcher() {
  const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');
  const currentTheme = localStorage.getItem('cd_theme') || document.documentElement.getAttribute('data-theme') || 'dark';

  setTheme(currentTheme, false);

  themeToggleBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      setTheme(newTheme, true);
    });
  });
}

function setTheme(theme, syncWithServer = true) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('cd_theme', theme);

  const icons = document.querySelectorAll('.theme-toggle-icon');
  icons.forEach(icon => {
    if (theme === 'light') {
      icon.className = 'bi bi-moon-stars-fill theme-toggle-icon';
    } else {
      icon.className = 'bi bi-sun-fill theme-toggle-icon';
    }
  });

  if (syncWithServer) {
    fetch('/accounts/api/set-theme/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ theme: theme })
    }).catch(err => console.log('Theme sync error (anonymous user):', err));
  }
}

/* ============================================================
   2. LIVE SEARCH AUTOCOMPLETE
============================================================ */
function initLiveSearch() {
  const searchInput = document.querySelector('#global-search-input');
  const dropdown = document.querySelector('#search-suggestions-dropdown');

  if (!searchInput || !dropdown) return;

  let debounceTimer;

  searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const query = e.target.value.trim();

    if (query.length < 2) {
      dropdown.style.display = 'none';
      dropdown.innerHTML = '';
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success' && data.results.length > 0) {
            let html = '';
            data.results.forEach(item => {
              html += `
                <a href="${item.url}" class="suggestion-item text-decoration-none">
                  <div class="action-btn-circle" style="width:32px; height:32px;">
                    <i class="bi ${item.icon}"></i>
                  </div>
                  <div class="flex-grow-1 overflow-hidden">
                    <div class="fw-bold text-truncate" style="color:var(--text-primary); font-size:0.9rem;">${item.title}</div>
                    <div class="text-truncate" style="color:var(--text-muted); font-size:0.75rem;">${item.type} • ${item.subtitle}</div>
                  </div>
                  <i class="bi bi-chevron-right text-muted small"></i>
                </a>
              `;
            });
            dropdown.innerHTML = html;
            dropdown.style.display = 'block';
          } else {
            dropdown.innerHTML = '<div class="p-3 text-muted text-center small">No matching cars or parts found</div>';
            dropdown.style.display = 'block';
          }
        })
        .catch(err => console.error('Search suggestion error:', err));
    }, 250);
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = 'none';
    }
  });
}

/* ============================================================
   3. CART & WISHLIST AJAX HANDLERS
============================================================ */
function initCartWishlistHandlers() {
  // Add to Cart AJAX
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-add-to-cart-ajax');
    if (!btn) return;

    e.preventDefault();
    const productId = btn.dataset.productId;
    const buildId = btn.dataset.buildId;
    const serviceId = btn.dataset.serviceId;
    const itemType = btn.dataset.itemType || 'product';
    const quantity = btn.dataset.quantity || 1;

    btn.disabled = true;
    const originalContent = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Adding...';

    fetch('/cart/api/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        item_type: itemType,
        product_id: productId,
        build_id: buildId,
        service_id: serviceId,
        quantity: parseInt(quantity)
      })
    })
    .then(res => res.json())
    .then(data => {
      btn.disabled = false;
      btn.innerHTML = originalContent;

      if (data.status === 'success') {
        showToast(data.message, 'success');
        updateCartBadge(data.cart_count);
      } else {
        showToast(data.message || 'Error adding to cart', 'error');
      }
    })
    .catch(err => {
      btn.disabled = false;
      btn.innerHTML = originalContent;
      showToast('Could not add to cart. Please try again.', 'error');
    });
  });

  // Wishlist Toggle AJAX
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-wishlist-toggle');
    if (!btn) return;

    e.preventDefault();
    const productId = btn.dataset.productId;
    const vehicleId = btn.dataset.vehicleId;

    fetch('/api/wishlist/toggle/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        product_id: productId,
        vehicle_id: vehicleId
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        showToast(data.message, 'info');
        updateWishlistBadge(data.wishlist_count);
        if (data.added) {
          btn.classList.add('active');
          btn.querySelector('i')?.classList.replace('bi-heart', 'bi-heart-fill');
        } else {
          btn.classList.remove('active');
          btn.querySelector('i')?.classList.replace('bi-heart-fill', 'bi-heart');
        }
      } else {
        if (data.message && data.message.includes('login')) {
          window.location.href = '/accounts/login/?next=' + window.location.pathname;
        } else {
          showToast(data.message || 'Error updating wishlist', 'error');
        }
      }
    })
    .catch(err => console.error('Wishlist error:', err));
  });
}

function updateCartBadge(count) {
  const badges = document.querySelectorAll('.cart-count-badge');
  badges.forEach(b => {
    b.textContent = count;
    b.style.display = count > 0 ? 'inline-block' : 'none';
  });
}

function updateWishlistBadge(count) {
  const badges = document.querySelectorAll('.wishlist-count-badge');
  badges.forEach(b => {
    b.textContent = count;
    b.style.display = count > 0 ? 'inline-block' : 'none';
  });
}

/* ============================================================
   4. TOAST NOTIFICATION UTILITY
============================================================ */
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container-cd');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container-cd';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast-cd';
  
  let icon = 'bi-info-circle-fill text-info';
  if (type === 'success') icon = 'bi-check-circle-fill text-success';
  if (type === 'error') icon = 'bi-exclamation-triangle-fill text-danger';

  toast.innerHTML = `
    <i class="bi ${icon} fs-5"></i>
    <div class="flex-grow-1 small fw-semibold">${message}</div>
    <button type="button" class="btn-close btn-close-white ms-2" style="font-size:0.75rem;" onclick="this.parentElement.remove()"></button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

/* CSRF Helper */
function getCsrfToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  return cookieValue || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

/* INR Currency Formatter Helper */
function formatINR(amount) {
  return '₹' + Number(amount).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}
