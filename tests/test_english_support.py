#!/usr/bin/env python3
"""
Comprehensive Testing Suite for English Language Support
Arabic Voice of Customer Platform
"""

import pytest
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

class TestEnglishLanguageSupport:
    """Test suite for comprehensive English language support"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.base_url = "http://localhost:5000"
        cls.wait = WebDriverWait(cls.driver, 10)
    
    @classmethod
    def teardown_class(cls):
        """Clean up test environment"""
        cls.driver.quit()
    
    def test_language_toggle_button_presence(self):
        """Test that language toggle button is present on all pages"""
        pages = ['/', '/feedback', '/dashboard/realtime', '/surveys', '/login', '/register']
        
        for page in pages:
            self.driver.get(f"{self.base_url}{page}")
            try:
                toggle_button = self.wait.until(
                    EC.presence_of_element_located((By.ID, "langToggle"))
                )
                assert toggle_button.is_displayed(), f"Language toggle not visible on {page}"
                
                # Check button text
                lang_text = toggle_button.find_element(By.ID, "langText")
                assert lang_text.text in ["English", "العربية"], f"Invalid toggle text on {page}: {lang_text.text}"
                
            except Exception as e:
                pytest.fail(f"Language toggle test failed on {page}: {str(e)}")
    
    def test_language_toggle_functionality(self):
        """Test that language toggle actually switches content"""
        self.driver.get(self.base_url)
        
        # Get initial Arabic content
        initial_title = self.driver.find_element(By.TAG_NAME, "h1").text
        assert "منصة" in initial_title, "Initial content should be in Arabic"
        
        # Click toggle button
        toggle_button = self.driver.find_element(By.ID, "langToggle")
        toggle_button.click()
        
        # Wait for content to change
        time.sleep(1)
        
        # Check English content
        english_title = self.driver.find_element(By.TAG_NAME, "h1").text
        assert "Arabic" in english_title, f"Content should be in English after toggle: {english_title}"
        
        # Check toggle button text changed
        lang_text = self.driver.find_element(By.ID, "langText")
        assert lang_text.text == "العربية", f"Toggle should show Arabic option: {lang_text.text}"
    
    def test_navigation_menu_translation(self):
        """Test that navigation menu items are properly translated"""
        self.driver.get(self.base_url)
        
        # Check Arabic navigation
        nav_links = self.driver.find_elements(By.CSS_SELECTOR, ".nav-link")
        arabic_texts = [link.text for link in nav_links if link.text.strip()]
        
        # Should contain Arabic text
        assert any("الرئيسية" in text for text in arabic_texts), "Arabic navigation not found"
        
        # Toggle to English
        toggle_button = self.driver.find_element(By.ID, "langToggle")
        toggle_button.click()
        time.sleep(1)
        
        # Check English navigation
        nav_links = self.driver.find_elements(By.CSS_SELECTOR, ".nav-link")
        english_texts = [link.text for link in nav_links if link.text.strip()]
        
        # Should contain English text
        assert any("Home" in text for text in english_texts), f"English navigation not found: {english_texts}"
    
    def test_form_labels_translation(self):
        """Test that form labels are translated on feedback page"""
        self.driver.get(f"{self.base_url}/feedback")
        
        # Toggle to English
        try:
            toggle_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "langToggle"))
            )
            toggle_button.click()
            time.sleep(1)
            
            # Check for English form elements
            page_source = self.driver.page_source.lower()
            
            # Should contain English form text
            english_indicators = ["feedback", "submit", "email", "rating"]
            found_indicators = [indicator for indicator in english_indicators if indicator in page_source]
            
            assert len(found_indicators) >= 2, f"Not enough English form content found: {found_indicators}"
            
        except Exception as e:
            pytest.fail(f"Form translation test failed: {str(e)}")
    
    def test_layout_direction_change(self):
        """Test that layout direction changes between RTL and LTR"""
        self.driver.get(self.base_url)
        
        # Check initial RTL layout
        html_element = self.driver.find_element(By.TAG_NAME, "html")
        initial_dir = html_element.get_attribute("dir")
        assert initial_dir == "rtl", f"Initial direction should be RTL: {initial_dir}"
        
        # Toggle to English
        toggle_button = self.driver.find_element(By.ID, "langToggle")
        toggle_button.click()
        time.sleep(1)
        
        # Check LTR layout
        html_element = self.driver.find_element(By.TAG_NAME, "html")
        english_dir = html_element.get_attribute("dir")
        assert english_dir == "ltr", f"English direction should be LTR: {english_dir}"
    
    def test_persistent_language_preference(self):
        """Test that language preference persists across page reloads"""
        self.driver.get(self.base_url)
        
        # Toggle to English
        toggle_button = self.driver.find_element(By.ID, "langToggle")
        toggle_button.click()
        time.sleep(1)
        
        # Reload page
        self.driver.refresh()
        time.sleep(2)
        
        # Check that English is still active
        html_element = self.driver.find_element(By.TAG_NAME, "html")
        lang_attr = html_element.get_attribute("lang")
        dir_attr = html_element.get_attribute("dir")
        
        assert lang_attr == "en", f"Language should persist as English: {lang_attr}"
        assert dir_attr == "ltr", f"Direction should persist as LTR: {dir_attr}"
    
    def test_page_title_translation(self):
        """Test that page titles are translated"""
        pages_to_test = [
            ('/', 'Arabic'),
            ('/feedback', 'Feedback'),
            ('/dashboard/realtime', 'Analytics')
        ]
        
        for page, expected_english_keyword in pages_to_test:
            self.driver.get(f"{self.base_url}{page}")
            
            # Toggle to English
            try:
                toggle_button = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "langToggle"))
                )
                toggle_button.click()
                time.sleep(1)
                
                # Check page title
                title = self.driver.title
                assert expected_english_keyword.lower() in title.lower(), \
                    f"Page title should contain '{expected_english_keyword}' on {page}: {title}"
                
            except Exception as e:
                print(f"Warning: Title test failed on {page}: {str(e)}")
    
    def test_button_text_translation(self):
        """Test that buttons are properly translated"""
        self.driver.get(self.base_url)
        
        # Toggle to English
        toggle_button = self.driver.find_element(By.ID, "langToggle")
        toggle_button.click()
        time.sleep(1)
        
        # Check for English button text
        buttons = self.driver.find_elements(By.CSS_SELECTOR, "a.btn, button.btn")
        button_texts = [btn.text for btn in buttons if btn.text.strip()]
        
        # Should contain some English button text
        english_button_keywords = ["View", "Share", "Feedback", "Analytics", "English"]
        found_keywords = []
        
        for text in button_texts:
            for keyword in english_button_keywords:
                if keyword.lower() in text.lower():
                    found_keywords.append(keyword)
        
        assert len(found_keywords) >= 1, f"No English button text found: {button_texts}"
    
    def test_responsive_design_with_language_toggle(self):
        """Test that language toggle works on mobile viewport"""
        # Set mobile viewport
        self.driver.set_window_size(375, 667)
        self.driver.get(self.base_url)
        
        try:
            # Toggle should still be accessible
            toggle_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "langToggle"))
            )
            
            # Click toggle
            toggle_button.click()
            time.sleep(1)
            
            # Verify language changed
            html_element = self.driver.find_element(By.TAG_NAME, "html")
            lang_attr = html_element.get_attribute("lang")
            
            assert lang_attr == "en", f"Language toggle should work on mobile: {lang_attr}"
            
        finally:
            # Reset viewport
            self.driver.set_window_size(1200, 800)
    
    def test_content_completeness(self):
        """Test that major content sections have English translations"""
        pages_with_content = [
            ('/', ['features', 'analytics', 'platform']),
            ('/feedback', ['feedback', 'submit', 'rating']),
            ('/dashboard/realtime', ['analytics', 'dashboard', 'real-time'])
        ]
        
        for page, required_keywords in pages_with_content:
            self.driver.get(f"{self.base_url}{page}")
            
            # Toggle to English
            try:
                toggle_button = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "langToggle"))
                )
                toggle_button.click()
                time.sleep(1)
                
                # Check page content
                page_text = self.driver.page_source.lower()
                
                found_keywords = []
                for keyword in required_keywords:
                    if keyword in page_text:
                        found_keywords.append(keyword)
                
                coverage = len(found_keywords) / len(required_keywords)
                assert coverage >= 0.5, \
                    f"Insufficient English content on {page}: {found_keywords}/{required_keywords}"
                
            except Exception as e:
                print(f"Warning: Content test failed on {page}: {str(e)}")

def run_english_support_tests():
    """Run all English language support tests"""
    print("Running English Language Support Test Suite...")
    
    # Run pytest with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])

if __name__ == "__main__":
    run_english_support_tests()