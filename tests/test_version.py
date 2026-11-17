# this_file: tests/test_version.py
"""Test version detection and git-tag-based versioning."""

from packaging.version import Version

from pypolona import __version__


def test_version_format():
    """Test that the version is a valid PEP 440 version (hatch-vcs makes .devN between tags)."""
    if __version__ == "0.0.0+unknown":
        return
    Version(__version__)


def test_version_is_string():
    """Test that version is a string."""
    assert isinstance(__version__, str)


def test_version_not_empty():
    """Test that version is not empty."""
    assert __version__
    assert len(__version__) > 0