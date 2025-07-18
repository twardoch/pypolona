#!/bin/bash
# this_file: scripts/test.sh
# Local test script for PyPolona

set -e

echo "🧪 Running PyPolona test suite..."

# Activate virtual environment
source .venv/bin/activate

# Run linting
echo "📋 Running linting checks..."
echo "  - ruff check"
ruff check .
echo "  - ruff format check"
ruff format --check .

# Run type checking
echo "🔍 Running type checks..."
mypy pypolona/

# Run tests with coverage
echo "🧪 Running tests with coverage..."
pytest --cov=pypolona --cov-report=term-missing --cov-report=html

echo "✅ All tests passed!"