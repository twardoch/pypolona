#!/bin/bash
# this_file: scripts/build.sh
# Local build script for PyPolona

set -e

echo "🔧 Setting up build environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e .[dev]

echo "✅ Build environment ready!"