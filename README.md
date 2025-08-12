Voice of Customer Platform
What This App Does
A bilingual (Arabic/English) customer feedback platform that:

Creates and distributes surveys via multiple channels (web, email, SMS)
Analyzes feedback using AI for sentiment analysis and insights
Provides real-time analytics dashboards
Supports Arabic text processing with RTL interface
Target Users: Businesses in Arabic-speaking markets collecting customer feedback

Quick Start for New Developers
1. Environment Setup
# This app runs on Replit - just click "Run"
# Dependencies install automatically via pyproject.toml
2. Required API Keys (Add to Replit Secrets)
OPENAI_API_KEY=your-openai-key     # Required for AI analysis
SESSION_SECRET=your-session-key    # Required for security
TWILIO_ACCOUNT_SID=optional        # For SMS surveys
TWILIO_AUTH_TOKEN=optional         # For SMS surveys
3. Access the App
Main app: http://0.0.0.0:5000
Login: Click the globe icon to switch languages
Test survey creation: /surveys/create
How to Make Changes
Adding New Features
Frontend: Edit templates in /templates/ directory
Backend Logic: Add routes in app.py for simple features, /api/ for complex ones
Translations: Update both /translations/ar.json and /translations/en.json
Database: Modify models in models_unified.py
Testing Your Changes
# Run the app and test manually
# Check browser console for JavaScript errors
# Test both Arabic and English interfaces
Key Files to Know
├── app.py                     # Main application with all routes
├── main.py                    # Entry point (don't modify)
├── models_unified.py          # Database schema
├── utils/
│   ├── language_manager.py    # Handles Arabic/English switching
│   └── simple_arabic_analyzer.py  # AI analysis engine
├── templates/                 # HTML templates
│   ├── index_simple.html      # Homepage
│   └── components/            # Reusable UI pieces
├── static/
│   ├── js/main.js            # Language switching logic
│   └── css/                   # Styling
└── translations/
    ├── ar.json               # Arabic text
    └── en.json               # English text
Common Development Tasks
Adding a New Page
Create template in /templates/your_page.html
Add route in app.py:
@app.route('/your-page')
def your_page():
    return render_template('your_page.html')
Add navigation link in /templates/components/unified_navigation.html
Add translations to both language files
Adding New Translation Text
Edit /translations/ar.json and /translations/en.json
Use in templates: {{ 'your.translation.key' | translate }}
Test language switching works
Modifying the Database
Edit models in models_unified.py
The database auto-creates tables on restart
For complex changes, consider data migration
Architecture Overview
Frontend: Jinja2 templates with Bootstrap CSS, bilingual support Backend: Flask with hybrid approach - simple routes for basic features, API blueprints for complex analytics Database: PostgreSQL with Arabic text optimization AI: OpenAI GPT-4o integration for Arabic sentiment analysis Auth: Replit OAuth (automatic in Replit environment)

How the Bilingual System Works
User language stored in Flask session
/utils/language_manager.py handles language detection and switching
Templates use {{ 'key' | translate }} for all text
JavaScript syncs with server language state
Click globe icon in navigation to switch languages
Common Issues & Solutions
Language Not Switching
Check browser console for JavaScript errors
Verify translations exist in both /translations/ar.json and /translations/en.json
Clear browser cache and reload
Database Errors
Database auto-recreates on restart
Check models_unified.py for model definitions
Environment variable DATABASE_URL is auto-provided by Replit
AI Analysis Not Working
Verify OPENAI_API_KEY is set in Replit Secrets
Check /utils/simple_arabic_analyzer.py for error logs
Test with simple Arabic text first
Styling Issues
Main CSS in /static/css/unified-layout.css
Bootstrap RTL CSS auto-loads for Arabic
Use browser dev tools to debug CSS conflicts
Deployment
Development: Just click "Run" in Replit Production: Use Replit deployments (click Deploy button)

The app is optimized for Replit's environment and handles Arabic text processing automatically.

Getting Help
Check this README first
Look at similar existing code in the app
Test changes in small increments
Use browser dev tools for frontend debugging
What Makes This App Special
Native Arabic Support: Full RTL interface with proper text processing
Bilingual: Seamless Arabic-English switching throughout
AI-Powered: Understands Arabic dialects and cultural context
Multi-Channel: Surveys via web, email, SMS, QR codes
Real-Time: Live analytics and dashboard updates
For Stakeholders
This platform helps businesses in Arabic markets understand their customers better through:

Professional survey creation and distribution
AI-powered analysis of Arabic feedback
Real-time dashboards showing customer satisfaction trends
Multi-channel delivery ensuring broad reach
The technology is modern, scalable, and specifically designed for Arabic-speaking markets.
