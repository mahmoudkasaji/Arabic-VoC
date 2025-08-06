# Installation Guide - Fixing Deployment Issues

## Quick Fix for uv Build System Error

The deployment error you encountered is due to uv build system conflicts with the pyproject.toml setup. Here are the applied fixes:

### ✅ Changes Made

1. **Simplified pyproject.toml**
   - Removed version constraints that cause uv conflicts
   - Simplified build system configuration
   - Removed complex metadata that can cause build issues

2. **Created setup.py Fallback**
   - Traditional setuptools configuration as backup
   - Ensures compatibility with standard Python packaging

3. **Added Build Configuration**
   - `deployment.toml` with uv cache disabling
   - Environment variables to force pip usage
   - Fallback build commands

4. **Created build_fallback.sh**
   - Manual installation script for dependencies
   - Bypasses uv build system entirely
   - Verifies installation success

### 🚀 Deployment Options

#### Option 1: Automatic (Recommended)
The simplified pyproject.toml should now work with Replit deployments.

#### Option 2: Manual Fallback
If deployment still fails, run:
```bash
./build_fallback.sh
```

#### Option 3: Individual Package Installation
Use the packager tool to install dependencies individually if needed.

### 🔧 Technical Details

**Root Cause**: uv build system was trying to create isolated Python environments that conflicted with Replit's container setup.

**Solution**: Disabled uv caching and provided multiple fallback installation methods.

### 📝 Environment Variables Added
- `UV_SYSTEM_PYTHON=1` - Forces uv to use system Python
- `PIP_NO_BUILD_ISOLATION=1` - Disables build isolation  
- `PIP_NO_CACHE_DIR=1` - Prevents cache conflicts

The platform should now deploy successfully on Replit!