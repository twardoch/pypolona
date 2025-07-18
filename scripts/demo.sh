#!/bin/bash
# this_file: scripts/demo.sh
# Demo script showing the complete git-tag-based semversioning workflow

set -e

echo "🎯 PyPolona Git-Tag-Based Semversioning Demo"
echo "============================================="

echo "📋 Current project status:"
echo "  - Current version: $(grep "version =" pyproject.toml | cut -d'"' -f2)"
echo "  - Current git branch: $(git branch --show-current)"
echo "  - Latest git tag: $(git describe --tags --abbrev=0 2>/dev/null || echo "None")"

echo ""
echo "🔧 Running build and test..."
./scripts/build.sh
./scripts/test.sh

echo ""
echo "📦 Building package..."
source .venv/bin/activate
hatch build

echo ""
echo "📋 Available scripts:"
echo "  - ./scripts/build.sh      - Set up build environment"
echo "  - ./scripts/test.sh       - Run tests and linting"
echo "  - ./scripts/release.sh    - Create a new release"
echo "  - ./scripts/demo.sh       - This demo script"

echo ""
echo "🚀 To create a new release:"
echo "  ./scripts/release.sh 1.1.0"
echo ""
echo "This will:"
echo "  1. Run full build and test suite"
echo "  2. Create and push git tag v1.1.0"
echo "  3. Trigger GitHub Actions CI/CD pipeline"
echo "  4. Build multiplatform binaries"
echo "  5. Publish to PyPI"
echo "  6. Create GitHub release with artifacts"

echo ""
echo "🎯 GitHub Actions workflow provides:"
echo "  - ✅ Automated testing on Python 3.9-3.12"
echo "  - ✅ Linting and type checking"
echo "  - ✅ Multiplatform binary builds (Linux, macOS, Windows)"
echo "  - ✅ Automatic PyPI publishing"
echo "  - ✅ GitHub releases with downloadable artifacts"
echo "  - ✅ Git-tag-based semantic versioning"

echo ""
echo "✅ Demo completed successfully!"