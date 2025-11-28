#!/bin/bash
# Convenient test runner script for local development

set -e

echo "🧪 Running test suite..."
echo ""

# Set environment variable for Firebase credentials
export FIREBASE_CREDENTIALS=/dev/null

# Parse command line arguments
COVERAGE_THRESHOLD=95
VERBOSE=""
HTML_REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --html)
            HTML_REPORT=true
            shift
            ;;
        --threshold)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose         Verbose output"
            echo "  --html               Generate HTML coverage report"
            echo "  --threshold NUM      Coverage threshold (default: 95)"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh --verbose --html"
            echo "  ./run_tests.sh --threshold 90"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run './run_tests.sh --help' for usage"
            exit 1
            ;;
    esac
done

# Run tests with coverage
if [ "$HTML_REPORT" = true ]; then
    pytest --cov=. --cov-report=term --cov-report=html --cov-config=.coveragerc $VERBOSE
    echo ""
    echo "📊 HTML coverage report generated in htmlcov/"
    echo "   Open htmlcov/index.html in your browser"
else
    pytest --cov=. --cov-report=term --cov-config=.coveragerc $VERBOSE
fi

# Check coverage threshold
echo ""
echo "🎯 Checking coverage threshold (>= ${COVERAGE_THRESHOLD}%)..."
coverage report --fail-under=$COVERAGE_THRESHOLD

echo ""
echo "✅ All tests passed with sufficient coverage!"
