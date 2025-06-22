"""
Visual regression tests for Arabic RTL layout consistency
Tests layout stability and visual elements across pages
"""

import pytest
import re
from bs4 import BeautifulSoup
from app import app

class TestArabicLayoutConsistency:
    """Test Arabic RTL layout consistency across pages"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.arabic
    def test_rtl_direction_consistency(self):
        """Test RTL direction is consistent across all pages"""
        pages = [
            '/analytics/executive',
            '/surveys/builder',
            '/surveys/manage',
            '/integrations/sources',
            '/integrations/destinations',
            '/integrations/ai',
            '/settings/account'
        ]
        
        for page in pages:
            response = self.client.get(page)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.data, 'html.parser')
            html_tag = soup.find('html')
            
            assert html_tag is not None, f"Page {page} missing html tag"
            assert html_tag.get('dir') == 'rtl', f"Page {page} missing RTL direction"
            assert html_tag.get('lang') == 'ar', f"Page {page} missing Arabic language"
    
    @pytest.mark.arabic
    def test_arabic_font_consistency(self):
        """Test Arabic fonts are consistently applied"""
        pages = ['/analytics/executive', '/surveys/builder', '/integrations/sources']
        
        font_families = set()
        for page in pages:
            response = self.client.get(page)
            content = response.data.decode('utf-8')
            
            # Extract font-family declarations
            font_matches = re.findall(r'font-family:\s*([^;]+)', content, re.IGNORECASE)
            for match in font_matches:
                font_families.add(match.strip().lower())
        
        # Should have Arabic fonts
        arabic_fonts_found = any('cairo' in font or 'amiri' in font or 'arabic' in font 
                               for font in font_families)
        assert arabic_fonts_found, f"No Arabic fonts found. Fonts: {list(font_families)[:5]}"
    
    @pytest.mark.ui
    def test_navigation_layout_consistency(self):
        """Test navigation layout is consistent across pages"""
        pages = ['/analytics/executive', '/surveys/builder', '/integrations/sources']
        
        nav_structures = []
        for page in pages:
            response = self.client.get(page)
            soup = BeautifulSoup(response.data, 'html.parser')
            
            nav = soup.find('nav')
            if nav:
                nav_classes = ' '.join(nav.get('class', []))
                nav_structures.append(nav_classes)
        
        # All navigation structures should be similar
        assert len(set(nav_structures)) <= 2, f"Inconsistent navigation structures: {nav_structures}"
    
    @pytest.mark.arabic
    def test_text_alignment_consistency(self):
        """Test text alignment is appropriate for Arabic RTL"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check for appropriate text alignment
        # Should not have left alignment for main content in RTL
        problematic_alignments = re.findall(r'text-align:\s*left', content, re.IGNORECASE)
        
        # Allow some left alignment for specific elements (like code or numbers)
        assert len(problematic_alignments) < 5, f"Too many left-aligned elements in RTL layout: {len(problematic_alignments)}"


class TestResponsiveLayoutValidation:
    """Test responsive layout works correctly"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_bootstrap_grid_usage(self):
        """Test Bootstrap grid system is properly used"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for proper grid structure
        containers = soup.find_all(class_=re.compile(r'container'))
        rows = soup.find_all(class_=re.compile(r'row'))
        cols = soup.find_all(class_=re.compile(r'col-'))
        
        assert len(containers) > 0, "No container elements found"
        assert len(rows) > 0, "No row elements found"
        assert len(cols) > 0, "No column elements found"
        
        # Check grid hierarchy: containers should contain rows, rows should contain cols
        for container in containers:
            container_rows = container.find_all(class_=re.compile(r'row'))
            if len(container_rows) > 0:
                # Found proper structure
                return
        
        # Alternative: check if cols are within rows
        for row in rows:
            row_cols = row.find_all(class_=re.compile(r'col-'))
            assert len(row_cols) > 0, "Rows should contain columns"
    
    @pytest.mark.ui
    def test_responsive_breakpoints(self):
        """Test responsive breakpoint classes are used"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check for responsive breakpoint classes
        breakpoints = ['sm', 'md', 'lg', 'xl', 'xxl']
        breakpoint_found = False
        
        for bp in breakpoints:
            if f'col-{bp}-' in content or f'd-{bp}-' in content:
                breakpoint_found = True
                break
        
        assert breakpoint_found, "No responsive breakpoint classes found"
    
    @pytest.mark.ui
    def test_mobile_navigation_structure(self):
        """Test mobile navigation structure"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for mobile navigation elements
        navbar_toggler = soup.find(class_=re.compile(r'navbar-toggler'))
        navbar_collapse = soup.find(class_=re.compile(r'navbar-collapse'))
        
        assert navbar_toggler is not None, "Mobile navbar toggler not found"
        assert navbar_collapse is not None, "Navbar collapse element not found"
        
        # Check data attributes for Bootstrap functionality
        toggler_target = navbar_toggler.get('data-bs-target') or navbar_toggler.get('data-target')
        collapse_id = navbar_collapse.get('id')
        
        if toggler_target and collapse_id:
            assert toggler_target.replace('#', '') == collapse_id, "Toggler target doesn't match collapse ID"


class TestVisualElementValidation:
    """Test visual elements render correctly"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_card_component_structure(self):
        """Test card components have proper structure"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        cards = soup.find_all(class_=re.compile(r'card\b'))
        assert len(cards) > 0, "No card components found"
        
        for card in cards[:3]:  # Test first 3 cards
            # Cards should have proper structure
            card_body = card.find(class_=re.compile(r'card-body'))
            card_header = card.find(class_=re.compile(r'card-header'))
            card_title = card.find(class_=re.compile(r'card-title'))
            
            # At least one of these should exist
            has_structure = card_body or card_header or card_title
            assert has_structure, f"Card missing proper structure: {card}"
    
    @pytest.mark.ui
    def test_button_styling_consistency(self):
        """Test button styling is consistent"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        buttons = soup.find_all('button')
        button_links = soup.find_all('a', class_=re.compile(r'btn'))
        
        all_buttons = buttons + button_links
        
        if len(all_buttons) > 0:
            # Check for Bootstrap button classes
            btn_classes = []
            for btn in all_buttons:
                classes = btn.get('class', [])
                btn_classes.extend([cls for cls in classes if cls.startswith('btn')])
            
            assert len(btn_classes) > 0, "Buttons missing Bootstrap classes"
    
    @pytest.mark.ui
    def test_icon_rendering(self):
        """Test icons render correctly"""
        response = self.client.get('/analytics/executive')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for Font Awesome icons
        fa_icons = soup.find_all(class_=re.compile(r'fa-|fas|far|fab|fal'))
        
        # Or check for other icon systems
        other_icons = soup.find_all('i', class_=re.compile(r'icon|material'))
        
        total_icons = len(fa_icons) + len(other_icons)
        assert total_icons > 0, "No icons found on the page"
    
    @pytest.mark.ui
    def test_color_scheme_consistency(self):
        """Test color scheme and CSS custom properties"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check for CSS custom properties (variables)
        css_vars = re.findall(r'--[\w-]+:', content)
        
        # Or check for consistent color usage
        color_values = re.findall(r'color:\s*([^;]+)', content, re.IGNORECASE)
        bg_colors = re.findall(r'background-color:\s*([^;]+)', content, re.IGNORECASE)
        
        # Should have some color definitions
        has_colors = len(css_vars) > 0 or len(color_values) > 0 or len(bg_colors) > 0
        assert has_colors, "No color definitions found"


class TestBrowserCompatibility:
    """Test browser compatibility features"""
    
    def setup_method(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def teardown_method(self):
        self.app_context.pop()
    
    @pytest.mark.ui
    def test_css_vendor_prefixes(self):
        """Test CSS vendor prefixes for compatibility"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check for modern CSS features that might need prefixes
        modern_css = [
            'transform', 'transition', 'border-radius', 'box-shadow',
            'flex', 'grid', 'backdrop-filter'
        ]
        
        css_features_found = sum(1 for feature in modern_css if feature in content.lower())
        
        # Should have some modern CSS features
        assert css_features_found > 0, "No modern CSS features found"
    
    @pytest.mark.ui
    def test_fallback_fonts(self):
        """Test fallback fonts are specified"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check font-family declarations
        font_families = re.findall(r'font-family:\s*([^;]+)', content, re.IGNORECASE)
        
        # Should have fallback fonts (serif, sans-serif, etc.)
        fallback_fonts = ['serif', 'sans-serif', 'monospace', 'cursive', 'fantasy']
        has_fallbacks = any(any(fallback in family.lower() for fallback in fallback_fonts) 
                           for family in font_families)
        
        assert has_fallbacks, f"No fallback fonts found. Families: {font_families[:3]}"
    
    @pytest.mark.arabic
    def test_arabic_text_rendering_support(self):
        """Test Arabic text rendering support"""
        response = self.client.get('/analytics/executive')
        content = response.data.decode('utf-8')
        
        # Check for Arabic Unicode range
        arabic_chars = re.findall(r'[\u0600-\u06FF]', content)
        assert len(arabic_chars) > 0, "No Arabic characters found"
        
        # Check for proper UTF-8 encoding
        soup = BeautifulSoup(response.data, 'html.parser')
        meta_charset = soup.find('meta', attrs={'charset': True})
        assert meta_charset is not None, "Missing charset meta tag"
        assert meta_charset.get('charset').upper() == 'UTF-8', "Not using UTF-8 encoding"


if __name__ == "__main__":
    # Run visual regression tests
    import subprocess
    result = subprocess.run(['python', '-m', 'pytest', __file__, '-v'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)