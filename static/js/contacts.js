/**
 * Contact Management JavaScript
 * Handles contact list, CRUD operations, and email testing
 */

let contacts = [];
let filteredContacts = [];
let contactGroups = [];

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Add error handling for DOM operations
    try {
        loadContacts();
        loadContactGroups();
    } catch (error) {
        console.error('Error initializing contacts page:', error);
        showAlert('error', 'حدث خطأ في تحميل الصفحة');
    }
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

// Escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Render contacts table
function renderContactsTable() {
    const tbody = document.getElementById('contactsTableBody');
    if (!tbody) {
        console.error('Contact table body not found');
        return;
    }
    
    // Clear existing content
    tbody.innerHTML = '';
    
    if (filteredContacts.length === 0) {
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = 8;
        emptyCell.className = 'text-center py-4';
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-users fa-2x text-muted mb-2';
        
        const message = document.createElement('p');
        message.className = 'text-muted';
        message.textContent = 'لا توجد جهات اتصال';
        
        emptyCell.appendChild(icon);
        emptyCell.appendChild(message);
        emptyRow.appendChild(emptyCell);
        tbody.appendChild(emptyRow);
        return;
    }
    
    filteredContacts.forEach(contact => {
        const row = document.createElement('tr');
        
        // Name column
        const nameCell = document.createElement('td');
        const nameContainer = document.createElement('div');
        nameContainer.className = 'd-flex align-items-center';
        
        const iconDiv = document.createElement('div');
        iconDiv.className = 'me-2';
        iconDiv.innerHTML = '<i class="fas fa-user-circle fa-lg text-primary"></i>';
        
        const infoDiv = document.createElement('div');
        const nameDiv = document.createElement('div');
        nameDiv.className = 'fw-bold';
        nameDiv.textContent = contact.name || '';
        
        infoDiv.appendChild(nameDiv);
        
        if (contact.tags && contact.tags.length > 0) {
            const tagsSmall = document.createElement('small');
            tagsSmall.className = 'text-muted';
            tagsSmall.textContent = contact.tags.join(', ');
            infoDiv.appendChild(tagsSmall);
        }
        
        nameContainer.appendChild(iconDiv);
        nameContainer.appendChild(infoDiv);
        nameCell.appendChild(nameContainer);
        
        // Email column
        const emailCell = document.createElement('td');
        if (contact.email) {
            const emailSpan = document.createElement('span');
            emailSpan.className = 'text-truncate';
            emailSpan.style.maxWidth = '150px';
            emailSpan.textContent = contact.email;
            emailCell.appendChild(emailSpan);
        } else {
            const emptySpan = document.createElement('span');
            emptySpan.className = 'text-muted';
            emptySpan.textContent = '-';
            emailCell.appendChild(emptySpan);
        }
        
        // Phone column
        const phoneCell = document.createElement('td');
        if (contact.phone) {
            const phoneSpan = document.createElement('span');
            phoneSpan.className = 'text-truncate';
            phoneSpan.textContent = contact.phone;
            phoneCell.appendChild(phoneSpan);
        } else {
            const emptySpan = document.createElement('span');
            emptySpan.className = 'text-muted';
            emptySpan.textContent = '-';
            phoneCell.appendChild(emptySpan);
        }
        
        // Company column
        const companyCell = document.createElement('td');
        if (contact.company) {
            const companySpan = document.createElement('span');
            companySpan.className = 'text-truncate';
            companySpan.style.maxWidth = '120px';
            companySpan.textContent = contact.company;
            companyCell.appendChild(companySpan);
        } else {
            const emptySpan = document.createElement('span');
            emptySpan.className = 'text-muted';
            emptySpan.textContent = '-';
            companyCell.appendChild(emptySpan);
        }
        
        // Channels column
        const channelsCell = document.createElement('td');
        const channelsDiv = document.createElement('div');
        channelsDiv.className = 'd-flex gap-1';
        
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
        
        (contact.available_channels || []).forEach(channel => {
            if (icons[channel]) {
                const channelIcon = document.createElement('i');
                channelIcon.className = `${icons[channel]} ${colors[channel]}`;
                channelIcon.title = channel;
                channelsDiv.appendChild(channelIcon);
            }
        });
        
        channelsCell.appendChild(channelsDiv);
        
        // Language column
        const langCell = document.createElement('td');
        const langBadge = document.createElement('span');
        langBadge.className = 'badge bg-light text-dark';
        langBadge.textContent = contact.language_preference === 'ar' ? 'العربية' : 'English';
        langCell.appendChild(langBadge);
        
        // Status column
        const statusCell = document.createElement('td');
        const statusBadge = document.createElement('span');
        statusBadge.className = `badge ${contact.is_active ? 'bg-success' : 'bg-secondary'}`;
        statusBadge.textContent = contact.is_active ? 'نشط' : 'غير نشط';
        statusCell.appendChild(statusBadge);
        
        // Actions column
        const actionsCell = document.createElement('td');
        const btnGroup = document.createElement('div');
        btnGroup.className = 'btn-group btn-group-sm';
        
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-outline-primary';
        editBtn.title = 'تعديل';
        editBtn.onclick = () => editContact(contact.id);
        editBtn.innerHTML = '<i class="fas fa-edit"></i>';
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-outline-danger';
        deleteBtn.title = 'حذف';
        deleteBtn.onclick = () => deleteContact(contact.id);
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        
        btnGroup.appendChild(editBtn);
        btnGroup.appendChild(deleteBtn);
        actionsCell.appendChild(btnGroup);
        
        // Assemble row
        row.appendChild(nameCell);
        row.appendChild(emailCell);
        row.appendChild(phoneCell);
        row.appendChild(companyCell);
        row.appendChild(channelsCell);
        row.appendChild(langCell);
        row.appendChild(statusCell);
        row.appendChild(actionsCell);
        
        tbody.appendChild(row);
    });
}

// Update contact count
function updateContactCount() {
    const countElement = document.getElementById('contactCount');
    if (countElement) {
        countElement.textContent = filteredContacts.length;
    }
}

// Populate group filter
function populateGroupFilter() {
    const groupFilter = document.getElementById('groupFilter');
    if (!groupFilter) {
        console.error('Group filter element not found');
        return;
    }
    
    // Clear existing options
    groupFilter.innerHTML = '';
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'جميع المجموعات';
    groupFilter.appendChild(defaultOption);
    
    // Add group options
    contactGroups.forEach(group => {
        const option = document.createElement('option');
        option.value = group.id;
        option.textContent = group.name || '';
        groupFilter.appendChild(option);
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

// Edit contact
function editContact(contactId) {
    // Find the contact in the contacts array
    const contact = contacts.find(c => c.id === contactId);
    if (!contact) {
        showAlert('error', 'لم يتم العثور على جهة الاتصال');
        return;
    }
    
    // Populate the edit form with contact data
    document.getElementById('editContactId').value = contact.id;
    document.getElementById('editContactName').value = contact.name || '';
    document.getElementById('editContactEmail').value = contact.email || '';
    document.getElementById('editContactPhone').value = contact.phone || '';
    document.getElementById('editContactCompany').value = contact.company || '';
    document.getElementById('editContactLanguage').value = contact.language_preference || 'ar';
    document.getElementById('editContactStatus').value = contact.is_active ? 'true' : 'false';
    document.getElementById('editEmailOptIn').checked = contact.email_opt_in;
    document.getElementById('editSmsOptIn').checked = contact.sms_opt_in;
    document.getElementById('editWhatsappOptIn').checked = contact.whatsapp_opt_in;
    document.getElementById('editContactNotes').value = contact.notes || '';
    
    // Show the edit modal
    const modal = new bootstrap.Modal(document.getElementById('editContactModal'));
    modal.show();
}

// Update contact
async function updateContact() {
    try {
        const contactId = document.getElementById('editContactId').value;
        const formData = {
            name: document.getElementById('editContactName').value,
            email: document.getElementById('editContactEmail').value || null,
            phone: document.getElementById('editContactPhone').value || null,
            company: document.getElementById('editContactCompany').value || null,
            language_preference: document.getElementById('editContactLanguage').value,
            is_active: document.getElementById('editContactStatus').value === 'true',
            email_opt_in: document.getElementById('editEmailOptIn').checked,
            sms_opt_in: document.getElementById('editSmsOptIn').checked,
            whatsapp_opt_in: document.getElementById('editWhatsappOptIn').checked,
            notes: document.getElementById('editContactNotes').value || null
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
        
        const response = await fetch(`/api/contacts/${contactId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showAlert('success', 'تم تحديث جهة الاتصال بنجاح');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editContactModal'));
            modal.hide();
            
            // Reload contacts
            loadContacts();
        } else {
            showAlert('error', data.error || 'فشل في تحديث جهة الاتصال');
        }
    } catch (error) {
        console.error('Error updating contact:', error);
        showAlert('error', 'حدث خطأ أثناء تحديث جهة الاتصال');
    }
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
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchContacts');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchContacts();
            }
        });
    }
});