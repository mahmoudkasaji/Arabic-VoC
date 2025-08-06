# GitHub Repository Setup for New Developers

## Repository Structure
This project is optimized for Replit but can also run locally. The main dependencies are managed through `pyproject.toml`.

## Quick Fork & Deploy
1. **Fork this repository** to your GitHub account
2. **Import to Replit**: 
   - Go to Replit
   - Click "Import from GitHub" 
   - Paste your forked repository URL
   - Replit will auto-install dependencies from `pyproject.toml`

## Environment Setup (Critical)
Set these secrets in Replit's Secrets panel:

### Required
- `SESSION_SECRET`: Any random string for session security
- `OPENAI_API_KEY`: Your OpenAI API key for AI analytics

### Email Integration  
- `GMAIL_EMAIL`: Gmail address for sending surveys
- `GMAIL_APP_PASSWORD`: Gmail app password (not regular password)

### Optional Integrations
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- `WHATSAPP_API_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID`
- `ANTHROPIC_API_KEY`, `JAIS_API_KEY`

## Running
- **In Replit**: Just click Run button
- **Locally**: `python main.py` or `gunicorn --bind 0.0.0.0:5000 main:app`

## Key Documentation
- `DEVELOPER_HANDOFF.md` - Complete setup guide
- `replit.md` - Project architecture and preferences
- `docs/` folder - Technical documentation

## Features Ready
✅ Bilingual surveys (Arabic/English)  
✅ AI sentiment analysis with GPT-4o
✅ Multi-channel distribution (Gmail, SMS, WhatsApp)
✅ Real-time analytics dashboard
✅ Professional PDF reporting
✅ Replit OAuth authentication

The platform is production-ready with comprehensive testing and documentation.