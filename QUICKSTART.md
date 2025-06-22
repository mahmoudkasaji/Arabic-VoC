# Quick Start Guide - Arabic VoC Platform

## Get Started in 5 Minutes

### 1. Prerequisites
- Python 3.11 or higher
- PostgreSQL 13+ (or use SQLite for development)
- OpenAI API key

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-org/arabic-voc-platform
cd arabic-voc-platform

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env with your configuration
```

### 3. Configuration
```bash
# Required environment variables
export DATABASE_URL="postgresql://user:pass@localhost/arabicvoc"
export OPENAI_API_KEY="your-openai-api-key"
export SECRET_KEY="your-secret-key"
```

### 4. Initialize Database
```bash
# Create database tables
python app/main.py
```

### 5. Run the Application
```bash
# Start the server
python app/main.py

# Or using Gunicorn for production
gunicorn --bind 0.0.0.0:5000 app.main:app
```

### 6. Access the Platform
- Open your browser to `http://localhost:5000`
- Default admin login: `admin@example.com` / `admin123`
- Start exploring the Arabic feedback analysis!

## Next Steps

### Explore Features
1. **Submit Test Feedback**: Go to `/feedback` and submit Arabic text
2. **View Analytics**: Check `/analytics` for real-time insights  
3. **Create Surveys**: Use `/survey-builder` to design custom surveys
4. **Configure Integrations**: Set up data sources in `/integrations`

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest testing/ -v

# Start with auto-reload
export FLASK_ENV=development
python app/main.py
```

### Production Deployment
```bash
# Use production configuration
export FLASK_ENV=production

# Deploy to Replit
# The platform is optimized for Replit deployment
# Just push to your Replit repository and it will auto-deploy

# Or deploy with Docker
docker build -t arabic-voc .
docker run -p 5000:5000 arabic-voc
```

## Need Help?

- **Documentation**: Check `/documentation/` for comprehensive guides
- **Testing**: See `/testing/guide/` for testing explanations
- **Arabic Docs**: Read `README_ARABIC.md` for Arabic documentation
- **Issues**: Report problems in GitHub Issues
- **Support**: Contact support@arabicvoc.com

## Quick Commands Reference

```bash
# Run all tests
python -m pytest testing/ -v

# Test Arabic analysis specifically  
python -m pytest testing/integration/test_agent_orchestration.py -v

# Check system health
curl http://localhost:5000/api/health

# Submit test feedback via API
curl -X POST http://localhost:5000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"content": "الخدمة ممتازة جداً", "channel": "api"}'
```

Welcome to the Arabic Voice of Customer Platform! 🚀