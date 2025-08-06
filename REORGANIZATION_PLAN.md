# File Reorganization Plan

## Current Issues Identified:
- Root directory contains 30+ files that should be nested
- Mixed file types (configs, routes, models, docs) at root level
- Duplicate functionality across multiple files
- Poor separation of concerns

## Recommended Structure:

```
project/
├── app/                          # Core application
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration (move from root)
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── auth.py             # Move from models/auth.py
│   │   ├── contacts.py         # Move from models/contacts.py
│   │   ├── survey.py           # Move from models/survey.py
│   │   └── unified.py          # Rename from models_unified.py
│   ├── routes/                  # Route blueprints
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication routes
│   │   ├── contacts.py         # Move contact_routes.py here
│   │   ├── ai_analysis.py      # Move routes_ai_analysis.py here
│   │   ├── feedback.py         # Move routes_feedback_widget.py here
│   │   └── main.py             # Move routes.py here
│   ├── api/                     # API endpoints (already organized)
│   ├── templates/               # HTML templates (already organized)
│   ├── static/                  # Static assets (already organized)
│   └── utils/                   # App-specific utilities
├── core/                        # Core business logic
│   ├── __init__.py
│   ├── auth/                    # Authentication logic
│   │   ├── __init__.py
│   │   └── replit_auth.py      # Move from root
│   └── analytics/               # Analytics processors
│       ├── __init__.py
│       └── simple_analyzer.py  # Move simple_arabic_analyzer.py
├── config/                      # Configuration files
│   ├── __init__.py
│   ├── development.py
│   ├── production.py
│   └── docker/                  # Docker configs
│       ├── Dockerfile.prod     # Move from root
│       └── docker-compose.prod.yml  # Move from root
├── docs/                        # Documentation (already organized)
├── scripts/                     # Utility scripts (already organized)
├── tests/                       # Test files (already organized)
├── utils/                       # Global utilities (already organized)
├── workflows/                   # Replit workflows (already organized)
├── deployment/                  # Deployment configs (already organized)
├── tools/                       # Development tools (already organized)
├── translations/                # Language files (already organized)
└── temp/                        # Temporary/debug files
    ├── cookies.txt             # Move from root
    ├── debug.cookie            # Move from root
    ├── test*.cookie            # Move all cookie files from root
    └── demo_files/             # Demo and visualization files
        ├── demo_flow_visualization.html
        ├── demo_user_flow.md
        └── enterprise_architecture_visualization.html
```

## Files to Move:

### Root → app/
- config.py → app/config.py
- models_unified.py → app/models/unified.py

### Root → app/routes/
- contact_routes.py → app/routes/contacts.py
- routes.py → app/routes/main.py
- routes_ai_analysis.py → app/routes/ai_analysis.py
- routes_feedback_widget.py → app/routes/feedback.py

### Root → core/auth/
- replit_auth.py → core/auth/replit_auth.py

### Root → core/analytics/
- simple_arabic_analyzer.py → core/analytics/simple_analyzer.py

### Root → config/docker/
- Dockerfile.prod → config/docker/Dockerfile.prod
- docker-compose.prod.yml → config/docker/docker-compose.prod.yml

### Root → temp/
- cookies.txt, debug.cookie, test*.cookie → temp/
- demo_flow_visualization.html → temp/demo_files/
- demo_user_flow.md → temp/demo_files/
- enterprise_architecture_visualization.html → temp/demo_files/

### Root → docs/
- product_analysis.md → docs/
- product_plan_integrations_redesign.md → docs/

## Benefits:
1. **Clear separation of concerns**
2. **Easier navigation and maintenance**
3. **Better organization for new developers**
4. **Cleaner root directory**
5. **Logical grouping of related files**

## Implementation Priority:
1. HIGH: Move route files to app/routes/
2. HIGH: Move config and auth files
3. MEDIUM: Move demo and temp files
4. LOW: Move documentation files (already well organized)