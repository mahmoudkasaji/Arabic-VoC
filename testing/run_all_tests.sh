#!/bin/bash

# Comprehensive test runner for Arabic VoC Platform
# Runs all test categories with proper reporting

echo "🧪 Arabic VoC Platform - Comprehensive Test Suite"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test categories
echo ""
echo "📋 Test Categories:"
echo "  1. Unit Tests (Component-level)"
echo "  2. Integration Tests (System interaction)"  
echo "  3. Performance Tests (Speed and efficiency)"
echo "  4. Security Tests (Data protection)"
echo "  5. User Experience Tests (End-to-end workflows)"
echo ""

# Function to run test category
run_test_category() {
    local category=$1
    local description=$2
    
    echo "🔄 Running $description..."
    
    if python -m pytest testing/$category/ -v --tb=short; then
        echo -e "${GREEN}✅ $description - PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ $description - FAILED${NC}"
        return 1
    fi
}

# Initialize counters
total_categories=5
passed_categories=0

# Run each test category
echo "🚀 Starting test execution..."
echo ""

# Unit Tests
if run_test_category "unit" "Unit Tests"; then
    ((passed_categories++))
fi
echo ""

# Integration Tests  
if run_test_category "integration" "Integration Tests"; then
    ((passed_categories++))
fi
echo ""

# Performance Tests
if run_test_category "performance" "Performance Tests"; then
    ((passed_categories++))
fi
echo ""

# Security Tests
if run_test_category "security" "Security Tests"; then
    ((passed_categories++))
fi
echo ""

# User Experience Tests
if run_test_category "user_experience" "User Experience Tests"; then
    ((passed_categories++))
fi
echo ""

# Generate summary
echo "📊 Test Summary"
echo "==============="
echo "Categories Passed: $passed_categories/$total_categories"

if [ $passed_categories -eq $total_categories ]; then
    echo -e "${GREEN}🎉 All test categories PASSED! Platform is healthy.${NC}"
    exit 0
elif [ $passed_categories -ge 4 ]; then
    echo -e "${YELLOW}⚠️  Most tests passed. Minor issues detected.${NC}"
    exit 1
else
    echo -e "${RED}🚨 Multiple test failures. Requires immediate attention.${NC}"
    exit 2
fi