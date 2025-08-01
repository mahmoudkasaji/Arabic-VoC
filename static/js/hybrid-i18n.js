/**
 * Hybrid I18N JavaScript Engine
 * Provides instant language switching without page reload
 */

class HybridI18N {
    constructor() {
        this.currentLanguage = 'ar';
        this.translations = {};
        this.isRTL = true;
        this.initialized = false;
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    async init() {
        console.log('🌐 Initializing Hybrid I18N system...');
        
        try {
            // Get current status from server
            const response = await fetch('/api/i18n/status');
            if (response.ok) {
                const status = await response.json();
                this.currentLanguage = status.current_language;
                this.translations = status.translations;
                this.isRTL = status.direction === 'rtl';
                
                console.log(`✅ I18N initialized - Language: ${this.currentLanguage}, Direction: ${status.direction}`);
            }
            
            // Set up language switcher
            this.setupLanguageSwitcher();
            
            // Apply initial language state
            this.applyLanguageToDOM();
            
            this.initialized = true;
            
        } catch (error) {
            console.error('❌ Failed to initialize I18N system:', error);
        }
    }
    
    setupLanguageSwitcher() {
        // Find language toggle buttons with multiple selectors
        const selectors = [
            '.hybrid-lang-toggle',
            '[href="/language/toggle"]',
            'a[href*="language/toggle"]',
            '.btn[href*="language"]'
        ];
        
        let toggleButtons = [];
        selectors.forEach(selector => {
            const found = document.querySelectorAll(selector);
            toggleButtons.push(...found);
        });
        
        // Remove duplicates
        toggleButtons = [...new Set(toggleButtons)];
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('🔄 Language toggle clicked!');
                this.switchLanguage();
            });
        });
        
        console.log(`🔧 Set up ${toggleButtons.length} language toggle buttons`);
        console.log('Button details:', toggleButtons.map(b => ({ class: b.className, href: b.href })));
    }
    
    async switchLanguage() {
        const targetLanguage = this.currentLanguage === 'ar' ? 'en' : 'ar';
        
        console.log(`🔄 Switching language from ${this.currentLanguage} to ${targetLanguage}`);
        
        // Show loading state
        this.showLoadingState();
        
        try {
            // Switch language on server
            const response = await fetch(`/api/i18n/switch/${targetLanguage}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                const result = await response.json();
                
                console.log('🎯 Server response:', result);
                
                // Update local state
                this.currentLanguage = result.language;
                this.translations = result.translations;
                this.isRTL = result.direction === 'rtl';
                
                console.log(`📊 Updated state: lang=${this.currentLanguage}, isRTL=${this.isRTL}, translations keys=${Object.keys(this.translations).length}`);
                
                // Apply to DOM instantly
                this.applyLanguageToDOM();
                
                console.log(`✅ Language switched to ${this.currentLanguage}`);
                
                // Show success feedback
                this.showSuccessFeedback();
                
            } else {
                throw new Error('Server language switch failed');
            }
            
        } catch (error) {
            console.error('❌ Language switch failed:', error);
            this.showErrorFeedback();
        } finally {
            this.hideLoadingState();
        }
    }
    
    applyLanguageToDOM() {
        // Update HTML lang and dir attributes
        document.documentElement.lang = this.currentLanguage;
        document.documentElement.dir = this.isRTL ? 'rtl' : 'ltr';
        document.body.dir = this.isRTL ? 'rtl' : 'ltr';
        
        // Update all translatable elements
        this.translateElements();
        
        // Update language button text
        this.updateLanguageButton();
        
        // Apply RTL/LTR styling
        this.applyDirectionStyling();
        
        console.log(`🎨 Applied ${this.currentLanguage} language to DOM (${this.isRTL ? 'RTL' : 'LTR'})`);
    }
    
    translateElements() {
        // Find all elements with data-i18n attributes
        const elements = document.querySelectorAll('[data-i18n]');
        
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.getTranslation(key);
            
            console.log(`🔍 Translating: ${key} -> ${translation}`);
            
            if (translation) {
                // Preserve icons and other HTML content while updating text
                const icon = element.querySelector('i');
                const iconHTML = icon ? icon.outerHTML + ' ' : '';
                
                if (element.tagName === 'TITLE') {
                    element.textContent = translation;
                } else if (iconHTML) {
                    element.innerHTML = iconHTML + translation;
                } else {
                    element.textContent = translation;
                }
            }
        });
        
        // Handle special cases - app name in various locations
        this.translateSpecialElements();
        
        console.log(`📝 Translated ${elements.length} elements`);
    }
    
    translateSpecialElements() {
        // Translate page title
        const title = this.getTranslation('app.name');
        if (title) {
            document.title = title;
            console.log(`📄 Updated page title: ${title}`);
        }
        
        // Translate navbar brand
        const navbarBrands = document.querySelectorAll('.navbar-brand');
        navbarBrands.forEach(brand => {
            const icon = brand.querySelector('i');
            const iconHTML = icon ? icon.outerHTML + ' ' : '';
            brand.innerHTML = iconHTML + title;
            console.log(`🏷️ Updated navbar brand: ${title}`);
        });
        
        // Translate navigation items
        this.translateNavigation();
        
        // Translate any other elements using translate filter format
        this.translateFilterElements();
    }
    
    translateNavigation() {
        const navItems = {
            'surveys': 'navigation.surveys_dropdown.title',
            'analytics': 'navigation.analytics_dropdown.title',
            'integrations': 'navigation.integrations_dropdown.title',
            'settings': 'navigation.settings_dropdown.title'
        };
        
        Object.entries(navItems).forEach(([id, key]) => {
            const element = document.querySelector(`[data-nav="${id}"]`);
            if (element) {
                const translation = this.getTranslation(key);
                if (translation) {
                    const icon = element.querySelector('i');
                    const iconHTML = icon ? icon.outerHTML + ' ' : '';
                    element.innerHTML = iconHTML + translation;
                }
            }
        });
    }
    
    updateLanguageButton() {
        // Update language toggle button text
        const toggleButtons = document.querySelectorAll('.hybrid-lang-toggle, [href="/language/toggle"]');
        const buttonText = this.getTranslation('language.switch_to');
        const tooltip = this.getTranslation('language.toggle_tooltip');
        
        console.log(`🔘 Found ${toggleButtons.length} language buttons to update`);
        console.log(`📝 Button text: ${buttonText}, Tooltip: ${tooltip}`);
        
        toggleButtons.forEach(button => {
            // Update the text span inside the button
            const textSpan = button.querySelector('[data-i18n="language.switch_to"]');
            if (textSpan && buttonText) {
                textSpan.textContent = buttonText;
                console.log(`✅ Updated button text to: ${buttonText}`);
            }
            
            // Update tooltip
            if (tooltip) {
                button.title = tooltip;
            }
        });
    }
    
    translateFilterElements() {
        // Handle common translation patterns that might not have data-i18n
        const commonSelectors = [
            'h1, h2, h3, h4, h5, h6',
            '.nav-link',
            '.dropdown-item',
            '.btn-text',
            'p, span'
        ];
        
        // Look for elements that might contain untranslated text
        commonSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                // Skip if already has data-i18n
                if (element.hasAttribute('data-i18n')) return;
                
                // Skip if contains only icons or complex HTML
                if (element.querySelector('i, img, svg') && element.textContent.trim().length < 3) return;
                
                // Try to find matching translation key
                const text = element.textContent.trim();
                if (text && text.length > 0) {
                    // Check if we have a direct translation
                    const translation = this.findTranslationByValue(text);
                    if (translation) {
                        element.textContent = translation;
                        console.log(`🔄 Found and updated: "${text}" -> "${translation}"`);
                    }
                }
            });
        });
    }
    
    findTranslationByValue(searchText) {
        // Search through translations to find matching text and return translation
        const searchLower = searchText.toLowerCase();
        
        // Search through all translation categories
        for (const category in this.translations) {
            for (const key in this.translations[category]) {
                const value = this.translations[category][key];
                if (typeof value === 'string') {
                    // Check if this matches the current opposite language
                    if (this.currentLanguage === 'en') {
                        // Currently English, so search Arabic text and return English
                        // This is complex without reverse lookup, skip for now
                    }
                }
            }
        }
        
        return null;
    }
    
    applyDirectionStyling() {
        // Add direction-specific CSS classes
        document.body.classList.remove('rtl', 'ltr');
        document.body.classList.add(this.isRTL ? 'rtl' : 'ltr');
        
        // Update any direction-dependent elements
        const containers = document.querySelectorAll('.container, .container-fluid');
        containers.forEach(container => {
            container.style.direction = this.isRTL ? 'rtl' : 'ltr';
        });
    }
    
    getTranslation(key) {
        // Navigate nested object keys (e.g., 'app.name' -> translations.app.name)
        const keys = key.split('.');
        let value = this.translations;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return null;
            }
        }
        
        return typeof value === 'string' ? value : null;
    }
    
    // UI Feedback Methods
    showLoadingState() {
        const toggleButtons = document.querySelectorAll('.hybrid-lang-toggle, [href="/language/toggle"]');
        toggleButtons.forEach(button => {
            button.style.pointerEvents = 'none';
            button.style.opacity = '0.6';
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-spinner fa-spin';
            }
        });
    }
    
    hideLoadingState() {
        const toggleButtons = document.querySelectorAll('.hybrid-lang-toggle, [href="/language/toggle"]');
        toggleButtons.forEach(button => {
            button.style.pointerEvents = 'auto';
            button.style.opacity = '1';
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-globe';
            }
        });
    }
    
    showSuccessFeedback() {
        // Brief success animation
        const toggleButtons = document.querySelectorAll('[href="/language/toggle"]');
        toggleButtons.forEach(button => {
            button.style.transform = 'scale(1.1)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 200);
        });
    }
    
    showErrorFeedback() {
        console.error('Language switch failed - refreshing page as fallback');
        // Fallback to page refresh if JavaScript switching fails
        window.location.reload();
    }
}

// Initialize global instance
window.HybridI18N = new HybridI18N();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HybridI18N;
}