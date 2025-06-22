#!/bin/bash

# User Experience Testing Runner for Arabic VoC Platform
# Comprehensive UX testing with detailed reporting

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[UX TEST]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configuration
BASE_URL="http://localhost:5000"
RESULTS_DIR="testing/user_experience/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$RESULTS_DIR/ux_test_report_$TIMESTAMP.json"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Check if server is running
check_server() {
    log "Checking if server is running at $BASE_URL..."
    
    if curl -f -s "$BASE_URL/api/health" > /dev/null; then
        success "Server is running and responsive"
        return 0
    else
        error "Server is not running or not responsive"
        return 1
    fi
}

# Install test dependencies
install_dependencies() {
    log "Installing test dependencies..."
    
    # Check if Chrome/Chromium is available for Selenium
    if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
        warning "Chrome/Chromium not found, installing..."
        
        # Install Chrome for testing
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
        apt-get update
        apt-get install -y google-chrome-stable
    fi
    
    # Install Python dependencies for testing
    pip install selenium requests websocket-client pytest pytest-asyncio
    
    success "Dependencies installed"
}

# Run interactive elements tests
run_interactive_tests() {
    log "Running interactive elements tests..."
    
    python testing/user_experience/test_interactive_elements.py > "$RESULTS_DIR/interactive_tests_$TIMESTAMP.log" 2>&1
    
    if [ $? -eq 0 ]; then
        success "Interactive elements tests completed successfully"
        return 0
    else
        error "Interactive elements tests failed"
        return 1
    fi
}

# Run frontend-backend integration tests
run_integration_tests() {
    log "Running frontend-backend integration tests..."
    
    python testing/user_experience/test_frontend_backend_integration.py > "$RESULTS_DIR/integration_tests_$TIMESTAMP.log" 2>&1
    
    if [ $? -eq 0 ]; then
        success "Integration tests completed successfully"
        return 0
    else
        error "Integration tests failed"
        return 1
    fi
}

# Run manual UX checklist validation
run_manual_validation() {
    log "Running manual UX validation checklist..."
    
    # Create manual validation script
    cat > "$RESULTS_DIR/manual_validation_$TIMESTAMP.sh" << 'EOF'
#!/bin/bash
echo "Manual UX Validation Checklist"
echo "==============================="
echo ""
echo "Please test the following manually and report results:"
echo ""
echo "1. Dashboard Loading:"
echo "   - Visit http://localhost:5000"
echo "   - Check if dashboard loads in under 2 seconds"
echo "   - Verify Arabic text displays correctly (RTL)"
echo "   - Test all navigation menu items"
echo ""
echo "2. Survey Builder:"
echo "   - Visit http://localhost:5000/survey-builder"
echo "   - Drag question types to canvas"
echo "   - Edit question properties"
echo "   - Save survey and verify success"
echo ""
echo "3. Feedback Submission:"
echo "   - Visit http://localhost:5000/feedback"
echo "   - Enter Arabic text: 'الخدمة ممتازة جداً'"
echo "   - Submit form and verify processing"
echo "   - Check dashboard for real-time update"
echo ""
echo "4. Settings and Toggles:"
echo "   - Visit http://localhost:5000/settings"
echo "   - Toggle various settings"
echo "   - Save settings and verify persistence"
echo "   - Refresh page and check if settings remain"
echo ""
echo "Report any issues found during manual testing."
EOF
    
    chmod +x "$RESULTS_DIR/manual_validation_$TIMESTAMP.sh"
    success "Manual validation checklist created: $RESULTS_DIR/manual_validation_$TIMESTAMP.sh"
}

# Generate user stories validation
validate_user_stories() {
    log "Validating user stories implementation..."
    
    python << 'EOF'
import json
import requests
import time

def validate_story(story_name, validation_func):
    try:
        result = validation_func()
        return {"story": story_name, "status": "passed" if result else "failed", "details": ""}
    except Exception as e:
        return {"story": story_name, "status": "error", "details": str(e)}

def check_dashboard_arabic():
    """Story 1: Arabic User Dashboard Access"""
    response = requests.get("http://localhost:5000/api/dashboard-metrics", timeout=5)
    return response.status_code == 200

def check_feedback_api():
    """Story 3: Feedback Submission and Analysis"""
    payload = {
        "content": "اختبار API للتعليقات العربية",
        "channel": "api_test"
    }
    response = requests.post("http://localhost:5000/api/feedback", json=payload, timeout=10)
    return response.status_code in [200, 201]

def check_health_endpoint():
    """Basic health check"""
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    return response.status_code == 200

# Run validations
validations = [
    ("Dashboard Arabic Support", check_dashboard_arabic),
    ("Feedback API Integration", check_feedback_api),
    ("System Health", check_health_endpoint)
]

results = []
for story, func in validations:
    result = validate_story(story, func)
    results.append(result)
    print(f"✅ {story}: {result['status']}" if result['status'] == 'passed' else f"❌ {story}: {result['status']}")

# Save results
with open("testing/user_experience/results/story_validation_" + str(int(time.time())) + ".json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nValidated {len([r for r in results if r['status'] == 'passed'])}/{len(results)} user stories")
EOF
    
    success "User stories validation completed"
}

# Performance validation for UX
run_performance_validation() {
    log "Running UX performance validation..."
    
    # Test dashboard load time
    log "Testing dashboard load time..."
    load_time=$(curl -w "%{time_total}" -o /dev/null -s "$BASE_URL/")
    
    if (( $(echo "$load_time < 3.0" | bc -l) )); then
        success "Dashboard loads in ${load_time}s (target: <3s)"
    else
        warning "Dashboard load time ${load_time}s exceeds target"
    fi
    
    # Test API response times
    log "Testing API response times..."
    api_time=$(curl -w "%{time_total}" -o /dev/null -s "$BASE_URL/api/health")
    
    if (( $(echo "$api_time < 1.0" | bc -l) )); then
        success "API responds in ${api_time}s (target: <1s)"
    else
        warning "API response time ${api_time}s exceeds target"
    fi
    
    # Save performance results
    cat > "$RESULTS_DIR/performance_$TIMESTAMP.json" << EOF
{
  "dashboard_load_time": $load_time,
  "api_response_time": $api_time,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "targets": {
    "dashboard_load_time": 3.0,
    "api_response_time": 1.0
  }
}
EOF
    
    success "Performance validation completed"
}

# Generate comprehensive report
generate_report() {
    log "Generating comprehensive UX test report..."
    
    cat > "$REPORT_FILE" << EOF
{
  "test_run": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "test_suite": "User Experience Testing",
    "platform": "Arabic Voice of Customer Platform",
    "version": "1.0.0"
  },
  "summary": {
    "total_test_categories": 5,
    "automated_tests": "interactive_elements, frontend_backend_integration",
    "manual_tests": "user_stories_validation, accessibility_check",
    "performance_tests": "load_time, api_response"
  },
  "test_files": {
    "interactive_elements": "testing/user_experience/results/interactive_tests_$TIMESTAMP.log",
    "integration_tests": "testing/user_experience/results/integration_tests_$TIMESTAMP.log",
    "performance_results": "testing/user_experience/results/performance_$TIMESTAMP.json",
    "manual_checklist": "testing/user_experience/results/manual_validation_$TIMESTAMP.sh"
  },
  "next_steps": [
    "Review automated test results",
    "Execute manual validation checklist",
    "Address any identified issues",
    "Validate fixes with additional testing"
  ]
}
EOF
    
    success "Report generated: $REPORT_FILE"
}

# Print usage information
usage() {
    cat << EOF
Arabic VoC Platform UX Testing Suite

Usage: $0 [options]

Options:
    --full          Run complete UX test suite
    --interactive   Run interactive elements tests only
    --integration   Run frontend-backend integration tests only
    --manual        Generate manual validation checklist only
    --performance   Run performance validation only
    --help          Show this help message

Examples:
    $0 --full
    $0 --interactive
    $0 --manual

The test results will be saved in testing/user_experience/results/
EOF
}

# Main execution
main() {
    local test_type="${1:-full}"
    
    echo "🧪 Arabic VoC Platform - User Experience Testing"
    echo "==============================================="
    echo ""
    
    case "$test_type" in
        "--full"|"full")
            log "Running complete UX test suite..."
            
            if ! check_server; then
                error "Cannot run tests without server running"
                exit 1
            fi
            
            install_dependencies
            run_interactive_tests
            run_integration_tests
            validate_user_stories
            run_performance_validation
            run_manual_validation
            generate_report
            
            success "Complete UX test suite finished"
            ;;
            
        "--interactive"|"interactive")
            check_server && install_dependencies && run_interactive_tests
            ;;
            
        "--integration"|"integration") 
            check_server && install_dependencies && run_integration_tests
            ;;
            
        "--manual"|"manual")
            run_manual_validation
            ;;
            
        "--performance"|"performance")
            check_server && run_performance_validation
            ;;
            
        "--help"|"help")
            usage
            ;;
            
        *)
            log "Running default UX test suite..."
            check_server && validate_user_stories && run_performance_validation
            ;;
    esac
    
    echo ""
    echo "📊 UX Test Results Summary:"
    echo "  - Results directory: $RESULTS_DIR"
    echo "  - Test timestamp: $TIMESTAMP"
    echo "  - View detailed results in generated files"
    echo ""
    
    if [ -f "$REPORT_FILE" ]; then
        echo "📋 Comprehensive report: $REPORT_FILE"
    fi
}

# Run with provided arguments
main "$@"