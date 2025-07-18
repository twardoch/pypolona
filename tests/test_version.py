# this_file: tests/test_version.py
"""Test version detection and git-tag-based versioning."""

import re
from pypolona import __version__


def test_version_format():
    """Test that version follows semantic versioning format."""
    # Allow semver format: major.minor.patch[-prerelease][+build]
    semver_pattern = r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    
    # Also allow unknown version for development
    if __version__ == "0.0.0+unknown":
        return
    
    assert re.match(semver_pattern, __version__), f"Version {__version__} does not follow semantic versioning"


def test_version_is_string():
    """Test that version is a string."""
    assert isinstance(__version__, str)


def test_version_not_empty():
    """Test that version is not empty."""
    assert __version__
    assert len(__version__) > 0