// Personal Savings Tracker JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-set today's date for new entries
    const dateInput = document.getElementById('date');
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }

    // Format number input for amount
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', function(e) {
            // Remove any non-digit characters except decimal point
            let value = e.target.value.replace(/[^\d.]/g, '');
            
            // Ensure only one decimal point
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            
            e.target.value = value;
        });

        // Add focus effect
        amountInput.addEventListener('focus', function() {
            this.select();
        });
    }

    // Auto-resize textarea
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    
                    // Show custom error message
                    showToast('Mohon lengkapi semua field yang diperlukan!', 'error');
                }
            } else {
                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('loading');
                    submitBtn.disabled = true;
                    
                    // Re-enable after 3 seconds as fallback
                    setTimeout(() => {
                        submitBtn.classList.remove('loading');
                        submitBtn.disabled = false;
                    }, 3000);
                }
            }
            
            form.classList.add('was-validated');
        });
    });

    // Smooth scroll to top
    window.addEventListener('scroll', function() {
        const scrollBtn = document.getElementById('scrollToTop');
        if (scrollBtn) {
            if (window.pageYOffset > 300) {
                scrollBtn.style.display = 'block';
            } else {
                scrollBtn.style.display = 'none';
            }
        }
    });

    // Search functionality
    const searchInput = document.getElementById('search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Auto-submit search form after 500ms of no typing
                if (this.value.length > 2 || this.value.length === 0) {
                    this.form.submit();
                }
            }, 500);
        });
    }

    // Animate counters on page load
    animateCounters();

    // Initialize delete confirmation
    initializeDeleteConfirmation();
});

// Delete confirmation function
function confirmDelete(entryId, description) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const descriptionElement = document.getElementById('deleteDescription');
    
    if (modal && form && descriptionElement) {
        // Set the form action
        form.action = `/delete/${entryId}`;
        
        // Set the description
        descriptionElement.textContent = `"${description}"`;
        
        // Show the modal
        const deleteModal = new bootstrap.Modal(modal);
        deleteModal.show();
    }
}

// Initialize delete confirmation
function initializeDeleteConfirmation() {
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function() {
            // Focus on cancel button
            const cancelBtn = deleteModal.querySelector('.btn-secondary');
            if (cancelBtn) {
                setTimeout(() => cancelBtn.focus(), 100);
            }
        });
    }
}

// Animate counters
function animateCounters() {
    const counters = document.querySelectorAll('.card h4');
    
    counters.forEach(counter => {
        const text = counter.textContent;
        
        // Extract number from text (handles currency format)
        const number = text.replace(/[^\d]/g, '');
        if (number && !isNaN(number)) {
            const target = parseInt(number);
            const increment = target / 50; // Animation duration
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                // Update display with original formatting
                if (text.includes('Rp')) {
                    counter.textContent = `Rp ${Math.floor(current).toLocaleString('id-ID')}`;
                } else {
                    counter.textContent = Math.floor(current);
                }
            }, 20);
        }
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to page
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1080';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Format currency for display
function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N: Add new entry
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        window.location.href = '/add';
    }
    
    // Ctrl/Cmd + H: Go home
    if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
        e.preventDefault();
        window.location.href = '/';
    }
    
    // ESC: Close modals
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
});

// Add scroll to top button
function addScrollToTopButton() {
    const button = document.createElement('button');
    button.id = 'scrollToTop';
    button.className = 'btn btn-primary position-fixed';
    button.style.cssText = `
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    `;
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.title = 'Kembali ke atas';
    
    button.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.body.appendChild(button);
}

// Initialize scroll to top button
addScrollToTopButton();

// Auto-save form data in localStorage (for form recovery)
function initializeFormRecovery() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const formId = form.id || form.action;
        
        // Load saved data
        const savedData = localStorage.getItem(`form_${formId}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && input.type !== 'submit') {
                        input.value = data[key];
                    }
                });
            } catch (e) {
                console.warn('Failed to restore form data:', e);
            }
        }
        
        // Save data on input
        form.addEventListener('input', function() {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            localStorage.setItem(`form_${formId}`, JSON.stringify(data));
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(`form_${formId}`);
        });
    });
}

// Initialize form recovery
initializeFormRecovery();
