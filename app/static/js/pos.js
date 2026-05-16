/* POS (Point of Sale) JavaScript
   ------------------------------------------------------------ */

const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.content || '';
const CHECKOUT_URL = '/pos/checkout';
const SEARCH_URL = '/pos/search';

let cart = [];       // { product_id, name, sku, quantity, unit_price, subtotal, stock }
let searchTimer = null;

/* ============================================================
   Search
   ============================================================ */
const searchInput = document.getElementById('pos-search');
const productList = document.getElementById('product-list');
const searchPlaceholder = document.getElementById('search-placeholder');

searchInput.addEventListener('input', () => {
    clearTimeout(searchTimer);
    const q = searchInput.value.trim();
    if (!q) {
        productList.innerHTML = '';
        searchPlaceholder.style.display = 'block';
        return;
    }
    searchTimer = setTimeout(() => fetchProducts(q), 280);
});

async function fetchProducts(q) {
    try {
        const res = await fetch(`${SEARCH_URL}?q=${encodeURIComponent(q)}`);
        const products = await res.json();
        renderProductList(products);
    } catch {
        productList.innerHTML = '<p class="text-danger text-center py-3">Gagal memuat produk.</p>';
    }
}

function renderProductList(products) {
    searchPlaceholder.style.display = 'none';
    productList.innerHTML = '';

    if (!products.length) {
        productList.innerHTML = '<p class="text-muted text-center py-4">Produk tidak ditemukan.</p>';
        return;
    }

    products.forEach(p => {
        const item = document.createElement('div');
        item.className = 'list-group-item list-group-item-action product-result-item d-flex justify-content-between align-items-center';
        item.innerHTML = `
            <div>
                <div class="fw-semibold">${escHtml(p.name)}</div>
                <small class="text-muted"><code>${escHtml(p.sku)}</code> &mdash; Stok: ${p.stock}</small>
            </div>
            <div class="text-end">
                <div class="fw-bold text-primary">Rp ${fmt(p.sell_price)}</div>
                <button class="btn btn-sm btn-primary mt-1" onclick="addToCart(${JSON.stringify(p).replace(/"/g, '&quot;')})">
                    <i class="bi bi-plus-lg"></i> Tambah
                </button>
            </div>
        `;
        productList.appendChild(item);
    });
}

/* ============================================================
   Cart
   ============================================================ */
function addToCart(product) {
    const existing = cart.find(i => i.product_id === product.id);
    if (existing) {
        if (existing.quantity >= existing.stock) {
            showToast(`Stok "${product.name}" sudah mencapai batas.`, 'warning');
            return;
        }
        existing.quantity++;
        existing.subtotal = existing.quantity * existing.unit_price;
    } else {
        cart.push({
            product_id: product.id,
            name: product.name,
            sku: product.sku,
            quantity: 1,
            unit_price: product.sell_price,
            subtotal: product.sell_price,
            stock: product.stock,
        });
    }
    renderCart();
    showToast(`"${product.name}" ditambahkan ke keranjang.`, 'success');
}

function updateQty(productId, delta) {
    const item = cart.find(i => i.product_id === productId);
    if (!item) return;
    const newQty = item.quantity + delta;
    if (newQty <= 0) {
        removeFromCart(productId);
        return;
    }
    if (newQty > item.stock) {
        showToast('Jumlah melebihi stok tersedia.', 'warning');
        return;
    }
    item.quantity = newQty;
    item.subtotal = item.quantity * item.unit_price;
    renderCart();
}

function setQty(productId, value) {
    const item = cart.find(i => i.product_id === productId);
    if (!item) return;
    const qty = parseInt(value);
    if (isNaN(qty) || qty <= 0) {
        removeFromCart(productId);
        return;
    }
    if (qty > item.stock) {
        showToast('Jumlah melebihi stok tersedia.', 'warning');
        return;
    }
    item.quantity = qty;
    item.subtotal = item.quantity * item.unit_price;
    renderCart();
}

function removeFromCart(productId) {
    cart = cart.filter(i => i.product_id !== productId);
    renderCart();
}

function clearCart() {
    if (!cart.length) return;
    if (!confirm('Kosongkan keranjang?')) return;
    cart = [];
    renderCart();
}

function renderCart() {
    const tbody = document.getElementById('cart-body');
    const emptyRow = document.getElementById('cart-empty-row');

    // Remove existing item rows (keep the empty row element)
    [...tbody.querySelectorAll('.cart-item-row')].forEach(r => r.remove());

    if (!cart.length) {
        emptyRow.style.display = '';
        updateTotal();
        return;
    }

    emptyRow.style.display = 'none';

    cart.forEach(item => {
        const tr = document.createElement('tr');
        tr.className = 'cart-item-row';
        tr.innerHTML = `
            <td>
                <div class="fw-semibold small">${escHtml(item.name)}</div>
                <div class="text-muted" style="font-size:0.75rem;">Rp ${fmt(item.unit_price)}/pcs</div>
            </td>
            <td>
                <div class="d-flex align-items-center gap-1">
                    <button class="btn btn-sm btn-outline-secondary px-1 py-0"
                            onclick="updateQty(${item.product_id}, -1)">
                        <i class="bi bi-dash"></i>
                    </button>
                    <input type="number" class="form-control form-control-sm qty-input"
                           value="${item.quantity}" min="1" max="${item.stock}"
                           onchange="setQty(${item.product_id}, this.value)">
                    <button class="btn btn-sm btn-outline-secondary px-1 py-0"
                            onclick="updateQty(${item.product_id}, 1)">
                        <i class="bi bi-plus"></i>
                    </button>
                </div>
            </td>
            <td class="fw-semibold small">Rp ${fmt(item.subtotal)}</td>
            <td>
                <button class="btn btn-sm btn-outline-danger px-1 py-0"
                        onclick="removeFromCart(${item.product_id})">
                    <i class="bi bi-x"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    updateTotal();
}

/* ============================================================
   Payment
   ============================================================ */
function getTotal() {
    return cart.reduce((sum, i) => sum + i.subtotal, 0);
}

function updateTotal() {
    const total = getTotal();
    document.getElementById('cart-total').textContent = `Rp ${fmt(total)}`;
    updateChange();
}

function updateChange() {
    const total = getTotal();
    const paid = parseFloat(document.getElementById('paid-amount').value) || 0;
    const change = paid - total;
    const el = document.getElementById('change-display');
    if (change < 0) {
        el.textContent = `- Rp ${fmt(Math.abs(change))}`;
        el.className = 'fw-semibold text-danger';
    } else {
        el.textContent = `Rp ${fmt(change)}`;
        el.className = 'fw-semibold text-success';
    }
}

async function processCheckout() {
    if (!cart.length) {
        showToast('Keranjang masih kosong.', 'warning');
        return;
    }

    const paidAmount = parseFloat(document.getElementById('paid-amount').value) || 0;
    const total = getTotal();

    if (paidAmount < total) {
        showToast('Uang yang diterima kurang dari total.', 'danger');
        return;
    }

    const btn = document.getElementById('btn-checkout');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Memproses...';

    try {
        const res = await fetch(CHECKOUT_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN,
            },
            body: JSON.stringify({
                items: cart.map(i => ({
                    product_id: i.product_id,
                    quantity: i.quantity,
                    unit_price: i.unit_price,
                })),
                paid_amount: paidAmount,
            }),
        });

        const data = await res.json();

        if (data.success) {
            window.location.href = `/transactions/${data.transaction_id}`;
        } else {
            showToast(data.message || 'Transaksi gagal.', 'danger');
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check-circle me-1"></i> Proses Pembayaran';
        }
    } catch {
        showToast('Koneksi gagal. Coba lagi.', 'danger');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-check-circle me-1"></i> Proses Pembayaran';
    }
}

/* ============================================================
   Helpers
   ============================================================ */
function fmt(n) {
    return Number(n).toLocaleString('id-ID');
}

function escHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const id = `toast-${Date.now()}`;
    const colorMap = { success: 'bg-success', danger: 'bg-danger', warning: 'bg-warning text-dark', info: 'bg-info' };
    const toast = document.createElement('div');
    toast.id = id;
    toast.className = `toast align-items-center text-white border-0 ${colorMap[type] || 'bg-secondary'}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${escHtml(message)}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    container.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function createToastContainer() {
    const div = document.createElement('div');
    div.id = 'toast-container';
    div.className = 'toast-container position-fixed top-0 end-0 p-3';
    div.style.zIndex = 1100;
    document.body.appendChild(div);
    return div;
}
