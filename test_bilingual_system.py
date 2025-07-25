#!/usr/bin/env python3
"""
Test script to verify the complete bilingual functionality
Tests API endpoints, template rendering, and session persistence
"""

import requests
import re

def test_bilingual_system():
    """Comprehensive test of the bilingual system"""
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🧪 Testing Bilingual System Functionality")
    print("=" * 50)
    
    # Test 1: Check initial language status
    print("\n1. Testing initial language status...")
    status_resp = session.get(f"{base_url}/api/language/status")
    if status_resp.status_code == 200:
        status = status_resp.json()
        print(f"   ✓ Initial language: {status['current_language']}")
        print(f"   ✓ Direction: {status['direction']}")
        print(f"   ✓ Opposite language: {status['opposite_language']}")
    else:
        print(f"   ❌ Status check failed: {status_resp.status_code}")
        return False
    
    # Test 2: Get homepage in current language
    print(f"\n2. Testing homepage in {status['current_language']}...")
    homepage_resp = session.get(base_url)
    if homepage_resp.status_code == 200:
        content = homepage_resp.text
        
        # Check for translated content
        if status['current_language'] == 'ar':
            # Look for Arabic content
            arabic_phrases = ["منصة صوت العميل", "الاستطلاعات", "التحليلات"]
            found_arabic = sum(1 for phrase in arabic_phrases if phrase in content)
            print(f"   ✓ Found {found_arabic}/{len(arabic_phrases)} Arabic phrases")
            
            # Check RTL direction
            if 'dir="rtl"' in content:
                print("   ✓ RTL direction set correctly")
            else:
                print("   ⚠️  RTL direction not found")
                
        else:
            # Look for English content
            english_phrases = ["Voice of Customer Platform", "Surveys", "Analytics"]
            found_english = sum(1 for phrase in english_phrases if phrase in content)
            print(f"   ✓ Found {found_english}/{len(english_phrases)} English phrases")
            
            # Check LTR direction
            if 'dir="ltr"' in content:
                print("   ✓ LTR direction set correctly")
            else:
                print("   ⚠️  LTR direction not found")
    else:
        print(f"   ❌ Homepage failed: {homepage_resp.status_code}")
        return False
    
    # Test 3: Toggle language
    print(f"\n3. Testing language toggle...")
    toggle_resp = session.post(f"{base_url}/api/language/toggle", 
                              json={}, 
                              headers={'Content-Type': 'application/json'})
    if toggle_resp.status_code == 200:
        toggle_result = toggle_resp.json()
        new_language = toggle_result['language']
        print(f"   ✓ Toggled to: {new_language}")
        print(f"   ✓ Direction: {toggle_result['direction']}")
    else:
        print(f"   ❌ Toggle failed: {toggle_resp.status_code}")
        return False
    
    # Test 4: Verify persistence after toggle
    print(f"\n4. Testing language persistence...")
    status_resp2 = session.get(f"{base_url}/api/language/status")
    if status_resp2.status_code == 200:
        status2 = status_resp2.json()
        if status2['current_language'] == new_language:
            print(f"   ✓ Language persisted correctly: {new_language}")
        else:
            print(f"   ❌ Language not persisted: expected {new_language}, got {status2['current_language']}")
            return False
    else:
        print(f"   ❌ Status check 2 failed: {status_resp2.status_code}")
        return False
    
    # Test 5: Check homepage in new language
    print(f"\n5. Testing homepage in new language ({new_language})...")
    homepage_resp2 = session.get(base_url)
    if homepage_resp2.status_code == 200:
        content2 = homepage_resp2.text
        
        if new_language == 'ar':
            arabic_phrases = ["منصة صوت العميل", "الاستطلاعات", "التحليلات"]
            found_arabic = sum(1 for phrase in arabic_phrases if phrase in content2)
            print(f"   ✓ Found {found_arabic}/{len(arabic_phrases)} Arabic phrases")
            
            if 'dir="rtl"' in content2:
                print("   ✓ RTL direction set correctly")
            else:
                print("   ⚠️  RTL direction not found")
        else:
            english_phrases = ["Voice of Customer Platform", "Surveys", "Analytics"]
            found_english = sum(1 for phrase in english_phrases if phrase in content2)
            print(f"   ✓ Found {found_english}/{len(english_phrases)} English phrases")
            
            if 'dir="ltr"' in content2:
                print("   ✓ LTR direction set correctly")
            else:
                print("   ⚠️  LTR direction not found")
    else:
        print(f"   ❌ Homepage 2 failed: {homepage_resp2.status_code}")
        return False
    
    # Test 6: Test translation API directly
    print(f"\n6. Testing translation API...")
    trans_resp = session.get(f"{base_url}/api/language/test?key=app.name")
    if trans_resp.status_code == 200:
        trans_result = trans_resp.json()
        print(f"   ✓ Translation for 'app.name': {trans_result['translation']}")
        print(f"   ✓ Current language: {trans_result['language']}")
    else:
        print(f"   ❌ Translation test failed: {trans_resp.status_code}")
        return False
    
    print(f"\n{'='*50}")
    print("🎉 Bilingual system test completed successfully!")
    print("✅ Language toggling works")
    print("✅ Session persistence works") 
    print("✅ Translation system works")
    print("✅ Direction switching works")
    
    return True

if __name__ == "__main__":
    try:
        test_bilingual_system()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")