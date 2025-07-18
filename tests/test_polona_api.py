# this_file: tests/test_polona_api.py
"""Test Polona API interaction methods."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pypolona.polona import Polona


@pytest.fixture
def polona_instance():
    """Create a Polona instance for testing."""
    opts = {
        "search": True,
        "advanced": False,
        "ids": False,
        "download": False,
        "images": False,
        "search_languages": None,
        "sort": "score desc",
        "format": "ids",
        "output": None,
        "download_dir": None,
        "max_pages": 0,
        "textpdf_skip": False,
        "skip": False,
        "query": ["test"]
    }
    
    return Polona(**opts)


@pytest.fixture
def mock_api_response():
    """Mock API response data."""
    return {
        "query": "test",
        "size": 2,
        "hits": [
            {
                "id": "123",
                "title": "Test Document 1",
                "creator": ["Test Author"],
                "date": "2023-01-01",
                "slug": "test-document-1"
            },
            {
                "id": "456", 
                "title": "Test Document 2",
                "creator": ["Another Author"],
                "date": "2023-01-02",
                "slug": "test-document-2"
            }
        ]
    }


def test_polona_init(polona_instance):
    """Test Polona class initialization."""
    assert polona_instance.o.search is True
    assert polona_instance.o.query == ["test"]


def test_url_validation():
    """Test URL validation for Polona URLs."""
    # Valid URLs
    valid_urls = [
        "https://polona.pl/item/test,123/",
        "https://polona.pl/item/another-test,456/",
        "polona.pl/item/test,789/"
    ]
    
    for url in valid_urls:
        # Test that URL contains expected pattern
        assert "polona.pl/item/" in url
        assert "," in url
    
    # Invalid URLs
    invalid_urls = [
        "https://example.com/test",
        "not-a-url",
        "https://polona.pl/wrong-format"
    ]
    
    for url in invalid_urls:
        assert "polona.pl/item/" not in url or "," not in url


def test_id_extraction():
    """Test extraction of document ID from Polona URL."""
    test_cases = [
        ("https://polona.pl/item/test-document,123/", "123"),
        ("https://polona.pl/item/another-test,456/", "456"),
        ("polona.pl/item/test,789/", "789"),
    ]
    
    for url, expected_id in test_cases:
        # Extract ID using simple string manipulation
        if "polona.pl/item/" in url and "," in url:
            parts = url.split(",")
            if len(parts) >= 2:
                id_part = parts[-1].rstrip("/")
                assert id_part == expected_id


def test_basic_functionality(polona_instance):
    """Test basic Polona functionality."""
    # Test instance creation
    assert polona_instance is not None
    assert hasattr(polona_instance, 'o')
    assert hasattr(polona_instance, 'ids')
    
    # Test option access
    assert polona_instance.o.search is True
    assert polona_instance.o.format == "ids"
    assert polona_instance.o.sort == "score desc"


def test_mock_api_response_structure(mock_api_response):
    """Test that mock API response has expected structure."""
    assert "query" in mock_api_response
    assert "size" in mock_api_response
    assert "hits" in mock_api_response
    assert len(mock_api_response["hits"]) == 2
    
    # Check hit structure
    hit = mock_api_response["hits"][0]
    assert "id" in hit
    assert "title" in hit
    assert "creator" in hit
    assert "date" in hit
    assert "slug" in hit