/**
 * ReWear AI: Main Frontend Interactivity
 * Wishlist, Product Comparison, Toast Notifications & UI Utilities
 */

document.addEventListener('DOMContentLoaded', () => {
    initWishlistButtons();
    initCompareButtons();
});

// Toast notification helper
function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type === 'success' ? 'dark' : (type === 'danger' ? 'danger' : 'primary')} border-0 show shadow-lg`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.style.borderRadius = '12px';

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center gap-2">
                <i class="bi ${type === 'success' ? 'bi-check-circle-fill text-success' : 'bi-info-circle-fill'}"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    container.appendChild(toastEl);
    setTimeout(() => {
        toastEl.classList.remove('show');
        setTimeout(() => toastEl.remove(), 300);
    }, 3200);
}

// 1. Wishlist Button Handlers
function initWishlistButtons() {
    document.querySelectorAll('.wishlist-toggle-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();

            const productId = btn.dataset.productId;
            if (!productId) return;

            try {
                const res = await fetch('/api/wishlist/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: parseInt(productId) })
                });

                if (res.status === 401) {
                    window.location.href = '/login';
                    return;
                }

                const data = await res.json();
                if (data.success) {
                    const icon = btn.querySelector('i');
                    if (data.action === 'added') {
                        btn.classList.add('active');
                        if (icon) {
                            icon.classList.remove('bi-heart');
                            icon.classList.add('bi-heart-fill');
                        }
                        showToast('Item saved to your Wishlist ❤️');
                    } else {
                        btn.classList.remove('active');
                        if (icon) {
                            icon.classList.remove('bi-heart-fill');
                            icon.classList.add('bi-heart');
                        }
                        showToast('Item removed from your Wishlist');
                    }

                    // Update navbar badge if present
                    const badge = document.getElementById('nav-wishlist-count');
                    if (badge) {
                        badge.textContent = data.count;
                        badge.style.display = data.count > 0 ? 'inline-flex' : 'none';
                    }
                }
            } catch (err) {
                console.error('Error toggling wishlist:', err);
            }
        });
    });
}

// 2. Comparison System Handlers
function initCompareButtons() {
    document.querySelectorAll('.compare-toggle-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();

            const productId = btn.dataset.productId;
            if (!productId) return;

            try {
                const res = await fetch('/api/compare/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: parseInt(productId) })
                });

                const data = await res.json();
                if (data.success) {
                    if (data.action === 'added') {
                        btn.classList.add('btn-dark');
                        btn.classList.remove('btn-outline-dark');
                        btn.innerHTML = '<i class="bi bi-check-lg me-1"></i> Added to Compare';
                        showToast('Added to comparison matrix ⚖️');
                    } else {
                        btn.classList.remove('btn-dark');
                        btn.classList.add('btn-outline-dark');
                        btn.innerHTML = '<i class="bi bi-arrow-left-right me-1"></i> Compare';
                        showToast('Removed from comparison');
                    }

                    // Update dock & navbar badge
                    updateCompareDock(data.count);
                } else {
                    showToast(data.message || 'Comparison limit reached (max 4)', 'warning');
                }
            } catch (err) {
                console.error('Error toggling compare:', err);
            }
        });
    });
}

function updateCompareDock(count) {
    const badge = document.getElementById('nav-compare-count');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }

    let dock = document.getElementById('comparison-floating-dock');
    if (count > 0) {
        if (!dock) {
            dock = document.createElement('div');
            dock.id = 'comparison-floating-dock';
            dock.className = 'comparison-floating-dock';
            document.body.appendChild(dock);
        }
        dock.innerHTML = `
            <div class="d-flex align-items-center gap-2">
                <i class="bi bi-arrow-left-right text-success"></i>
                <span class="fw-bold">${count} item${count > 1 ? 's' : ''} in Comparison</span>
            </div>
            <div class="d-flex align-items-center gap-2">
                <a href="/compare" class="btn btn-sm btn-eco">View Comparison</a>
                <a href="/compare/clear" class="btn btn-sm text-white-50"><i class="bi bi-x-circle"></i></a>
            </div>
        `;
    } else if (dock) {
        dock.remove();
    }
}
