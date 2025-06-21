#!/usr/bin/env python3
"""
Automated i18n Template Generator for Arabic VoC Platform
Generates standardized language toggle implementation for new pages
"""

import os
import json

class I18nTemplateGenerator:
    def __init__(self):
        self.template_config = {
            "js_template": "static/js/simple-lang-toggle.js",
            "pages_config": "scripts/i18n-pages-config.json"
        }
    
    def generate_page_template(self, page_name, elements):
        """Generate complete i18n implementation for a new page"""
        
        # 1. Generate HTML template with proper IDs
        html_template = self._generate_html_template(page_name, elements)
        
        # 2. Generate JavaScript additions
        js_additions = self._generate_js_additions(page_name, elements)
        
        # 3. Generate translation entries
        translation_entries = self._generate_translation_entries(page_name, elements)
        
        return {
            "html_template": html_template,
            "js_additions": js_additions,
            "translation_entries": translation_entries,
            "implementation_steps": self._generate_implementation_steps(page_name)
        }
    
    def _generate_html_template(self, page_name, elements):
        """Generate HTML template with proper i18n structure"""
        template = f"""
<!-- Language Toggle Button (add to navigation) -->
<button id="langToggle" class="btn btn-primary me-3" onclick="toggleLanguage()">
    <i class="fas fa-globe me-1"></i>
    <span id="langText">English</span>
</button>

<!-- {page_name.title()} Page Elements -->
"""
        
        for element in elements:
            element_type = element.get('type', 'text')
            element_id = f"{page_name}-{element['key']}-text"
            
            if element_type == 'text':
                template += f'<span id="{element_id}">{element["ar_text"]}</span>\n'
            elif element_type == 'heading':
                level = element.get('level', 'h1')
                template += f'<{level} id="{element_id}">{element["ar_text"]}</{level}>\n'
            elif element_type == 'placeholder':
                input_id = element['input_id']
                template += f'<input id="{input_id}" placeholder="{element["ar_text"]}" />\n'
        
        return template
    
    def _generate_js_additions(self, page_name, elements):
        """Generate JavaScript ID mappings and placeholder mappings"""
        
        # ID mappings for text elements
        id_mappings = {}
        placeholder_mappings = {}
        
        for element in elements:
            if element.get('type') == 'placeholder':
                placeholder_mappings[element['input_id']] = f"{page_name}-{element['key']}-placeholder"
            else:
                element_id = f"{page_name}-{element['key']}-text"
                translation_key = f"{page_name}-{element['key']}"
                id_mappings[element_id] = translation_key
        
        js_code = f"""
// Add to idMappings in simple-lang-toggle.js:
{json.dumps(id_mappings, indent=8)[1:-1]},

// Add to placeholderMappings in simple-lang-toggle.js:
{json.dumps(placeholder_mappings, indent=8)[1:-1]},
"""
        return js_code
    
    def _generate_translation_entries(self, page_name, elements):
        """Generate translation entries for both Arabic and English"""
        
        ar_translations = {}
        en_translations = {}
        
        for element in elements:
            key = f"{page_name}-{element['key']}"
            if element.get('type') == 'placeholder':
                key += "-placeholder"
            
            ar_translations[key] = element['ar_text']
            en_translations[key] = element['en_text']
        
        return {
            "arabic": ar_translations,
            "english": en_translations
        }
    
    def _generate_implementation_steps(self, page_name):
        """Generate step-by-step implementation guide"""
        return [
            f"1. Add language toggle button to {page_name}.html navigation",
            f"2. Replace static text with ID-based elements in {page_name}.html",
            "3. Add generated ID mappings to static/js/simple-lang-toggle.js",
            "4. Add generated translations to static/js/simple-lang-toggle.js",
            "5. Include simple-lang-toggle.js script in page head",
            "6. Test language toggle functionality"
        ]
    
    def generate_for_common_pages(self):
        """Generate templates for common page types"""
        
        common_pages = {
            "dashboard": [
                {"key": "title", "type": "heading", "level": "h1", "ar_text": "لوحة التحكم", "en_text": "Dashboard"},
                {"key": "subtitle", "type": "text", "ar_text": "نظرة عامة على البيانات", "en_text": "Data Overview"},
                {"key": "search", "type": "placeholder", "input_id": "searchInput", "ar_text": "البحث...", "en_text": "Search..."}
            ],
            "profile": [
                {"key": "title", "type": "heading", "level": "h1", "ar_text": "الملف الشخصي", "en_text": "Profile"},
                {"key": "name-label", "type": "text", "ar_text": "الاسم:", "en_text": "Name:"},
                {"key": "email-label", "type": "text", "ar_text": "البريد الإلكتروني:", "en_text": "Email:"}
            ],
            "settings": [
                {"key": "title", "type": "heading", "level": "h1", "ar_text": "الإعدادات", "en_text": "Settings"},
                {"key": "language-label", "type": "text", "ar_text": "اللغة:", "en_text": "Language:"},
                {"key": "save-btn", "type": "text", "ar_text": "حفظ", "en_text": "Save"}
            ]
        }
        
        templates = {}
        for page_name, elements in common_pages.items():
            templates[page_name] = self.generate_page_template(page_name, elements)
        
        return templates

def main():
    generator = I18nTemplateGenerator()
    
    print("I18n Template Generator for Arabic VoC Platform")
    print("=" * 50)
    
    # Generate common page templates
    templates = generator.generate_for_common_pages()
    
    # Save templates to file
    output_file = "scripts/i18n-templates.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(templates, f, indent=2, ensure_ascii=False)
    
    print(f"Generated templates saved to: {output_file}")
    print("\nAvailable templates:")
    for page_name in templates.keys():
        print(f"  - {page_name}")
    
    print("\nUsage:")
    print("1. Copy HTML template to your new page")
    print("2. Add JS mappings to simple-lang-toggle.js")
    print("3. Add translations to simple-lang-toggle.js")
    print("4. Include script in page head")
    print("5. Test functionality")

if __name__ == "__main__":
    main()