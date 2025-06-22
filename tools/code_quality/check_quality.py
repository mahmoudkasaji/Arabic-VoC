#!/usr/bin/env python3
"""
Code quality checker for Arabic VoC Platform
Validates code standards, documentation, and best practices
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_syntax():
    """Check Python syntax across all Python files"""
    print("🔍 Checking Python syntax...")
    
    python_files = list(Path('.').rglob('*.py'))
    errors = []
    
    for file_path in python_files:
        if 'venv' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            subprocess.run(['python', '-m', 'py_compile', str(file_path)], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            errors.append(f"Syntax error in {file_path}")
    
    if errors:
        print(f"❌ {len(errors)} syntax errors found")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print(f"✅ All {len(python_files)} Python files have valid syntax")
        return True

def check_imports():
    """Check for common import issues"""
    print("🔍 Checking import structure...")
    
    # Look for circular imports and missing modules
    issues = []
    
    # This is a simplified check - in production you'd use more sophisticated tools
    python_files = list(Path('.').rglob('*.py'))
    
    for file_path in python_files:
        if 'venv' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for relative imports without package structure
            if 'from .' in content and '__init__.py' not in str(file_path):
                parent_dir = file_path.parent
                if not (parent_dir / '__init__.py').exists():
                    issues.append(f"Relative import in {file_path} without package structure")
                    
        except Exception as e:
            issues.append(f"Could not read {file_path}: {e}")
    
    if issues:
        print(f"⚠️  {len(issues)} import issues found")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ Import structure looks good")
        return True

def check_documentation():
    """Check documentation completeness"""
    print("🔍 Checking documentation...")
    
    required_docs = [
        'README.md',
        'README_ARABIC.md', 
        'QUICKSTART.md',
        'documentation/README.md',
        'testing/README.md'
    ]
    
    missing_docs = []
    for doc in required_docs:
        if not Path(doc).exists():
            missing_docs.append(doc)
    
    if missing_docs:
        print(f"❌ {len(missing_docs)} required documents missing:")
        for doc in missing_docs:
            print(f"  {doc}")
        return False
    else:
        print("✅ All required documentation present")
        return True

def check_test_coverage():
    """Check test file coverage"""
    print("🔍 Checking test coverage...")
    
    # Count Python files vs test files
    app_files = list(Path('app').rglob('*.py')) if Path('app').exists() else []
    test_files = list(Path('testing').rglob('test_*.py')) if Path('testing').exists() else []
    
    print(f"  Application files: {len(app_files)}")
    print(f"  Test files: {len(test_files)}")
    
    if len(test_files) == 0:
        print("❌ No test files found")
        return False
    elif len(test_files) < len(app_files) * 0.5:
        print("⚠️  Test coverage may be low")
        return True
    else:
        print("✅ Good test file coverage")
        return True

def check_arabic_files():
    """Check Arabic text files for encoding issues"""
    print("🔍 Checking Arabic text encoding...")
    
    # Find files likely to contain Arabic text
    arabic_files = []
    for pattern in ['*arabic*.py', '*arabic*.md', '*_arabic.md']:
        arabic_files.extend(Path('.').rglob(pattern))
    
    encoding_errors = []
    
    for file_path in arabic_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if file contains Arabic characters
            arabic_chars = any('\u0600' <= char <= '\u06FF' for char in content)
            if arabic_chars:
                print(f"  ✅ {file_path} - Arabic text detected and readable")
            else:
                print(f"  ⚠️  {file_path} - No Arabic text detected")
                
        except UnicodeDecodeError:
            encoding_errors.append(f"Encoding error in {file_path}")
        except Exception as e:
            encoding_errors.append(f"Could not read {file_path}: {e}")
    
    if encoding_errors:
        print(f"❌ {len(encoding_errors)} encoding errors:")
        for error in encoding_errors:
            print(f"  {error}")
        return False
    else:
        print("✅ All Arabic files have proper UTF-8 encoding")
        return True

def main():
    """Run all quality checks"""
    print("🚀 Arabic VoC Platform - Code Quality Check")
    print("==========================================")
    print()
    
    checks = [
        ("Python Syntax", check_python_syntax),
        ("Import Structure", check_imports),
        ("Documentation", check_documentation),
        ("Test Coverage", check_test_coverage),
        ("Arabic Encoding", check_arabic_files)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * (len(check_name) + 4))
        
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error running {check_name}: {e}")
            results.append((check_name, False))
        
        print()
    
    # Summary
    print("📊 Quality Check Summary")
    print("========================")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All quality checks passed!")
        return 0
    elif passed >= total * 0.8:
        print("⚠️  Most checks passed, minor issues detected")
        return 1
    else:
        print("🚨 Multiple quality issues detected")
        return 2

if __name__ == "__main__":
    sys.exit(main())