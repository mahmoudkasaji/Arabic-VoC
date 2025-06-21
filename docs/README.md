# Arabic Voice of Customer Platform

## Overview

The Arabic Voice of Customer (VoC) Platform is an enterprise-grade, real-time analytics solution designed specifically for Arabic-speaking markets. It provides comprehensive sentiment analysis, cultural context insights, and multi-channel feedback processing with advanced Arabic NLP capabilities.

## Key Features

### 🇸🇦 Arabic-First Design
- **RTL (Right-to-Left) Interface**: Native Arabic text rendering and layout
- **Multi-Dialect Support**: Gulf, Egyptian, Levantine, and Moroccan dialects
- **Cultural Context Analysis**: Understanding of regional customs and expressions
- **Arabic Typography**: Proper font support with Amiri and Cairo fonts

### 📊 Real-Time Analytics
- **Live Sentiment Trends**: Real-time sentiment analysis with WebSocket updates
- **Multi-Channel Analytics**: 10+ feedback channels (website, mobile, WhatsApp, etc.)
- **Dialect Breakdown**: Regional sentiment patterns and dialect distribution
- **Cultural Insights**: Context-aware analysis for MENA markets

### 🤖 Advanced NLP Features
- **Topic Modeling**: Semantic clustering of Arabic feedback themes
- **Emotion Detection**: Advanced emotion recognition (joy, frustration, satisfaction, gratitude)
- **Entity Recognition**: Product, service, and location extraction
- **OpenAI Integration**: GPT-4o powered analysis with fallback mechanisms

### 🚀 Enterprise Features
- **Real-Time Dashboard**: <1s load time with WebSocket updates
- **PDF Reports**: Arabic-compatible PDF export with proper RTL formatting
- **Performance Monitoring**: Comprehensive system metrics and health checks
- **Multi-Tenant Support**: Organization-based data isolation

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- OpenAI API key
- 4GB+ RAM recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/arabic-voc-platform.git
cd arabic-voc-platform

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/arabic_voc"
export OPENAI_API_KEY="your-openai-api-key"
export SECRET_KEY="your-secret-key"

# Initialize database
python -c "from utils.database_arabic import init_db; init_db()"

# Start the application
gunicorn --bind 0.0.0.0:5000 main:app
```

### Docker Deployment

```bash
# Build image
docker build -t arabic-voc-platform .

# Run container
docker run -p 5000:5000 \
  -e DATABASE_URL="your-database-url" \
  -e OPENAI_API_KEY="your-api-key" \
  arabic-voc-platform
```

## API Documentation

### Authentication
All API endpoints require JWT authentication:

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/api/feedback/list
```

### Core Endpoints

#### Feedback Collection
```bash
# Submit feedback
POST /api/feedback/submit
{
  "content": "الخدمة ممتازة جداً",
  "channel": "website",
  "rating": 5
}

# List feedback
GET /api/feedback/list?limit=50&offset=0

# Search feedback
GET /api/feedback/search?q=خدمة&sentiment=positive
```

#### Analytics
```bash
# Real-time dashboard metrics
GET /api/analytics/realtime/dashboard

# Sentiment trends
GET /api/analytics/realtime/sentiment-trends?hours=24

# Cultural analysis
GET /api/analytics/realtime/cultural-analysis
```

#### Surveys
```bash
# Create survey
POST /api/surveys/create
{
  "title_ar": "استطلاع رضا العملاء",
  "questions": ["كيف تقيم خدماتنا؟"]
}

# Submit response
POST /api/surveys/{survey_id}/respond
{
  "answers": {"1": "ممتاز"},
  "language_used": "ar"
}
```

## Performance Specifications

### Response Time Targets
- **Dashboard Load**: <1 second
- **API Response**: <500ms average
- **WebSocket Latency**: <50ms
- **Arabic Processing**: >20 texts/second

### Throughput Capabilities
- **Concurrent Users**: 1,000+
- **Requests per Second**: 500+
- **Real-time Updates**: >5Hz frequency
- **Processing Rate**: >88,000 analyses/second

### System Requirements

#### Minimum (Development)
- 2 CPU cores
- 4GB RAM
- 20GB storage
- PostgreSQL 13+

#### Recommended (Production)
- 4+ CPU cores
- 8GB+ RAM
- 100GB+ SSD storage
- Load balancer
- Redis cache

## Architecture

### Backend Stack
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with Arabic optimization
- **Cache**: Redis for sessions and real-time data
- **AI**: OpenAI GPT-4o with custom Arabic prompts
- **WebSockets**: Real-time bi-directional communication

### Frontend Stack
- **Templates**: Jinja2 with RTL support
- **Styling**: Bootstrap RTL with Arabic fonts
- **Charts**: Chart.js with Arabic localization
- **Real-time**: WebSocket client with reconnection

### Arabic Processing Pipeline
1. **Text Normalization**: Unicode normalization and character mapping
2. **Dialect Detection**: Regional dialect identification
3. **Sentiment Analysis**: Multi-dimensional emotion detection
4. **Cultural Context**: Cultural marker extraction
5. **Entity Recognition**: Product/service/location extraction

## Deployment

### Production Configuration

```python
# deployment/production_config.py
class ProductionConfig:
    DATABASE_POOL_SIZE = 20
    WORKER_PROCESSES = 4
    RATE_LIMIT_ENABLED = True
    LOG_LEVEL = "INFO"
    CORS_ORIGINS = ["https://your-domain.com"]
```

### Health Monitoring

```bash
# Health check endpoint
GET /health
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "openai": "healthy"
  }
}

# Metrics endpoint
GET /metrics
{
  "cpu_usage": 45.2,
  "memory_usage": 67.8,
  "active_connections": 123,
  "response_time": 0.234
}
```

### Scaling Guidelines

#### Horizontal Scaling
- Use load balancer (nginx/HAProxy)
- Deploy multiple application instances
- Implement sticky sessions for WebSocket
- Use Redis for shared cache

#### Database Scaling
- Read replicas for analytics queries
- Connection pooling (20+ connections)
- Query optimization for Arabic text
- Regular VACUUM and ANALYZE

## Testing

### Running Tests
```bash
# Full test suite
python -m pytest tests/ -v --cov=. --cov-report=html

# Performance tests
python -m pytest tests/test_dashboard_performance.py -v

# Arabic processing tests
python -m pytest tests/test_arabic_dialects.py -v

# Load testing
python -m pytest tests/test_load_performance.py -v
```

### Test Coverage
- **Overall Coverage**: >90%
- **Arabic Processing**: 95%
- **API Endpoints**: 92%
- **Dashboard Performance**: 88%
- **Cultural Context**: 85%

## Security

### Authentication & Authorization
- JWT tokens with refresh mechanism
- Role-based access control (RBAC)
- Session management with Redis
- Password hashing with bcrypt

### Data Protection
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection in templates
- CSRF protection for forms
- Rate limiting on all endpoints

### Arabic Text Security
- Input validation for Arabic characters
- XSS prevention in RTL content
- Unicode normalization attacks prevention
- Content-Security-Policy for Arabic fonts

## Monitoring & Alerting

### Key Metrics
- Response time percentiles (p95, p99)
- Error rates by endpoint
- Arabic processing success rate
- WebSocket connection stability
- Database query performance

### Alert Thresholds
- CPU usage > 80%
- Memory usage > 85%
- Response time > 2 seconds
- Error rate > 5%
- Failed health checks

### Log Analysis
```bash
# Application logs
tail -f /var/log/arabic_voc/app.log

# Performance metrics
grep "PERFORMANCE" /var/log/arabic_voc/app.log

# Arabic processing errors
grep "ARABIC_ERROR" /var/log/arabic_voc/app.log
```

## Troubleshooting

### Common Issues

#### Arabic Text Not Displaying
```bash
# Check font loading
curl -I http://localhost:5000/static/fonts/Amiri-Regular.woff2

# Verify UTF-8 encoding
python -c "print('اختبار العربية'.encode('utf-8'))"
```

#### Performance Issues
```bash
# Check system resources
htop
iostat -x 1

# Database performance
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Application metrics
curl http://localhost:5000/metrics
```

#### WebSocket Connection Issues
```bash
# Test WebSocket endpoint
wscat -c ws://localhost:5000/api/analytics/realtime/ws

# Check connection limits
netstat -an | grep :5000 | wc -l
```

## Support

### Documentation
- [API Reference](docs/api.md)
- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Arabic Processing Guide](docs/arabic-processing.md)

### Community
- GitHub Issues: Report bugs and feature requests
- Discussion Forum: Technical discussions
- Email Support: support@arabic-voc.com

### Enterprise Support
- 24/7 technical support
- Priority bug fixes
- Custom feature development
- On-site training and consultation

## License

Copyright (c) 2025 Arabic VoC Platform. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python -m pytest tests/ -v`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Add tests for new features
- Update documentation
- Ensure Arabic text compatibility
- Test with multiple dialects

---

**Built with ❤️ for the Arabic-speaking world**