# Arabic Voice of Customer Platform

## منصة صوت العميل العربية

A comprehensive Arabic-first feedback processing platform that leverages AI-powered sentiment analysis to collect, process, and analyze customer feedback from multiple channels.

## Features

### 🌟 Core Capabilities
- **Multi-channel Feedback Collection**: Website, mobile app, email, phone, social media, WhatsApp, SMS, surveys, and chatbots
- **AI-Powered Arabic Sentiment Analysis**: Advanced sentiment analysis using OpenAI GPT-4o optimized for Arabic text
- **Real-time Analytics Dashboard**: Comprehensive metrics and insights with RTL support
- **Arabic-First Design**: Full RTL support with proper Arabic text handling and cultural context

### 🚀 Technical Highlights
- **FastAPI Backend**: High-performance async API with automatic documentation
- **PostgreSQL Database**: Scalable database with Arabic text optimization
- **Advanced Caching**: Multi-level caching for improved performance
- **Security Validation**: Comprehensive input validation and sanitization
- **Performance Optimization**: Batch processing and intelligent caching strategies

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd arabic-voc-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/arabic_voc"
   export OPENAI_API_KEY="your-openai-api-key"
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the platform**
   - Main Dashboard: http://localhost:8000/
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Feedback Collection
- `POST /api/feedback/submit` - Submit new feedback
- `GET /api/feedback/list` - List feedback with filters
- `GET /api/feedback/{id}` - Get specific feedback
- `DELETE /api/feedback/{id}` - Delete feedback

### Analytics
- `GET /api/analytics/dashboard` - Dashboard metrics
- `GET /api/analytics/sentiment` - Sentiment analysis metrics
- `GET /api/analytics/trends` - Trend analysis
- `GET /api/analytics/export` - Export analytics data

### Example Usage

```python
import requests

# Submit Arabic feedback
feedback_data = {
    "content": "الخدمة ممتازة جداً وأنصح بها بشدة",
    "channel": "website",
    "rating": 5,
    "customer_email": "customer@example.com"
}

response = requests.post(
    "http://localhost:8000/api/feedback/submit",
    json=feedback_data
)

print(response.json())
```

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest tests/test_arabic_processing.py  # Arabic processing tests
pytest tests/test_security.py  # Security tests
pytest tests/test_performance.py  # Performance tests

# Run with coverage
pytest --cov=utils --cov=api --cov-report=html
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load tests
cd performance
python load_test.py

# Or run interactively
locust -f load_test.py --host http://localhost:8000
```

## Architecture

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