# API to Flask Migration Guide

## Overview
This guide documents the migration from FastAPI endpoints to Flask routes for internal operations in the Voice of Customer platform.

## Migration Summary

### ✅ Migrated to Flask Routes

#### Contact Management
- **Old**: `/api/contacts/*` (FastAPI Blueprint)
- **New**: Direct Flask routes in `routes.py` and `contact_routes.py`
- **Endpoints**:
  - `GET /contacts/search` - Search contacts with filters
  - `POST /contacts/edit/<id>` - Edit contact information
  - `POST /contacts/delete/<id>` - Hard delete contacts
  - `POST /contacts/bulk-import` - CSV bulk import
  - `GET /contacts/export` - Export contacts as CSV
  - `POST /contacts/create` - Create new contacts

#### User Preferences
- **Old**: `/api/user/preferences` (FastAPI)
- **New**: Flask routes in `routes.py`
- **Endpoints**:
  - `GET /user/preferences` - Get user settings
  - `POST /user/preferences` - Update user settings

#### Integration Testing
- **Old**: `/api/integrations/test/<id>` (FastAPI)
- **New**: Flask route in `routes.py`
- **Endpoints**:
  - `POST /integrations/test/<integration_id>` - Test specific integrations

#### Survey Operations (Simple)
- **Old**: Complex FastAPI endpoints
- **New**: Simplified Flask routes
- **Endpoints**:
  - `GET /surveys/list` - List surveys with filtering
  - `POST /surveys/<id>/distribute` - Survey distribution

#### Feedback Collection (Simple)
- **Old**: Complex FastAPI with async processing
- **New**: Simple Flask route
- **Endpoints**:
  - `POST /feedback/submit` - Simple feedback submission

### 🔄 Kept as API Blueprints (Complex Operations)

#### Analytics APIs
- `api/analytics_live.py` - Real-time analytics with WebSocket support
- `api/enhanced_analytics.py` - AI-powered text analysis
- `api/professional_reports.py` - Complex report generation

#### External Integrations
- Integration status monitoring (kept for backward compatibility)
- Feedback widget API (complex widget logic)

## Benefits Achieved

### Performance Improvements
- **Reduced Latency**: Direct database operations without async overhead
- **Simpler Authentication**: Native Replit Auth integration
- **Better Session Management**: Flask-Login integration

### Development Benefits
- **Simplified Code**: No async/await for simple CRUD operations
- **Better Debugging**: Flask's native error handling
- **Easier Testing**: Direct route testing without API client setup

### Architecture Benefits
- **Hybrid Approach**: Flask for simple operations, APIs for complex processing
- **Better Integration**: Native template rendering and form handling
- **Reduced Complexity**: Fewer moving parts for internal operations

## File Changes

### Deprecated Files
- `api/contacts_api_deprecated.py` (moved from `api/contacts.py`)
- `api/user_preferences_deprecated.py` (moved from `api/user_preferences.py`)

### Updated Files
- `routes.py` - Added all new Flask routes
- `contact_routes.py` - Enhanced contact management routes
- `app.py` - Updated blueprint registration
- `replit.md` - Documented migration

## Testing

### Flask Route Testing
```bash
# Test user preferences
curl -X GET http://localhost:5000/user/preferences

# Test contact search
curl -X GET http://localhost:5000/contacts/search?q=test

# Test feedback submission
curl -X POST http://localhost:5000/feedback/submit \
  -H "Content-Type: application/json" \
  -d '{"content":"Test feedback","rating":5}'

# Test survey listing
curl -X GET http://localhost:5000/surveys/list
```

### API Blueprint Testing (Still Active)
```bash
# Test integration status
curl -X GET http://localhost:5000/api/integrations/status

# Test live analytics
curl -X GET http://localhost:5000/api/analytics/live/dashboard

# Test enhanced analytics
curl -X POST http://localhost:5000/api/analytics/enhanced-text
```

## Migration Guidelines

### When to Use Flask Routes
- Simple CRUD operations
- Form processing
- File uploads/downloads
- Direct template rendering
- Session management
- Internal administrative tasks

### When to Keep API Blueprints
- Complex data processing
- AI/ML integrations
- Real-time features (WebSocket)
- External API integrations
- Heavy computational tasks
- Multi-step workflows

## Rollback Plan
If issues arise, the deprecated API files can be restored:
1. Rename `*_deprecated.py` files back to original names
2. Restore blueprint registration in `app.py`
3. Update frontend to use API endpoints instead of Flask routes

## Next Steps
1. Monitor performance improvements
2. Update frontend to use new Flask routes
3. Remove deprecated API files after validation period
4. Update documentation and tests