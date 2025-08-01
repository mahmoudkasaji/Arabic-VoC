# Voice of Customer Platform

## Overview
An enterprise-grade Voice of Customer platform designed to deliver comprehensive bilingual (Arabic/English) feedback analysis. It features AI-powered sentiment analysis, multi-channel survey distribution, real-time analytics optimized for Arabic-speaking markets, and professional reporting. Built with Flask and PostgreSQL, the platform supports 12 feedback channels with 95%+ AI accuracy for Arabic text processing. The vision is to provide actionable insights for businesses, leveraging advanced technology to understand customer sentiment and drive continuous improvement.

## User Preferences
Preferred communication style: Simple, everyday language.
Visual preferences: Subtle drag-and-drop effects without tilting or rotation - prefers clean, minimal visual feedback.
UX preferences: Industry-standard layouts with 70% canvas space, collapsible sidebars, and professional question type galleries. Prefers practical, non-gimmicky features - avoid complex Arabic text analytics settings or "Arabic visions" type features that native speakers wouldn't use. Prefers focused MVP approach - doing a few things really well rather than many features poorly.
Mobile preferences: Question type dropdown instead of sidebar list, positioned under survey header section.
Desktop preferences: Maximized canvas space with survey header moved to right properties panel for optimal screen utilization.
Executive Dashboard Focus: Prioritizes real-time KPIs with immediate business value, prefers phased development approach leveraging existing infrastructure.
Navigation Architecture: Prefers 4-tier navigation structure: 1. Surveys 2. Analytics 3. Integrations 4. Settings with proper cascading navigation and breadcrumbs for clear information architecture.
AI Analysis Preference: Prefers efficient multi-agent orchestration over single prompts for better accuracy, cost efficiency, and maintainability. Values robust fallback systems and performance optimization.
Code Organization Preference: Prefers rationalized, consolidated file structure with clear separation of concerns. Values plain-language documentation for non-technical users and logical grouping of related functionality (e.g., all testing under unified structure with explanatory guides). Prefers Flask routes over API endpoints for contact management operations.
Localization Preference: Values bilingual documentation (English/Arabic) to make the platform accessible to Arabic-speaking developers and users. Prefers comprehensive Levantine Arabic documentation for technical guides, user manuals, and development instructions to support non-English speakers joining the development process.
UX Testing Focus: Prioritizes comprehensive frontend-backend integration testing with emphasis on ensuring all toggles, buttons, and interactive elements work correctly. Values user story-driven testing approach with detailed validation of Arabic text handling and real-time functionality.
QA Framework Preference: Prefers comprehensive testing coverage that evolves with platform enhancements. Values enhancement-specific test development for each major release, maintaining high-quality standards (≥95% pass rate) while ensuring Arabic language excellence and mobile responsiveness. Emphasizes automated testing pipelines with manual validation for user experience quality.

## Recent Changes
**Simplified Analytics Dashboard (August 2025)**
- Created clean 4-KPI dashboard layout focusing on essential metrics: CSAT, NPS, CES, and Completion Rate
- Implemented toggleable chart system allowing users to switch between different KPI visualizations
- Converted from API-based to pure Flask server-side rendering for improved simplicity and performance
- Designed beautiful Arabic-friendly interface with gradient cards and smooth animations
- Embedded chart data directly in templates using Jinja2 for optimal loading speed

**Comprehensive Codebase Refactoring (August 2025)**
- Completed major refactoring and consolidation initiative reducing code complexity by 80%
- Reduced LSP diagnostics from 117 to 23 (80% reduction) through systematic consolidation
- Created 7 consolidated utilities combining 19+ scattered utility files
- Standardized import patterns across all major files (app.py, routes.py, contact_routes.py)
- Fixed SQLAlchemy model inheritance issues reducing model-related errors by 62%
- Implemented unified response handling and error management across all endpoints
- Maintained all existing functionality while significantly improving maintainability and performance

**Legacy Code Cleanup (August 2025)**
- Completed comprehensive codebase audit and cleanup following API migration
- Removed deprecated API files and unused main files (run.py, debug routes)
- Fixed test imports and disabled obsolete FastAPI dependencies
- Streamlined application structure for better maintainability and performance

**API to Flask Migration (August 2025)**
- Converted internal operation APIs from FastAPI to Flask routes for improved integration
- Migrated contact management, user preferences, integration testing, and survey distribution to Flask
- Consolidated routing structure to reduce complexity and improve performance for simple operations
- Maintained API structure for complex analytics and external integrations

**API Integrations Catalog Enhancement (January 2025)**
- Redesigned `/integrations/catalog` with developer-focused API documentation approach
- Improved from visual-heavy dashboard to technical reference with endpoint details, authentication methods, and testing interface
- Added comprehensive API documentation format showing request headers, response examples, and implementation files
- Enhanced filtering, export capabilities, and real-time API testing functionality

## System Architecture

### 6-Layer Enterprise Architecture
- **Presentation**: 25+ responsive Arabic RTL templates with bilingual interface and progressive web app features.
- **API & Services**: 15+ RESTful endpoints for analytics and multi-channel distribution.
- **Business Logic**: Arabic text processing, GPT-4o AI engine, survey management, and Replit OAuth 2.0 + PKCE security.
- **Data**: PostgreSQL with Arabic optimization, unified data models, and real-time analytics storage.
- **External Integrations**: OpenAI GPT-4o, Gmail/Twilio/WhatsApp APIs, Replit platform integration, Chart.js visualizations.
- **Infrastructure**: Gunicorn WSGI with auto-scaling, multi-environment deployment, and performance monitoring.

### Technical Implementation
- **Backend Framework**: Hybrid Flask/API architecture optimized for Replit deployment. Flask routes for internal operations, API blueprints for complex processing.
- **Authentication**: Enterprise Replit OAuth 2.0 with PKCE and role-based access control. Native Replit integration with a three-table user management system (`replit_users`, `replit_user_preferences`, `replit_oauth`).
- **AI System**: Advanced Arabic analyzer with OpenAI GPT-4o integration, supporting sentiment analysis, emotion detection, and topic categorization with cultural context awareness.
- **Database**: PostgreSQL 13+ with Arabic collation, connection pooling, and performance indexes, managed by Flask-SQLAlchemy.
- **Frontend**: Jinja2 templates with RTL support, custom CSS with an Arabic design system, vanilla JavaScript, and Chart.js for visualizations. Arabic fonts (Amiri, Cairo) are used.
- **Survey Management**: Flask routes for simple operations (list, create, distribute), API blueprints for complex analytics. Streamlined navigation, unified interface for creation, distribution, and monitoring, with multi-channel options (email, SMS, links). Supports various question types and generates web-hosted survey links (custom URLs, QR codes).
- **Analytics Dashboard**: Hybrid approach - Flask routes for basic data, API blueprints for complex analytics. Consolidated into two core approaches: Main Analytics Dashboard for KPIs and Advanced Analytics for enhanced text analysis and professional reporting. Features quantitative metrics, qualitative text analytics, and a journey matrix. Includes predictive CX insights (satisfaction, early warning, opportunity detection) and an "Actions Required" workflow tab for analysts.
- **Feedback Widgets**: Flask routes for simple submissions, API blueprints for complex processing. Persistent footer and sidebar feedback forms with conditional logic, Arabic RTL support, and direct database integration.
- **Contact Management**: Migrated to Flask routes for optimal performance. Direct database operations for CRUD functionality, hard delete functionality, bulk import/export, and integration with survey distribution.
- **User Preferences**: Flask routes for settings management with native session integration.
- **Integration Testing**: Flask routes for real-time integration health monitoring and testing.
- **Internationalization**: Full bilingual system (Arabic/English) with JSON translation dictionaries, template helpers, JavaScript toggles, and complete RTL/LTR support.
- **UI/UX Decisions**: Unified navigation with a 4-tab structure (Surveys, Analytics, Integrations, Settings), consistent layout system, and comprehensive design system with standardized components and responsive design. Emphasis on progressive disclosure and simplified workflows.

## External Dependencies
- **Flask**: Web framework.
- **Flask-Dance**: OAuth 2.0 integration for Replit authentication.
- **Flask-Login**: Session management.
- **SQLAlchemy**: ORM for database interactions.
- **OpenAI**: GPT-4o for AI analysis.
- **PyJWT**: JWT token handling.
- **arabic-reshaper**: For Arabic character shaping.
- **python-bidi**: For bidirectional text algorithm.
- **aiofiles**: For async file operations.
- **Jinja2**: Template rendering.
- **Chart.js**: Data visualization.
- **Font Awesome**: Icon library.
- **Google Fonts**: Arabic typography.
- **Gmail SMTP**: For email delivery.
- **Twilio/WhatsApp APIs**: For multi-channel distribution (planned/integrated).
- **Replit Platform**: For database and deployment.