/**
 * Contact Management JavaScript
 * Handles contact list, CRUD operations, and email testing
 */

let contacts = [];
let filteredContacts = [];
let contactGroups = [];

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadContacts();
    loadContactGroups();
});

// Load contacts from API
async function loadContacts(filters = {}) {
    try {
        const params = new URLSearchParams(filters);
        const response = await fetch(`/api/contacts?${params}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            contacts = data.contacts;
            filteredContacts = contacts;
            renderContactsTable();
            updateContactCount();
        } else {
            showAlert('error', 'فشل في تحميل جهات الاتصال');
        }
    } catch (error) {
        console.error('Error loading contacts:', error);
        showAlert('error', 'حدث خطأ أثناء تحميل جهات الاتصال');
    }
}

// Load contact groups
async function loadContactGroups() {
    try {
        const response = await fetch('/api/contacts/groups');
        const data = await response.json();
        
        if (data.status === 'success') {
            contactGroups = data.groups;
            populateGroupFilter();
        }
    } catch (error) {
        console.error('Error loading contact groups:', error);
    }
}

// Render contacts table
function renderContactsTable() {
    const tbody = document.getElementById('contactsTableBody');
    
    if (filteredContacts.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-4">
                    <i class="fas fa-users fa-2x text-muted mb-2"></i>
                    <p class="text-muted">لا توجد جهات اتصال</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filteredContacts.map(contact => `
        <tr>
            <td>
                <div class="d-flex align-items-center">
                    <div class="me-2">
                        <i class="fas fa-user-circle fa-lg text-primary"></i>
                    </div>
                    <div>
                        <div class="fw-bold">${contact.name}</div>
                        ${contact.tags && contact.tags.length > 0 ? 
                            `<small class="text-muted">${contact.tags.join(', ')}</small>` : ''
                        }
                    </div>
                </div>
            </td>
            <td>
                ${contact.email ? 
                    `<span class="text-truncate" style="max-width: 150px;">${contact.email}</span>` : 
                    '<span class="text-muted">-</span>'
                }
            </td>
            <td>
                ${contact.phone ? 
                    `<span class="text-truncate">${contact.phone}</span>` : 
                    '<span class="text-muted">-</span>'
                }
            </td>
            <td>
                ${contact.company ? 
                    `<span class="text-truncate" style="max-width: 120px;">${contact.company}</span>` : 
                    '<span class="text-muted">-</span>'
                }
            </td>
            <td>
                <div class="d-flex gap-1">
                    ${contact.available_channels.map(channel => {
                        const icons = {
                            'email': 'fas fa-envelope',
                            'sms': 'fas fa-sms',
                            'whatsapp': 'fab fa-whatsapp'
                        };
                        const colors = {
                            'email': 'text-primary',
                            'sms': 'text-success',
                            'whatsapp': 'text-info'
                        };
                        return `<i class="${icons[channel]} ${colors[channel]}" title="${channel}"></i>`;
                    }).join('')}
                </div>
            </td>
            <td>
                <span class="badge bg-light text-dark">
                    ${contact.language_preference === 'ar' ? 'العربية' : 'English'}
                </span>
            </td>
            <td>
                <span class="badge ${contact.is_active ? 'bg-success' : 'bg-secondary'}">
                    ${contact.is_active ? 'نشط' : 'غير نشط'}
                </span>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="editContact(${contact.id})" title="تعديل">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteContact(${contact.id})" title="حذف">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Update contact count
function updateContactCount() {
    document.getElementById('contactCount').textContent = filteredContacts.length;
}

// Populate group filter
function populateGroupFilter() {
    const groupFilter = document.getElementById('groupFilter');
    groupFilter.innerHTML = '<option value="">جميع المجموعات</option>';
    
    contactGroups.forEach(group => {
        groupFilter.innerHTML += `<option value="${group.id}">${group.name}</option>`;
    });
}

// Show add contact modal
function showAddContactModal() {
    // Reset form
    document.getElementById('addContactForm').reset();
    document.getElementById('contactLanguage').value = 'ar';
    document.getElementById('contactStatus').value = 'true';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('addContactModal'));
    modal.show();
}

// Save contact
async function saveContact() {
    try {
        const formData = {
            name: document.getElementById('contactName').value,
            email: document.getElementById('contactEmail').value || null,
            phone: document.getElementById('contactPhone').value || null,
            company: document.getElementById('contactCompany').value || null,
            language_preference: document.getElementById('contactLanguage').value,
            is_active: document.getElementById('contactStatus').value === 'true',
            email_opt_in: document.getElementById('emailOptIn').checked,
            sms_opt_in: document.getElementById('smsOptIn').checked,
            whatsapp_opt_in: document.getElementById('whatsappOptIn').checked,
            notes: document.getElementById('contactNotes').value || null
        };
        
        // Validation
        if (!formData.name.trim()) {
            showAlert('error', 'الاسم مطلوب');
            return;
        }
        
        if (!formData.email && !formData.phone) {
            showAlert('error', 'البريد الإلكتروني أو رقم الهاتف مطلوب');
            return;
        }
        
        const response = await fetch('/api/contacts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showAlert('success', 'تم حفظ جهة الاتصال بنجاح');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addContactModal'));
            modal.hide();
            
            // Reload contacts
            loadContacts();
        } else {
            showAlert('error', data.error || 'فشل في حفظ جهة الاتصال');
        }
    } catch (error) {
        console.error('Error saving contact:', error);
        showAlert('error', 'حدث خطأ أثناء حفظ جهة الاتصال');
    }
}

// Search contacts
function searchContacts() {
    const query = document.getElementById('searchContacts').value.toLowerCase();
    
    if (!query.trim()) {
        filteredContacts = contacts;
    } else {
        filteredContacts = contacts.filter(contact => 
            contact.name.toLowerCase().includes(query) ||
            (contact.email && contact.email.toLowerCase().includes(query)) ||
            (contact.phone && contact.phone.includes(query)) ||
            (contact.company && contact.company.toLowerCase().includes(query))
        );
    }
    
    renderContactsTable();
    updateContactCount();
}

// Apply filters
function applyFilters() {
    const groupId = document.getElementById('groupFilter').value;
    const channel = document.getElementById('channelFilter').value;
    const status = document.getElementById('statusFilter').value;
    
    const filters = {};
    if (groupId) filters.group_id = groupId;
    if (channel) filters.channel = channel;
    if (status !== 'all') filters.active_only = status === 'active';
    
    loadContacts(filters);
}

// Reset filters
function resetFilters() {
    document.getElementById('groupFilter').value = '';
    document.getElementById('channelFilter').value = '';
    document.getElementById('statusFilter').value = 'active';
    document.getElementById('searchContacts').value = '';
    
    loadContacts();
}

// Edit contact (placeholder)
function editContact(contactId) {
    // TODO: Implement edit functionality
    showAlert('info', 'ميزة التعديل قيد التطوير');
}

// Delete contact
async function deleteContact(contactId) {
    if (!confirm('هل أنت متأكد من حذف جهة الاتصال هذه؟')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/contacts/${contactId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showAlert('success', 'تم حذف جهة الاتصال بنجاح');
            loadContacts();
        } else {
            showAlert('error', data.error || 'فشل في حذف جهة الاتصال');
        }
    } catch (error) {
        console.error('Error deleting contact:', error);
        showAlert('error', 'حدث خطأ أثناء حذف جهة الاتصال');
    }
}

// Show email test modal
function testEmailService() {
    const modal = new bootstrap.Modal(document.getElementById('emailTestModal'));
    modal.show();
}

// Run email test
async function runEmailTest() {
    const emailInput = document.getElementById('testEmail');
    const resultDiv = document.getElementById('emailTestResult');
    
    if (!emailInput.value.trim()) {
        showAlert('error', 'يرجى إدخال عنوان بريد إلكتروني للاختبار');
        return;
    }
    
    try {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <span>جاري إرسال الاختبار...</span>
            </div>
        `;
        
        const response = await fetch('/api/contacts/test-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                test_email: emailInput.value
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    تم إرسال رسالة الاختبار بنجاح!
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    فشل في إرسال الاختبار: ${data.message}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error testing email:', error);
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                حدث خطأ أثناء اختبار البريد الإلكتروني
            </div>
        `;
    }
}

// Show bulk import modal (placeholder)
function showBulkImportModal() {
    showAlert('info', 'ميزة الاستيراد الجماعي قيد التطوير');
}

// Utility function to show alerts
function showAlert(type, message) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Search on Enter key
document.getElementById('searchContacts').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchContacts();
    }
});