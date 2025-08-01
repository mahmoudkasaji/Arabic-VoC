"""
Smart Template Processor for Voice of Customer Platform
Automated solution for updating hardcoded templates without manual replacement
"""

import os
import re
import json
from typing import Dict, List, Tuple
from utils.language_manager import language_manager


class SmartTemplateProcessor:
    """
    Intelligent template processor that automatically finds and replaces
    hardcoded text with translation keys
    """
    
    def __init__(self):
        self.templates_dir = 'templates'
        self.translation_mappings = self._load_translation_mappings()
        
    def _load_translation_mappings(self) -> Dict[str, str]:
        """Load mappings between hardcoded text and translation keys"""
        
        # Arabic to translation key mappings
        arabic_mappings = {
            'جهات الاتصال': 'navigation.contacts_dropdown.title',
            'إدارة جهات الاتصال': 'navigation.contacts_dropdown.management',
            'قائمة جهات الاتصال': 'navigation.contacts_dropdown.list',
            'إدارة وتنظيم جهات الاتصال': 'navigation.contacts_dropdown.manage_organize',
            'التحليلات الأساسية': 'navigation.analytics_basic.title',
            'لوحة المؤشرات الرئيسية': 'navigation.analytics_basic.kpi_dashboard',
            'مقاييس الأداء الرئيسية والرؤى التشغيلية': 'navigation.analytics_basic.kpi_subtitle',
            'تحليل النصوص بالذكاء الاصطناعي': 'navigation.analytics_basic.ai_text_analysis',
            'تحليل المشاعر والمواضيع باستخدام نماذج الذكاء الاصطناعي': 'navigation.analytics_basic.ai_subtitle',
            'توزيع الاستطلاعات': 'navigation.surveys_distribution.title',
            'معالج 3 خطوات لتوزيع الاستطلاعات عبر قنوات متعددة': 'navigation.surveys_distribution.subtitle',
            'إدارة التكاملات والذكاء الاصطناعي': 'navigation.integrations_ai.title',
            'مراقبة وإدارة جميع التكاملات التقنية ونماذج الذكاء الاصطناعي': 'navigation.integrations_ai.subtitle',
            'إدارة الاستطلاعات': 'surveys.title',
            'منصة صوت العميل': 'app.name'
        }
        
        return arabic_mappings
    
    def find_hardcoded_text(self, file_path: str) -> List[Tuple[str, int, str]]:
        """
        Find hardcoded Arabic text in template files
        Returns list of (text, line_number, suggested_key)
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Skip lines that already use translation filters
                if '| translate' in line:
                    continue
                
                # Find Arabic text that should be translated
                for arabic_text, translation_key in self.translation_mappings.items():
                    if arabic_text in line and not line.strip().startswith('<!--'):
                        findings.append((arabic_text, line_num, translation_key))
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return findings
    
    def auto_replace_hardcoded_text(self, file_path: str, dry_run: bool = True) -> Dict:
        """
        Automatically replace hardcoded text with translation keys
        """
        replacements_made = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace hardcoded Arabic text with translation keys
            for arabic_text, translation_key in self.translation_mappings.items():
                if arabic_text in content:
                    # Create replacement pattern
                    replacement = f"{{{{ '{translation_key}' | translate }}}}"
                    
                    # Replace only if not already a translation
                    pattern = re.escape(arabic_text)
                    if re.search(f'{pattern}(?![^{{]*translate)', content):
                        content = re.sub(pattern, replacement, content)
                        replacements_made.append({
                            'original': arabic_text,
                            'replacement': replacement,
                            'key': translation_key
                        })
            
            # Write back if not dry run and changes were made
            if not dry_run and content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return {
                'file': file_path,
                'replacements': replacements_made,
                'dry_run': dry_run,
                'changed': content != original_content
            }
            
        except Exception as e:
            return {
                'file': file_path,
                'error': str(e),
                'replacements': [],
                'dry_run': dry_run,
                'changed': False
            }
    
    def scan_all_templates(self) -> Dict:
        """Scan all template files for hardcoded text"""
        results = {
            'files_scanned': 0,
            'files_with_issues': 0,
            'total_issues': 0,
            'details': []
        }
        
        for root, dirs, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    findings = self.find_hardcoded_text(file_path)
                    
                    results['files_scanned'] += 1
                    
                    if findings:
                        results['files_with_issues'] += 1
                        results['total_issues'] += len(findings)
                        results['details'].append({
                            'file': file_path,
                            'issues': findings
                        })
        
        return results
    
    def fix_all_templates(self, dry_run: bool = True) -> Dict:
        """Fix all templates automatically"""
        results = {
            'files_processed': 0,
            'files_changed': 0,
            'total_replacements': 0,
            'details': [],
            'dry_run': dry_run
        }
        
        for root, dirs, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    fix_result = self.auto_replace_hardcoded_text(file_path, dry_run)
                    
                    results['files_processed'] += 1
                    
                    if fix_result['changed']:
                        results['files_changed'] += 1
                        results['total_replacements'] += len(fix_result['replacements'])
                    
                    if fix_result['replacements'] or fix_result.get('error'):
                        results['details'].append(fix_result)
        
        return results


def create_translation_key_suggestions(text: str) -> List[str]:
    """Generate suggested translation keys for new text"""
    # Simple key generation logic
    key_base = text.lower()
    key_base = re.sub(r'[^\w\s]', '', key_base)  # Remove special chars
    key_base = re.sub(r'\s+', '_', key_base)      # Replace spaces with underscores
    
    suggestions = [
        f"navigation.{key_base}",
        f"general.{key_base}",
        f"buttons.{key_base}",
        f"messages.{key_base}"
    ]
    
    return suggestions


def main():
    """Main function for testing the template processor"""
    processor = SmartTemplateProcessor()
    
    print("🔍 Scanning templates for hardcoded text...")
    scan_results = processor.scan_all_templates()
    
    print(f"📊 Scan Results:")
    print(f"  Files scanned: {scan_results['files_scanned']}")
    print(f"  Files with issues: {scan_results['files_with_issues']}")
    print(f"  Total issues: {scan_results['total_issues']}")
    
    if scan_results['details']:
        print("\n📋 Issues found:")
        for detail in scan_results['details']:
            print(f"\n  📄 {detail['file']}:")
            for issue in detail['issues']:
                text, line, key = issue
                print(f"    Line {line}: '{text}' → {key}")
    
    print("\n🔧 Running dry-run fix...")
    fix_results = processor.fix_all_templates(dry_run=True)
    
    print(f"📊 Fix Results (Dry Run):")
    print(f"  Files processed: {fix_results['files_processed']}")
    print(f"  Files that would change: {fix_results['files_changed']}")
    print(f"  Total replacements: {fix_results['total_replacements']}")
    
    if fix_results['details']:
        print("\n📋 Potential changes:")
        for detail in fix_results['details']:
            if detail['replacements']:
                print(f"\n  📄 {detail['file']}:")
                for replacement in detail['replacements']:
                    print(f"    '{replacement['original']}' → {replacement['replacement']}")


if __name__ == "__main__":
    main()