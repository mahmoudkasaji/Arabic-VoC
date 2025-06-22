# Development Tools

This folder contains utilities and tools for developing and maintaining the Arabic VoC Platform.

## Available Tools

### Code Quality (`code_quality/`)
- `check_quality.py` - Comprehensive code quality validation
- Checks syntax, imports, documentation, test coverage, and Arabic encoding

### Performance Analysis (`performance_analysis/`)
- Performance profiling and optimization tools
- Benchmarking utilities for Arabic text processing
- Load testing scripts

### Data Migration (`data_migration/`)
- Database migration utilities
- Data import/export tools
- Backup and restore scripts

## Usage

### Code Quality Check
```bash
# Run complete quality validation
python tools/code_quality/check_quality.py

# Quick syntax check only
python tools/code_quality/check_quality.py --syntax-only
```

### Performance Analysis
```bash
# Profile Arabic text processing
python tools/performance_analysis/profile_arabic.py

# Benchmark agent system
python tools/performance_analysis/benchmark_agents.py
```

### Data Migration
```bash
# Export feedback data
python tools/data_migration/export_data.py --format json

# Import from legacy system
python tools/data_migration/import_legacy.py --source data.csv
```

These tools help maintain code quality, optimize performance, and manage data effectively during development and deployment.