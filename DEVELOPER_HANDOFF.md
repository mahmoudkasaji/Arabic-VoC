# Developer Handoff Guide

## Project Overview
This is an enterprise-grade Voice of Customer platform with comprehensive bilingual (Arabic/English) feedback analysis. The platform features AI-powered sentiment analysis, multi-channel survey distribution, and real-time analytics optimized for Arabic-speaking markets.

## Quick Start for New Developers

### 1. Fork/Clone Setup
- Fork this repository to your GitHub account
- Import to Replit or clone locally
- Dependencies auto-install from `pyproject.toml` (Replit handles this automatically)

### 2. Required Environment Variables (Secrets)
Set these in Replit Secrets or your `.env` file:

**Essential for basic functionality:**
```
SESSION_SECRET=your-session-secret-here
DATABASE_URL=your-postgresql-url (auto-provided in Replit)
```

**Gmail SMTP Integration:**
```
GMAIL_EMAIL=your-gmail-address
GMAIL_APP_PASSWORD=your-gmail-app-password
```

**AI Analytics (OpenAI):**
```
OPENAI_API_KEY=your-openai-api-key
```

**Optional Integrations:**
```
# Twilio SMS
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token  
TWILIO_PHONE_NUMBER=your-twilio-number

# WhatsApp Business API
WHATSAPP_API_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id

# Anthropic Claude (optional)
ANTHROPIC_API_KEY=your-anthropic-key

# JAIS Arabic AI (optional)
JAIS_API_KEY=your-jais-key
JAIS_ENDPOINT=https://api.core42.ai/v1
```

### 3. Running the Application
```bash
# In Replit: Just click "Run" button
# Locally: 
python main.py
# Or with Gunicorn:
gunicorn --bind 0.0.0.0:5000 main:app
```

### 4. Key Files to Understand
- `main.py` - Application entry point
- `app.py` - Flask app configuration and database setup
- `routes/` - Main application routes
- `api/` - API blueprints for integrations
- `templates/` - Jinja2 templates with RTL support
- `static/` - CSS, JS, and assets
- `models/` - Database models
- `utils/` - Utility functions and helpers
- `replit.md` - Project documentation and preferences

### 5. Database Setup
- PostgreSQL is auto-configured in Replit
- Tables are auto-created on first run
- Check `models/` folder for schema definitions

### 6. Testing Integrations
1. Go to `/integrations` page
2. Use "Test API" buttons to verify connections
3. Check logs in Replit console for troubleshooting

### 7. Key Features
- **Surveys**: Create and distribute multilingual surveys
- **Analytics**: AI-powered sentiment analysis with Arabic support  
- **Integrations**: Gmail, Twilio SMS, WhatsApp Business API
- **Feedback Widgets**: Embeddable feedback forms
- **Reporting**: Professional PDF reports with visualizations

## Architecture Notes
- **Backend**: Flask with PostgreSQL
- **Frontend**: Jinja2 templates + vanilla JavaScript
- **AI**: OpenAI GPT-4o for sentiment analysis
- **Authentication**: Replit OAuth 2.0
- **Deployment**: Optimized for Replit platform

## Development Tips
1. Check `replit.md` for user preferences and recent changes
2. All text supports Arabic RTL rendering
3. Follow the existing code patterns for consistency
4. Test with both English and Arabic content
5. Use the integrated testing endpoints for debugging

## Support Channels
- Check existing issues and documentation
- Review console logs for debugging
- Test all integrations before deploying changes

## Next Steps for New Developer
1. Set up required environment variables
2. Run the application and explore all features
3. Review the codebase structure in `replit.md`
4. Test creating a survey and analyzing responses
5. Verify all integrations are working properly

Good luck with the development!