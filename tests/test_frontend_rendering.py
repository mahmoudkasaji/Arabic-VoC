"""
Frontend rendering tests for HTML/CSS validation
Tests Arabic RTL layout, Bootstrap components, and visual elements
"""

import pytest
import re
from bs4 import BeautifulSoup
from app import app

class TestHTMLStructure:
    """Test HTML structure and semantic elements"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_html5_document_structure(self):
        """Test proper HTML5 document structure"""
        pages = [
            '/analytics/executive',
            '/surveys/builder',
            '/integrations/sources',
            '/settings/account'
        ]
        
        for page in pages:
            response = self.client.get(page)
            assert response.status_code == 200
            
            soup = BeautifulSoup(response.data, 'html.parser')
            
            # Check HTML5 doctype (handle potential whitespace)
            soup_str = str(soup).strip()
            assert soup_str.startswith('<!DOCTYPE html>'), f"Page {page} missing HTML5 doctype"
            
            # Check required meta tags
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            assert viewport_meta is not None, f"Page {page} missing viewport meta tag"
            assert 'width=device-width' in viewport_meta.get('content', ''), f"Page {page} viewport not responsive"
            
            # Check charset
            charset_meta = soup.find('meta', attrs={'charset': True})
            assert charset_meta is not None, f"Page {page} missing charset meta tag"
            assert charset_meta.get('charset').upper() == 'UTF-8', f"Page {page} not using UTF-8"
    
    @pytest.mark.arabic
    def test_arabic_rtl_attributes(self):
        """Test Arabic RTL attributes are correctly set"""
        pages = ['/analytics/executive', '/surveys/builder', '/integrations/sources']
        
        for page in pages:
            response = self.client.get(page)
            soup = BeautifulSoup(response.data, 'html.parser')
            
            html_tag = soup.find('html')
            assert html_tag is not None, f"Page {page} missing html tag"
            assert html_tag.get('dir') == 'rtl', f"Page {page} missing RTL direction"
            assert html_tag.get('lang') == 'ar', f"Page {page} missing Arabic language"
    
    @pytest.mark.ui
    def test_semantic_html_elements(self):
        """Test semantic HTML elements are properly used"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for semantic navigation
        nav = soup.find('nav')
        assert nav is not None, "Missing semantic nav element"
        
        # Check for main content area
        main = soup.find('main') or soup.find('div', class_=re.compile(r'main|content'))
        assert main is not None, "Missing main content area"
        
        # Check for proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        assert len(headings) > 0, "No heading elements found"
        
        # Should have at least one h1
        h1_tags = soup.find_all('h1')
        assert len(h1_tags) >= 1, "Missing h1 tag"


class TestCSSAndStyling:
    """Test CSS classes and styling elements"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_bootstrap_css_integration(self):
        """Test Bootstrap CSS is properly integrated"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check Bootstrap CSS link
        assert 'bootstrap' in content.lower(), "Bootstrap CSS not found"
        assert 'css' in content.lower(), "CSS files not linked"
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for Bootstrap classes
        bootstrap_classes = [
            'container', 'container-fluid', 'row', 'col-', 
            'btn', 'navbar', 'dropdown', 'card'
        ]
        
        page_classes = set()
        for element in soup.find_all(class_=True):
            for cls in element.get('class', []):
                page_classes.add(cls)
        
        found_bootstrap = False
        for bs_class in bootstrap_classes:
            if any(bs_class in cls for cls in page_classes):
                found_bootstrap = True
                break
        
        assert found_bootstrap, f"No Bootstrap classes found. Found classes: {list(page_classes)[:10]}"
    
    @pytest.mark.arabic
    def test_arabic_font_integration(self):
        """Test Arabic fonts are properly integrated"""
        pages = ['/analytics/executive', '/surveys/builder']
        
        for page in pages:
            response = self.client.get(page)
            content = response.data.decode('utf-8')
            
            # Check for Arabic font families
            arabic_fonts = ['cairo', 'amiri', 'noto', 'droid arabic']
            font_found = any(font in content.lower() for font in arabic_fonts)
            assert font_found, f"Page {page} missing Arabic fonts"
            
            # Check for Google Fonts integration
            assert 'fonts.googleapis.com' in content or 'fonts.google.com' in content, f"Page {page} missing Google Fonts"
    
    @pytest.mark.ui
    def test_responsive_design_classes(self):
        """Test responsive design CSS classes"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for responsive column classes
        responsive_patterns = [
            r'col-\w{2}-\d+',  # col-lg-6, col-md-4, etc.
            r'd-\w{2}-\w+',    # d-md-block, d-lg-none, etc.
        ]
        
        page_html = str(soup)
        responsive_found = False
        for pattern in responsive_patterns:
            if re.search(pattern, page_html):
                responsive_found = True
                break
        
        assert responsive_found, "No responsive design classes found"
    
    @pytest.mark.ui
    def test_icon_font_integration(self):
        """Test icon fonts (Font Awesome) integration"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check for Font Awesome
        assert 'font-awesome' in content.lower() or 'fontawesome' in content.lower(), "Font Awesome not found"
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for icon classes
        icon_elements = soup.find_all(class_=re.compile(r'fa-|fas|far|fab'))
        assert len(icon_elements) > 0, "No Font Awesome icons found"


class TestComponentRendering:
    """Test specific UI component rendering"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_navigation_component_rendering(self):
        """Test navigation component renders correctly"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check navbar structure
        navbar = soup.find('nav', class_=re.compile(r'navbar'))
        assert navbar is not None, "Navbar component not found"
        
        # Check dropdown menus
        dropdowns = soup.find_all(class_=re.compile(r'dropdown'))
        assert len(dropdowns) > 0, "No dropdown menus found"
        
        # Check navigation links
        nav_links = soup.find_all('a', class_=re.compile(r'nav-link'))
        assert len(nav_links) > 0, "No navigation links found"
        
        # Check Arabic navigation text
        nav_text = navbar.get_text()
        arabic_nav_items = ['الاستطلاعات', 'التحليلات', 'التكاملات', 'الإعدادات']
        found_arabic_nav = any(item in nav_text for item in arabic_nav_items)
        assert found_arabic_nav, f"Arabic navigation items not found. Found: {nav_text[:100]}"
    
    @pytest.mark.ui
    def test_breadcrumb_component_rendering(self):
        """Test breadcrumb component renders correctly"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check breadcrumb structure
        breadcrumb = soup.find(class_=re.compile(r'breadcrumb'))
        assert breadcrumb is not None, "Breadcrumb component not found"
        
        # Check breadcrumb items
        breadcrumb_items = soup.find_all('li', class_=re.compile(r'breadcrumb-item'))
        assert len(breadcrumb_items) > 0, "No breadcrumb items found"
        
        # Check home breadcrumb
        breadcrumb_text = breadcrumb.get_text()
        assert 'الرئيسية' in breadcrumb_text, "Home breadcrumb missing"
    
    @pytest.mark.ui
    def test_dashboard_card_components(self):
        """Test dashboard card components render correctly"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for card components
        cards = soup.find_all(class_=re.compile(r'card'))
        assert len(cards) > 0, "No card components found"
        
        # Check card structure
        for card in cards[:3]:  # Check first 3 cards
            card_body = card.find(class_=re.compile(r'card-body'))
            assert card_body is not None, "Card missing card-body"
    
    @pytest.mark.ui
    def test_form_components_rendering(self):
        """Test form components render correctly"""
        response = self.client.get('/surveys/builder')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for form elements
        forms = soup.find_all('form')
        inputs = soup.find_all(['input', 'textarea', 'select'])
        buttons = soup.find_all('button')
        
        # Should have interactive elements
        assert len(forms) > 0 or len(inputs) > 0 or len(buttons) > 0, "No form elements found"
        
        # Check for Bootstrap form classes
        form_classes = ['form-control', 'form-group', 'form-label', 'btn']
        found_form_classes = False
        
        for element in soup.find_all(class_=True):
            element_classes = element.get('class', [])
            if any(fc in ' '.join(element_classes) for fc in form_classes):
                found_form_classes = True
                break
        
        assert found_form_classes, "No Bootstrap form classes found"


class TestChartAndVisualization:
    """Test chart and data visualization rendering"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_chartjs_integration(self):
        """Test Chart.js integration and canvas elements"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check for Chart.js library
        assert 'chart.js' in content.lower() or 'chartjs' in content.lower(), "Chart.js library not found"
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for canvas elements (used by Chart.js)
        canvas_elements = soup.find_all('canvas')
        assert len(canvas_elements) > 0, "No canvas elements found for charts"
        
        # Check canvas has proper attributes
        for canvas in canvas_elements:
            canvas_id = canvas.get('id')
            assert canvas_id is not None, "Canvas missing ID attribute"
    
    @pytest.mark.ui
    def test_dashboard_metrics_display(self):
        """Test dashboard metrics are displayed correctly"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for metric display elements
        metric_elements = soup.find_all(class_=re.compile(r'metric|kpi|stat'))
        
        # Should have some metric display elements or cards with numbers
        number_pattern = re.compile(r'\d+')
        has_metrics = len(metric_elements) > 0
        
        # Alternative: check for cards with numerical content
        if not has_metrics:
            cards = soup.find_all(class_=re.compile(r'card'))
            for card in cards:
                if number_pattern.search(card.get_text()):
                    has_metrics = True
                    break
        
        assert has_metrics, "No metric display elements found"


class TestMobileResponsiveness:
    """Test mobile responsive design"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_mobile_viewport_meta(self):
        """Test mobile viewport meta tag"""
        pages = ['/analytics/executive', '/surveys/builder', '/integrations/sources']
        
        for page in pages:
            response = self.client.get(page)
            soup = BeautifulSoup(response.data, 'html.parser')
            
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            assert viewport_meta is not None, f"Page {page} missing viewport meta"
            
            content = viewport_meta.get('content', '')
            assert 'width=device-width' in content, f"Page {page} viewport not mobile-friendly"
            assert 'initial-scale=1' in content, f"Page {page} missing initial scale"
    
    @pytest.mark.ui
    def test_mobile_navigation_toggle(self):
        """Test mobile navigation toggle button"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for navbar toggler (hamburger menu)
        toggler = soup.find(class_=re.compile(r'navbar-toggler'))
        assert toggler is not None, "Mobile navigation toggle not found"
        
        # Check toggle attributes
        assert toggler.get('data-bs-toggle') or toggler.get('data-toggle'), "Toggle missing data attributes"
    
    @pytest.mark.ui
    def test_responsive_grid_system(self):
        """Test responsive grid system usage"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for responsive column classes
        responsive_cols = soup.find_all(class_=re.compile(r'col-(xs|sm|md|lg|xl)-'))
        assert len(responsive_cols) > 0, "No responsive column classes found"
        
        # Check for containers
        containers = soup.find_all(class_=re.compile(r'container'))
        assert len(containers) > 0, "No container classes found"


class TestAccessibility:
    """Test accessibility features"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_aria_attributes(self):
        """Test ARIA attributes for accessibility"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for ARIA attributes
        aria_elements = soup.find_all(attrs=re.compile(r'^aria-'))
        assert len(aria_elements) > 0, "No ARIA attributes found"
        
        # Check specific ARIA attributes
        aria_labels = soup.find_all(attrs={'aria-label': True})
        aria_expanded = soup.find_all(attrs={'aria-expanded': True})
        
        assert len(aria_labels) > 0 or len(aria_expanded) > 0, "No accessibility ARIA attributes found"
    
    @pytest.mark.ui
    def test_alt_text_for_images(self):
        """Test alt text for images"""
        pages = ['/analytics/executive', '/surveys/builder']
        
        for page in pages:
            response = self.client.get(page)
            soup = BeautifulSoup(response.data, 'html.parser')
            
            images = soup.find_all('img')
            for img in images:
                # Images should have alt attribute (can be empty for decorative images)
                assert img.has_attr('alt'), f"Image in {page} missing alt attribute: {img}"
    
    @pytest.mark.ui
    def test_form_labels(self):
        """Test form labels for accessibility"""
        response = self.client.get('/surveys/builder')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for label elements
        labels = soup.find_all('label')
        inputs = soup.find_all(['input', 'textarea', 'select'])
        
        if len(inputs) > 0:
            # Should have some labels or aria-label attributes
            has_labels = len(labels) > 0
            has_aria_labels = any(inp.has_attr('aria-label') for inp in inputs)
            
            assert has_labels or has_aria_labels, "Form inputs missing labels or aria-labels"


if __name__ == "__main__":
    # Run frontend rendering tests
    import subprocess
    result = subprocess.run(['python', '-m', 'pytest', __file__, '-v', '-m', 'ui'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)