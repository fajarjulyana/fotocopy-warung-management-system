// Main JavaScript file for Invoice Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize service items management
    initServiceItems();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize currency formatting
    initCurrencyFormatting();
    
    // Initialize search functionality
    initSearch();
});

// Service Items Management
function initServiceItems() {
    const addItemBtn = document.getElementById('add-item-btn');
    const serviceItemsContainer = document.getElementById('service-items-container');
    const itemCountInput = document.getElementById('item-count');
    
    if (!addItemBtn || !serviceItemsContainer) return;
    
    let itemCount = 0;
    
    // Add new service item
    addItemBtn.addEventListener('click', function() {
        addServiceItem();
    });
    
    function addServiceItem() {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'service-item-row';
        itemDiv.innerHTML = `
            <div class="row">
                <div class="col-md-5">
                    <label class="form-label">Jenis Perbaikan</label>
                    <input type="text" class="form-control" name="item_description_${itemCount}" 
                           placeholder="Contoh: Service laptop, ganti LCD, dll" required>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Harga (Rp)</label>
                    <input type="number" class="form-control price-input" name="item_price_${itemCount}" 
                           placeholder="50000" min="0" step="1000" required>
                </div>
                <div class="col-md-2">
                    <label class="form-label">Jumlah</label>
                    <input type="number" class="form-control quantity-input" name="item_quantity_${itemCount}" 
                           value="1" min="1" required>
                </div>
                <div class="col-md-2">
                    <label class="form-label">Aksi</label>
                    <button type="button" class="btn btn-danger btn-sm remove-item-btn w-100">
                        <i class="fas fa-trash"></i> Hapus
                    </button>
                </div>
            </div>
            <div class="row mt-2">
                <div class="col-md-12">
                    <small class="text-muted">Subtotal: <span class="item-subtotal">Rp 0</span></small>
                </div>
            </div>
        `;
        
        serviceItemsContainer.appendChild(itemDiv);
        itemCount++;
        
        // Update item count
        if (itemCountInput) {
            itemCountInput.value = itemCount;
        }
        
        // Add remove functionality
        const removeBtn = itemDiv.querySelector('.remove-item-btn');
        removeBtn.addEventListener('click', function() {
            itemDiv.remove();
            calculateTotal();
        });
        
        // Add calculation functionality
        const priceInput = itemDiv.querySelector('.price-input');
        const quantityInput = itemDiv.querySelector('.quantity-input');
        
        [priceInput, quantityInput].forEach(input => {
            input.addEventListener('input', function() {
                calculateItemSubtotal(itemDiv);
                calculateTotal();
            });
        });
    }
    
    // Calculate subtotal for individual item
    function calculateItemSubtotal(itemDiv) {
        const priceInput = itemDiv.querySelector('.price-input');
        const quantityInput = itemDiv.querySelector('.quantity-input');
        const subtotalSpan = itemDiv.querySelector('.item-subtotal');
        
        const price = parseFloat(priceInput.value) || 0;
        const quantity = parseInt(quantityInput.value) || 0;
        const subtotal = price * quantity;
        
        subtotalSpan.textContent = formatCurrency(subtotal);
    }
    
    // Add first item by default
    if (serviceItemsContainer && serviceItemsContainer.children.length === 0) {
        addServiceItem();
    }
}

// Calculate total amounts
function calculateTotal() {
    const priceInputs = document.querySelectorAll('.price-input');
    const quantityInputs = document.querySelectorAll('.quantity-input');
    const discountInput = document.getElementById('discount');
    const subtotalElement = document.getElementById('subtotal-amount');
    const discountElement = document.getElementById('discount-amount');
    const totalElement = document.getElementById('total-amount');
    
    let subtotal = 0;
    
    // Calculate subtotal
    priceInputs.forEach((priceInput, index) => {
        const price = parseFloat(priceInput.value) || 0;
        const quantity = parseInt(quantityInputs[index]?.value) || 0;
        subtotal += price * quantity;
    });
    
    // Calculate discount
    const discountPercent = parseFloat(discountInput?.value) || 0;
    const discountAmount = subtotal * (discountPercent / 100);
    const total = subtotal - discountAmount;
    
    // Update display
    if (subtotalElement) subtotalElement.textContent = formatCurrency(subtotal);
    if (discountElement) discountElement.textContent = formatCurrency(discountAmount);
    if (totalElement) totalElement.textContent = formatCurrency(total);
}

// Currency formatting
function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(amount);
}

// Initialize currency formatting for inputs
function initCurrencyFormatting() {
    const discountInput = document.getElementById('discount');
    if (discountInput) {
        discountInput.addEventListener('input', calculateTotal);
    }
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Show first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            
            form.classList.add('was-validated');
        });
    });
}

// Search functionality
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchForm = document.getElementById('search-form');
    
    if (searchInput && searchForm) {
        // Auto-submit search after typing stops
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                if (searchInput.value.trim().length >= 2 || searchInput.value.trim().length === 0) {
                    searchForm.submit();
                }
            }, 500);
        });
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function confirmDelete(message = 'Apakah Anda yakin ingin menghapus item ini?') {
    return confirm(message);
}

// Print functionality
function printInvoice() {
    window.print();
}

// Export functionality (if needed in the future)
function exportToExcel() {
    // Placeholder for future Excel export functionality
    showAlert('Fitur export Excel akan segera hadir!', 'info');
}

// Loading state management
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="loading">Memuat...</div>';
    }
}

function hideLoading() {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(el => el.remove());
}
