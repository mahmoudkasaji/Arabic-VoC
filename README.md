# Arabic Voice of Customer Platform

A comprehensive platform for collecting and analyzing Arabic customer feedback with real-time analytics and bilingual support.

## Architecture Overview

### Core Components
- **Flask Application** (`main.py`): Main application entry point
- **Authentication** (`replit_auth.py`): Replit Auth integration
- **Routes** (`routes.py`): Application routing and API endpoints
- **Models** (`models.py`): Database models for users, feedback, and OAuth tokens
- **Static Assets** (`static/`): CSS, JavaScript, and language management
- **Templates** (`templates/`): HTML templates with RTL support

### Key Features
- ✅ Replit Auth integration for seamless authentication
- ✅ Bilingual support (Arabic/English) with RTL layout
- ✅ Real-time feedback collection and analysis
- ✅ Responsive Bootstrap UI with Arabic typography
- ✅ Protected dashboard and analytics pages

## Quick Start

1. **Environment Setup**
   - Ensure `REPL_ID` environment variable is set (automatically set in Replit)
   - Optional: Set `DATABASE_URL` for external database

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Access the Platform**
   - Main page: Your Replit URL
   - Feedback (public): `/feedback`
   - Dashboard (protected): `/dashboard/realtime`
   - Analytics (protected): `/analytics`

## File Structure

```
├── main.py              # Application entry point
├── routes.py            # URL routing and API endpoints
├── replit_auth.py       # Authentication logic
├── models.py            # Database models
├── static/
│   ├── css/main.css     # Styling with RTL support
│   └── js/
│       └── lang-manager.js  # Language switching logic
├── templates/           # HTML templates
├── utils/               # Utility modules for Arabic processing
├── api/                 # API endpoint modules
└── docs/                # Documentation
```

## API Endpoints

- `GET /` - Main dashboard (auth required) or landing page
- `GET /feedback` - Public feedback form
- `POST /api/feedback` - Submit feedback (public)
- `GET /api/user` - Get current user info (auth required)
- `GET /health` - Health check endpoint

## Development

The platform uses Flask with SQLAlchemy for the backend and Bootstrap with custom CSS for the frontend. Language switching is handled client-side with JavaScript.

### Arabic Support
- RTL layout and typography
- Arabic text processing utilities
- Bilingual interface with seamless switching
- Cultural context preservation in feedback analysis

## Deployment

Deployed on Replit with automatic scaling. The application uses:
- Flask development server for local development
- SQLite database (upgradeable to PostgreSQL)
- Replit Auth for user management
- Static file serving through Flask