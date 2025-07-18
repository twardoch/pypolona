#!/bin/bash
# this_file: scripts/release.sh
# Local release script for PyPolona

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.1.0"
    exit 1
fi

VERSION=$1

echo "🚀 Preparing release $VERSION..."

# Validate version format (basic semver check)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Version must be in format X.Y.Z (e.g., 1.1.0)"
    exit 1
fi

# Check if we're on a clean git state
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Working directory is not clean. Please commit or stash changes."
    exit 1
fi

# Run build and test
echo "🔧 Building and testing..."
./scripts/build.sh
./scripts/test.sh

# Build package
echo "📦 Building package..."
source .venv/bin/activate
hatch build

# Create and push tag
echo "🏷️  Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin "v$VERSION"

echo "✅ Release $VERSION created successfully!"
echo "📋 Next steps:"
echo "  - GitHub Actions will automatically build and test the release"
echo "  - Check the Actions tab for build status"
echo "  - Manual PyPI publish: twine upload dist/*"