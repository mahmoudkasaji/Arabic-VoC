# Arabic VoC Platform - Design System Documentation

**Version**: 1.0  
**Last Updated**: June 23, 2025  
**Status**: Production Ready

## Overview

The Arabic Voice of Customer platform implements a comprehensive design system that ensures visual consistency, accessibility, and cultural appropriateness across all user interfaces. The system is built with Arabic-first design principles and RTL (Right-to-Left) layout support.

## Core Philosophy

### Arabic-First Design
- Native Arabic typography with Cairo and Amiri fonts
- Right-to-left layout optimization
- Cultural color preferences and visual patterns
- Proper Arabic text rendering and spacing

### Component-Driven Architecture
- Reusable UI components with consistent behavior
- CSS custom properties for maintainable theming
- Responsive design patterns for all screen sizes
- Accessibility compliance for Arabic content

## Design Tokens

### Color Palette

#### Primary Colors
```css
--primary-50: #f0f9f4
--primary-100: #dcf2e4
--primary-200: #bce5cc
--primary-300: #8dd3aa
--primary-400: #5bb882
--primary-500: #2E8B57  /* Main brand color - Sea Green */
--primary-600: #25754a
--primary-700: #1f5e3d
--primary-800: #1a4d33
--primary-900: #16402b
```

#### Secondary Colors
```css
--secondary-500: #F4A460  /* Sandy Brown */
--accent-blue: #4169E1
--success: #28a745
--warning: #ffc107
--danger: #dc3545
--info: #17a2b8
```

#### Neutral Palette
```css
--neutral-50: #f8f9fa
--neutral-100: #f1f3f4
--neutral-200: #e9ecef
--neutral-800: #343a40
--neutral-900: #212529
```

### Typography Scale

#### Font Families
```css
--font-family-primary: 'Cairo', sans-serif
--font-family-heading: 'Amiri', serif
--font-family-mono: 'Courier New', monospace
```

#### Font Sizes
```css
--font-size-xs: 0.75rem    /* 12px */
--font-size-sm: 0.875rem   /* 14px */
--font-size-base: 1rem     /* 16px */
--font-size-lg: 1.125rem   /* 18px */
--font-size-xl: 1.25rem    /* 20px */
--font-size-2xl: 1.5rem    /* 24px */
--font-size-3xl: 1.875rem  /* 30px */
--font-size-4xl: 2.25rem   /* 36px */
--font-size-5xl: 3rem      /* 48px */
```

### Spacing System
```css
--space-1: 0.25rem   /* 4px */
--space-2: 0.5rem    /* 8px */
--space-3: 0.75rem   /* 12px */
--space-4: 1rem      /* 16px */
--space-5: 1.25rem   /* 20px */
--space-6: 1.5rem    /* 24px */
--space-8: 2rem      /* 32px */
--space-10: 2.5rem   /* 40px */
--space-12: 3rem     /* 48px */
--space-16: 4rem     /* 64px */
--space-20: 5rem     /* 80px */
--space-24: 6rem     /* 96px */
```

### Border Radius
```css
--radius-none: 0
--radius-sm: 0.125rem   /* 2px */
--radius-base: 0.25rem  /* 4px */
--radius-md: 0.375rem   /* 6px */
--radius-lg: 0.5rem     /* 8px */
--radius-xl: 0.75rem    /* 12px */
--radius-2xl: 1rem      /* 16px */
--radius-full: 9999px
```

### Shadow System
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)
```

## Component Library

### Layout Components

#### Container
```css
.container-custom {
    max-width: 1400px;
    margin: 0 auto;
    padding-left: var(--space-4);
    padding-right: var(--space-4);
}
```

#### Page Header
```css
.page-header {
    background: var(--bg-primary);
    padding: var(--space-8);
    margin-bottom: var(--space-8);
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-base);
    border: 1px solid var(--border-light);
}
```

### Card Components

#### Standard Card
```css
.card-custom {
    background: var(--bg-primary);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
    margin-bottom: var(--space-6);
    box-shadow: var(--shadow-base);
    border: 1px solid var(--border-light);
    transition: all var(--transition-base);
}
```

#### Interactive Card
```css
.card-custom.card-interactive {
    cursor: pointer;
}

.card-custom.card-interactive:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
}
```

### Button Components

#### Primary Button
```css
.btn-primary-custom {
    background-color: var(--primary-500);
    color: var(--text-white);
    border-color: var(--primary-500);
    padding: var(--space-3) var(--space-6);
    font-weight: var(--font-weight-medium);
    border-radius: var(--radius-lg);
    transition: all var(--transition-base);
}

.btn-primary-custom:hover {
    background-color: var(--primary-600);
    border-color: var(--primary-600);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}
```

#### Outline Button
```css
.btn-outline-custom {
    background-color: transparent;
    color: var(--primary-500);
    border-color: var(--primary-500);
}

.btn-outline-custom:hover {
    background-color: var(--primary-500);
    color: var(--text-white);
}
```

#### Button Sizes
```css
.btn-sm-custom {
    padding: var(--space-2) var(--space-4);
    font-size: var(--font-size-sm);
    border-radius: var(--radius-md);
}

.btn-lg-custom {
    padding: var(--space-4) var(--space-8);
    font-size: var(--font-size-lg);
    border-radius: var(--radius-xl);
}
```

### Form Components

#### Form Control
```css
.form-control-custom {
    display: block;
    width: 100%;
    padding: var(--space-3) var(--space-4);
    font-size: var(--font-size-base);
    color: var(--text-primary);
    background-color: var(--bg-primary);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-lg);
    transition: all var(--transition-base);
}

.form-control-custom:focus {
    outline: none;
    border-color: var(--primary-500);
    box-shadow: 0 0 0 3px rgba(46, 139, 87, 0.1);
}
```

#### Form Label
```css
.form-label-custom {
    display: block;
    margin-bottom: var(--space-2);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
}
```

#### Form Group
```css
.form-group-custom {
    margin-bottom: var(--space-5);
}
```

### Navigation Components

#### Navbar
```css
.navbar-custom {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border-light);
    padding: var(--space-4) 0;
    position: sticky;
    top: 0;
    z-index: var(--z-sticky);
}
```

#### Navigation Links
```css
.nav-link-custom {
    padding: var(--space-2) var(--space-4);
    color: var(--text-primary);
    text-decoration: none;
    border-radius: var(--radius-md);
    transition: all var(--transition-base);
}

.nav-link-custom:hover,
.nav-link-custom.active {
    background-color: var(--primary-50);
    color: var(--primary-600);
}
```

## Typography System

### Arabic Title Class
```css
.arabic-title {
    font-family: var(--font-family-heading);
    font-weight: var(--font-weight-bold);
}
```

### Heading Hierarchy
```css
h1, .h1 {
    font-size: var(--font-size-4xl);
    font-weight: var(--font-weight-bold);
    line-height: var(--line-height-tight);
    margin-bottom: var(--space-6);
}

h2, .h2 {
    font-size: var(--font-size-3xl);
    font-weight: var(--font-weight-semibold);
    line-height: var(--line-height-tight);
    margin-bottom: var(--space-5);
}
```

## Responsive Design

### Breakpoints
- Mobile: max-width 576px
- Tablet: max-width 768px
- Desktop: max-width 1200px
- Large Desktop: max-width 1400px

### Mobile Adaptations
```css
@media (max-width: 768px) {
    .container-custom {
        padding-left: var(--space-3);
        padding-right: var(--space-3);
    }
    
    .page-header {
        padding: var(--space-6);
        margin-bottom: var(--space-6);
    }
}
```

## Utility Classes

### Color Utilities
```css
.text-primary-custom { color: var(--primary-500) !important; }
.text-secondary-custom { color: var(--secondary-500) !important; }
.text-success-custom { color: var(--success) !important; }
.text-warning-custom { color: var(--warning) !important; }
.text-danger-custom { color: var(--danger) !important; }
```

### Background Utilities
```css
.bg-primary-custom { background-color: var(--primary-500); }
.bg-secondary-custom { background-color: var(--secondary-500); }
.bg-light-custom { background-color: var(--bg-secondary); }
```

### Border Utilities
```css
.border-primary-custom { border-color: var(--primary-500); }
.border-light-custom { border-color: var(--border-light); }
```

### Border Radius Utilities
```css
.rounded-custom { border-radius: var(--radius-base); }
.rounded-lg-custom { border-radius: var(--radius-lg); }
.rounded-xl-custom { border-radius: var(--radius-xl); }
```

### Shadow Utilities
```css
.shadow-sm-custom { box-shadow: var(--shadow-sm); }
.shadow-custom { box-shadow: var(--shadow-base); }
.shadow-lg-custom { box-shadow: var(--shadow-lg); }
```

## Implementation Guidelines

### Template Structure
All templates should include:
```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    {% include 'components/head.html' %}
    <title>Page Title - منصة صوت العميل العربية</title>
</head>
<body>
    {% include 'components/navigation.html' %}
    
    <div class="container-custom">
        <div class="page-header">
            <h1 class="arabic-title">Page Title</h1>
            <p class="text-muted">Page description</p>
        </div>
        
        <!-- Page content -->
    </div>
    
    {% include 'components/scripts.html' %}
</body>
</html>
```

### Shared Components

#### Head Component (`components/head.html`)
- Bootstrap RTL CSS
- Font Awesome icons
- Arabic fonts (Cairo, Amiri)
- Design system CSS
- Meta tags for Arabic content

#### Scripts Component (`components/scripts.html`)
- Bootstrap JavaScript
- Chart.js (when needed)
- Page-specific scripts

#### Navigation Component (`components/navigation.html`)
- Unified navbar styling
- Arabic navigation labels
- Consistent dropdown menus

## Quality Assurance

### Validation Checklist
- [ ] Uses shared head and scripts components
- [ ] Implements container-custom for proper layout
- [ ] Uses card-custom for content sections
- [ ] Applies btn-primary-custom for primary actions
- [ ] Uses form-control-custom for form inputs
- [ ] Includes arabic-title for headings
- [ ] Maintains RTL direction and Arabic language
- [ ] Follows color system with CSS custom properties

### Testing Requirements
- Cross-browser compatibility (Chrome, Firefox, Safari)
- Mobile responsiveness validation
- Arabic text rendering verification
- Color contrast accessibility compliance
- Performance impact assessment

## Maintenance

### Adding New Components
1. Define component in `static/css/design-system.css`
2. Use CSS custom properties for consistency
3. Include hover and focus states
4. Add responsive behavior
5. Document usage in this file
6. Update test suite

### Updating Colors
1. Modify color variables in design tokens section
2. Test across all components
3. Validate accessibility contrast ratios
4. Update documentation

### Version Control
- All design system changes require documentation updates
- Test coverage for new components
- Cross-page consistency validation
- User feedback integration

## Support

For design system questions or issues:
- Check component documentation above
- Review implementation in existing templates
- Run design system test suite
- Validate with Arabic content experts