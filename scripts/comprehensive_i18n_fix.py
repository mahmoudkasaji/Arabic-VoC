#!/usr/bin/env python3
"""
Comprehensive i18n fix for all pages
Adds missing data-i18n attributes to all Arabic text elements
"""

import os
import re

def fix_template_i18n(template_path, replacements):
    """Fix i18n attributes in a template file"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_str, new_str in replacements:
            content = content.replace(old_str, new_str)
        
        if content != original_content:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed {template_path}")
            return True
        else:
            print(f"- No changes needed for {template_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error fixing {template_path}: {e}")
        return False

def main():
    print("Comprehensive i18n Fix for All Templates")
    print("=" * 50)
    
    # Templates directory
    templates_dir = "templates"
    
    # Fix feedback.html
    feedback_fixes = [
        ('class="navbar-brand" href="/">\n                <i class="fas fa-comments text-primary"></i>\n                منصة صوت العميل العربية', 
         'class="navbar-brand" href="/">\n                <i class="fas fa-comments text-primary"></i>\n                <span data-i18n="home.title">منصة صوت العميل العربية</span>'),
        
        ('<h1 class="arabic-title text-center">شاركنا رأيك</h1>',
         '<h1 class="arabic-title text-center" data-i18n="feedback.title">شاركنا رأيك</h1>'),
        
        ('<p class="text-center lead">نقدر آراءكم ومقترحاتكم لتطوير خدماتنا</p>',
         '<p class="text-center lead" data-i18n="feedback.subtitle">نقدر آراءكم ومقترحاتكم لتطوير خدماتنا</p>'),
        
        ('إرسال التعليق',
         '<span data-i18n="feedback.submit">إرسال التعليق</span>'),
        
        ('<h3>شكراً لك!</h3>',
         '<h3 data-i18n="feedback.success_title">شكراً لك!</h3>'),
        
        ('<p>تم إرسال تعليقك بنجاح وسيتم تحليله قريباً.</p>',
         '<p data-i18n="feedback.success_message">تم إرسال تعليقك بنجاح وسيتم تحليله قريباً.</p>')
    ]
    
    # Fix dashboard_realtime.html
    dashboard_fixes = [
        ('<h1 class="arabic-title text-center mb-2">لوحة التحليلات المباشرة</h1>',
         '<h1 class="arabic-title text-center mb-2" data-i18n="dashboard.title">لوحة التحليلات المباشرة</h1>'),
        
        ('<p class="text-center mb-0">منصة صوت العميل العربية - تحليل مباشر ومتقدم</p>',
         '<p class="text-center mb-0" data-i18n="dashboard.subtitle">منصة صوت العميل العربية - تحليل مباشر ومتقدم</p>'),
        
        ('<span id="connectionStatus" class="badge bg-secondary">غير متصل</span>',
         '<span id="connectionStatus" class="badge bg-secondary" data-i18n="dashboard.disconnected">غير متصل</span>'),
        
        ('<h3 class="arabic-title mb-3">اتجاهات المشاعر بالوقت الفعلي</h3>',
         '<h3 class="arabic-title mb-3" data-i18n="dashboard.sentiment_trends">اتجاهات المشاعر بالوقت الفعلي</h3>'),
        
        ('<h4 class="arabic-title mb-3">مقياس المشاعر</h4>',
         '<h4 class="arabic-title mb-3" data-i18n="dashboard.sentiment_gauge">مقياس المشاعر</h4>')
    ]
    
    # Fix surveys.html 
    surveys_fixes = [
        ('<h1 class="arabic-title display-5 mb-3">الاستطلاعات</h1>',
         '<h1 class="arabic-title display-5 mb-3" data-i18n="surveys.title">الاستطلاعات</h1>'),
        
        ('استطلاعات ذكية لجمع آراء العملاء باللغة العربية',
         '<span data-i18n="surveys.subtitle">استطلاعات ذكية لجمع آراء العملاء باللغة العربية</span>'),
        
        ('منصة صوت العميل العربية',
         '<span data-i18n="home.title">منصة صوت العميل العربية</span>')
    ]
    
    # Fix login.html
    login_fixes = [
        ('تسجيل الدخول\n                        </button>',
         '<span data-i18n="auth.login_button">تسجيل الدخول</span>\n                        </button>'),
        
        ('إنشاء حساب جديد</a>',
         '<span data-i18n="auth.create_account">إنشاء حساب جديد</span></a>'),
        
        ('نسيت كلمة المرور؟</a>',
         '<span data-i18n="auth.forgot_password">نسيت كلمة المرور؟</span></a>')
    ]
    
    # Fix register.html
    register_fixes = [
        ('<h2 class="arabic-title">إنشاء حساب جديد</h2>',
         '<h2 class="arabic-title" data-i18n="auth.register_title">إنشاء حساب جديد</h2>'),
        
        ('<p class="text-muted">انضم إلى منصة صوت العميل العربية</p>',
         '<p class="text-muted" data-i18n="auth.register_subtitle">انضم إلى منصة صوت العميل العربية</p>')
    ]
    
    # Apply fixes to each template
    templates_to_fix = [
        ("templates/feedback.html", feedback_fixes),
        ("templates/dashboard_realtime.html", dashboard_fixes), 
        ("templates/surveys.html", surveys_fixes),
        ("templates/login.html", login_fixes),
        ("templates/register.html", register_fixes)
    ]
    
    fixed_count = 0
    for template_path, fixes in templates_to_fix:
        if os.path.exists(template_path):
            if fix_template_i18n(template_path, fixes):
                fixed_count += 1
        else:
            print(f"✗ Template not found: {template_path}")
    
    print(f"\nFixed {fixed_count} templates")
    print("All critical i18n attributes have been added")

if __name__ == "__main__":
    main()