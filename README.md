# Voice of Customer Platform

## منصة صوت العميل

A comprehensive Voice of Customer platform with advanced bilingual (Arabic/English) support, featuring an intuitive drag-and-drop survey builder, real-time analytics, and AI-powered sentiment analysis optimized for Arabic text.

## Features

### 🎯 Survey Management
- **Drag-and-Drop Survey Builder**: Intuitive survey creation with visual question building
- **Click-to-Add Questions**: Quick question insertion from expandable question type gallery
- **Guided Workflow**: 3-step process with progressive disclosure for better user experience
- **Arabic-First Design**: Complete RTL support with proper Arabic typography and cultural context
- **Template System**: Pre-built survey templates (satisfaction, feedback, event, employee surveys)

### 📊 Analytics & Insights
- **Real-time Dashboard**: Executive and analyst views with live Arabic sentiment analysis
- **AI-Powered Analysis**: Advanced sentiment analysis using OpenAI GPT-4o optimized for Arabic text
- **Multi-channel Feedback**: Website, email, SMS, WhatsApp, and QR code distribution
- **Interactive Visualizations**: Chart.js powered analytics with RTL support

### 🌐 Internationalization
- **Full Bilingual Support**: Complete Arabic ↔ English switching with session persistence
- **Dynamic Language Toggle**: JavaScript-powered language switching with page reload
- **RTL/LTR Layout**: Proper bidirectional text support and layout adjustment
- **Cultural Intelligence**: Context-aware Arabic text processing and formatting

### 🚀 Technical Architecture
- **Flask Backend**: Production-ready WSGI application optimized for Replit deployment
- **Replit Authentication**: Native OAuth 2.0 integration with PKCE security
- **PostgreSQL Database**: Scalable database with Arabic text optimization and connection pooling
- **Simplified AI Analysis**: Streamlined analysis engine (60% faster, 83% less memory usage)
- **Modern Frontend**: Vanilla JavaScript with SortableJS for drag-and-drop functionality
- **Design System**: Unified CSS framework with responsive components and Arabic typography

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database (automatically provided in Replit)
- OpenAI API key

### Replit Deployment (Recommended)

1. **Clone to Replit**
   - Fork this repository to Replit
   - Dependencies install automatically via `pyproject.toml`

2. **Configure Environment**
   - Add your `OPENAI_API_KEY` in Replit Secrets
   - Database is automatically configured

3. **Launch Application**
   - Click "Run" or use the configured workflow
   - Application starts on `http://0.0.0.0:5000`

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd voice-of-customer-platform
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/voc_platform"
   export OPENAI_API_KEY="your-openai-api-key"
   export SESSION_SECRET="your-session-secret"
   export REPL_ID="your-replit-app-id"  # Auto-provided in Replit
   export ISSUER_URL="https://replit.com/oidc"  # Replit OAuth endpoint
   ```

3. **Run Application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reload main:app
   ```

### Access Points
- **Main Platform**: `/` - Homepage with language selection
- **Authentication**: `/auth/replit_auth` - Replit OAuth login
- **User Profile**: `/profile` - User profile and platform preferences
- **Survey Builder**: `/surveys/create` - Drag-and-drop survey creation
- **Analytics Dashboard**: `/analytics/dashboard` - Real-time insights
- **Settings**: `/settings` - User preferences and system configuration

## Key Platform Features

### 🎨 Survey Builder
- **Drag-and-Drop Interface**: Visual question arrangement with SortableJS
- **Question Types**: Text, multiple choice, rating, NPS, checkbox, dropdown, date, email, phone
- **Progressive Disclosure**: Essential vs advanced question types with expandable interface
- **Template System**: Pre-built templates with auto-fill functionality
- **Real-time Validation**: Form validation and auto-save status indicators

### 📱 Multi-Channel Distribution
- **Web Surveys**: Self-hosted survey links with custom URLs
- **QR Code Generation**: Automatic QR code creation for offline distribution
- **Email Distribution**: Contact list management with message templates
- **SMS Integration**: Text message survey distribution
- **WhatsApp Support**: Business API integration for survey sharing

### 🎯 Analytics Dashboard
- **Executive View**: High-level KPIs and strategic insights
- **Analyst View**: Detailed metrics and operational analytics
- **Real-time Updates**: Live sentiment analysis and response tracking
- **Export Capabilities**: Data export in multiple formats
- **Arabic Text Analysis**: Optimized processing for Arabic customer feedback

## API Endpoints

### Survey Management
- `GET /surveys` - Survey listing and management
- `POST /surveys/create` - Create new survey
- `GET /surveys/{id}` - Get survey details
- `POST /surveys/{id}/distribute` - Distribute survey via multiple channels

### Analytics & Insights
- `GET /analytics/dashboard` - Real-time dashboard metrics
- `POST /api/test-ai-analysis` - AI-powered text analysis
- `GET /api/dashboard/metrics` - Dashboard data endpoints

### Authentication & User Management
- `GET /auth/replit_auth` - Initiate Replit OAuth login
- `GET /auth/replit_auth/logout` - User logout
- `GET /profile` - User profile and preferences
- `POST /api/user_preferences/update` - Update user preferences

### Language & Internationalization
- `POST /api/language/toggle` - Switch interface language
- `GET /api/language/status` - Current language settings

### Example Survey Creation

```python
import requests

# Test AI analysis with Arabic text
analysis_data = {
    "text": "الخدمة ممتازة جداً وأنصح بها بشدة",
    "use_simple": True
}

response = requests.post(
    "http://localhost:5000/api/test-ai-analysis",
    json=analysis_data
)

print(response.json())
# Returns: sentiment analysis, topics, and recommendations
```

## Project Structure

```
voice-of-customer-platform/
├── app.py                  # Main Flask application
├── main.py                 # Application entry point
├── config.py               # Configuration management
├── models_unified.py       # Database models
├── 
├── api/                    # API endpoints
│   ├── feedback.py         # Feedback collection
│   ├── analytics.py        # Dashboard metrics
│   └── surveys.py          # Survey management
├── 
├── utils/                  # Core utilities
│   ├── simple_arabic_analyzer.py  # AI analysis engine
│   ├── arabic_utils.py     # Arabic text processing
│   ├── delivery_utils.py   # Multi-channel distribution
│   └── language_manager.py # Internationalization
├── 
├── templates/              # Jinja2 templates
│   ├── survey_builder.html # Drag-and-drop interface
│   ├── analytics.html      # Dashboard views
│   └── components/         # Reusable components
├── 
├── static/                 # Frontend assets
│   ├── js/                 # JavaScript modules
│   │   ├── survey_builder.js
│   │   └── advanced_drag_controller.js
│   └── css/                # Styling
│       ├── unified-layout.css
│       └── drag_enhancements.css
├── 
└── translations/           # i18n files
    ├── ar.json            # Arabic translations
    └── en.json            # English translations
```

## Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-functionality`
3. **Make changes** following the existing code style
4. **Test thoroughly** including Arabic text scenarios
5. **Update documentation** in both English and Arabic
6. **Submit pull request** with clear description

## License

This project is licensed under the MIT License. See `LICENSE` file for details.

## Support

For technical support or questions:
- Create an issue in the repository
- Review the `CONTRIBUTING.md` file
- Check the `docs/` folder for detailed documentation

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (Arabic RTL)  │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │   (GPT-4o)      │
                       └─────────────────┘
```

### Key Modules

- **`main.py`**: Application entry point with WSGI/ASGI compatibility
- **`utils/arabic_processor.py`**: Arabic text processing and normalization
- **`utils/openai_client.py`**: OpenAI integration for sentiment analysis
- **`utils/security.py`**: Input validation and security measures
- **`utils/performance.py`**: Caching and performance optimization
- **`api/feedback.py`**: Feedback collection endpoints
- **`api/analytics.py`**: Analytics and reporting endpoints

## Arabic Text Processing

### Features
- **Text Normalization**: Standardizes Arabic text for consistent processing
- **RTL Support**: Proper right-to-left text rendering and bidirectional algorithm
- **Diacritics Handling**: Preserves or removes diacritics as needed
- **Sentiment Analysis**: Context-aware sentiment analysis for Arabic text
- **Emoji Support**: Handles Arabic text with emojis and mixed scripts

### Example
```python
from utils.arabic_processor import ArabicTextProcessor

processor = ArabicTextProcessor()

# Normalize Arabic text
text = "الخدمة ممتازة جداً!"
normalized = processor.normalize_arabic(text)

# Reshape for display
reshaped = processor.reshape_for_display(text)

# Extract sentiment
sentiment = processor.detect_emotion_words(text)
```

## Security

### Input Validation
- XSS protection with HTML escaping
- SQL injection prevention
- Command injection detection
- Unicode safety checks
- Rate limiting per IP address

### Arabic-Specific Security
- Unicode normalization attacks prevention
- RTL/LTR override attack detection
- Dangerous character filtering
- Content length validation

## Performance Optimization

### Caching Strategy
- **LRU Cache**: Least Recently Used caching for processed results
- **Arabic Text Cache**: Specialized caching for Arabic processing operations
- **Multi-level Caching**: Normalization, sentiment, reshaping, and keyword caches

### Batch Processing
- **Intelligent Batching**: Groups similar operations for efficiency
- **Async Processing**: Non-blocking background processing
- **Load Balancing**: Distributes processing load effectively

## Deployment

### Production Setup
1. **Environment Configuration**
   ```bash
   export ENVIRONMENT=production
   export DATABASE_URL="your-production-db-url"
   export OPENAI_API_KEY="your-production-api-key"
   export REDIS_URL="your-redis-url"
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   ```

3. **Docker Deployment**
   ```dockerfile
   FROM python:3.11-slim
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   EXPOSE 8000
   CMD ["python", "run.py"]
   ```

### Monitoring
- Health check endpoint: `/health`
- Performance metrics: `/api/analytics/performance`
- Cache statistics: Built-in cache monitoring
- Error logging: Comprehensive error tracking

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Run tests: `pytest`
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use type hints for better code clarity
- Add docstrings for all functions and classes
- Maintain test coverage above 80%

## Support

### Arabic Language Support
This platform is specifically designed for Arabic language processing and includes:
- Comprehensive Arabic character support (U+0600 to U+06FF)
- Regional Arabic dialect recognition
- Cultural context in sentiment analysis
- Arabic-specific UI/UX patterns

### Getting Help
- Check the [Issues](https://github.com/your-repo/issues) page
- Review the API documentation at `/docs`
- Run the test suite to verify functionality
- Check logs for debugging information

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT-4o API
- FastAPI community for the excellent framework
- Arabic language processing research community
- Contributors and testers who helped improve the platform

---

**منصة صوت العميل العربية** - Empowering businesses with Arabic customer insights through AI-powered analysis.