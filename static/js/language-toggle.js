/**
 * Universal Language Toggle for Arabic Voice of Customer Platform
 * Switches between Arabic and English across all pages
 */

let currentLang = 'ar';

function toggleLanguage() {
    if (currentLang === 'ar') {
        switchToEnglish();
    } else {
        switchToArabic();
    }
    
    // Store preference in localStorage
    localStorage.setItem('preferred-language', currentLang);
}

function switchToEnglish() {
    currentLang = 'en';
    document.documentElement.setAttribute('lang', 'en');
    document.documentElement.setAttribute('dir', 'ltr');
    
    // Update toggle button
    const langText = document.getElementById('langText');
    if (langText) langText.textContent = 'العربية';
    
    // Show English text, hide Arabic
    document.querySelectorAll('.text-ar, .nav-text-ar, .hero-text-ar, .hero-desc-ar, .hero-sub-ar, .btn-text-ar, .feature-title-ar, .feature-desc-ar, .stats-label-ar, .form-label-ar, .card-title-ar, .card-text-ar').forEach(el => {
        el.classList.add('d-none');
    });
    
    document.querySelectorAll('.text-en, .nav-text-en, .hero-text-en, .hero-desc-en, .hero-sub-en, .btn-text-en, .feature-title-en, .feature-desc-en, .stats-label-en, .form-label-en, .card-title-en, .card-text-en').forEach(el => {
        el.classList.remove('d-none');
    });
    
    // Update brand text
    const brandText = document.getElementById('brandText');
    if (brandText) brandText.textContent = 'Arabic VoC Platform';
    
    // Update page title
    document.title = document.title.replace(/منصة صوت العميل العربية/g, 'Arabic Voice of Customer Platform');
    
    // Adjust layout for LTR
    document.body.classList.remove('rtl-layout');
    document.body.classList.add('ltr-layout');
    
    // Update Bootstrap RTL classes
    document.querySelectorAll('.text-end').forEach(el => {
        el.classList.remove('text-end');
        el.classList.add('text-start');
    });
    
    document.querySelectorAll('.me-auto').forEach(el => {
        el.classList.remove('me-auto');
        el.classList.add('ms-auto');
    });
}

function switchToArabic() {
    currentLang = 'ar';
    document.documentElement.setAttribute('lang', 'ar');
    document.documentElement.setAttribute('dir', 'rtl');
    
    // Update toggle button
    const langText = document.getElementById('langText');
    if (langText) langText.textContent = 'English';
    
    // Show Arabic text, hide English
    document.querySelectorAll('.text-en, .nav-text-en, .hero-text-en, .hero-desc-en, .hero-sub-en, .btn-text-en, .feature-title-en, .feature-desc-en, .stats-label-en, .form-label-en, .card-title-en, .card-text-en').forEach(el => {
        el.classList.add('d-none');
    });
    
    document.querySelectorAll('.text-ar, .nav-text-ar, .hero-text-ar, .hero-desc-ar, .hero-sub-ar, .btn-text-ar, .feature-title-ar, .feature-desc-ar, .stats-label-ar, .form-label-ar, .card-title-ar, .card-text-ar').forEach(el => {
        el.classList.remove('d-none');
    });
    
    // Update brand text
    const brandText = document.getElementById('brandText');
    if (brandText) brandText.textContent = 'صوت العميل العربية';
    
    // Update page title
    document.title = document.title.replace(/Arabic Voice of Customer Platform/g, 'منصة صوت العميل العربية');
    
    // Adjust layout for RTL
    document.body.classList.remove('ltr-layout');
    document.body.classList.add('rtl-layout');
    
    // Update Bootstrap RTL classes
    document.querySelectorAll('.text-start').forEach(el => {
        el.classList.remove('text-start');
        el.classList.add('text-end');
    });
    
    document.querySelectorAll('.ms-auto').forEach(el => {
        el.classList.remove('ms-auto');
        el.classList.add('me-auto');
    });
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check for stored preference
    const savedLang = localStorage.getItem('preferred-language');
    if (savedLang === 'en') {
        switchToEnglish();
    } else {
        // Default to Arabic
        switchToArabic();
    }
});

// Export for use in other scripts
window.toggleLanguage = toggleLanguage;
window.switchToEnglish = switchToEnglish;
window.switchToArabic = switchToArabic;