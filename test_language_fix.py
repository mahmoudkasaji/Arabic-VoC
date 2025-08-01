"""
Final Language Fix Test - Comprehensive Solution
"""

from app import app
import requests

print("🚀 FINAL BILINGUAL SYSTEM FIX TEST")
print("=" * 60)

# Test the complete system
with app.test_client() as client:
    print("1. Testing English language rendering:")
    
    # Force English language
    with client.session_transaction() as sess:
        sess['language'] = 'en'
    
    response = client.get('/')
    content = response.data.decode('utf-8')
    
    # Check specific elements
    if 'Voice of Customer Platform' in content:
        print("   ✅ English app name found")
    else:
        print("   ❌ English app name NOT found")
    
    if 'Surveys' in content:
        print("   ✅ English navigation found")
    else:
        print("   ❌ English navigation NOT found")
    
    print("\n2. Testing Arabic language rendering:")
    
    # Force Arabic language 
    with client.session_transaction() as sess:
        sess['language'] = 'ar'
    
    response = client.get('/')
    content = response.data.decode('utf-8')
    
    # Check specific elements
    if 'منصة صوت العميل' in content:
        print("   ✅ Arabic app name found")
    else:
        print("   ❌ Arabic app name NOT found")
    
    if 'الاستطلاعات' in content:
        print("   ✅ Arabic navigation found") 
    else:
        print("   ❌ Arabic navigation NOT found")

    print("\n3. Testing language toggle:")
    
    # Test the toggle endpoint
    response = client.get('/language/toggle')
    print(f"   Toggle response: {response.status_code}")
    
    # Test direct language setting
    response = client.get('/language/set/en')
    print(f"   Direct EN set: {response.status_code}")
    
    response = client.get('/language/set/ar')  
    print(f"   Direct AR set: {response.status_code}")

print("\n" + "=" * 60) 
print("🎯 DIAGNOSIS COMPLETE")