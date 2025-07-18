# this_file: tests/test_cli.py
"""Test CLI argument parsing and main entry point."""

import sys
import pytest
from unittest.mock import patch, MagicMock
from pypolona.__main__ import cli


def test_parser_creation():
    """Test that the argument parser can be created."""
    parser = cli()
    assert parser is not None
    assert parser.prog == "ppolona"


def test_parser_search_mode():
    """Test parsing search mode arguments."""
    parser = cli()
    
    # Test search mode
    args = parser.parse_args(["--search", "test", "query"])
    assert args.search is True
    assert args.query == ["test", "query"]


def test_parser_ids_mode():
    """Test parsing IDs mode arguments."""
    parser = cli()
    
    # Test IDs mode
    args = parser.parse_args(["--ids", "123", "456"])
    assert args.ids is True
    assert args.query == ["123", "456"]


def test_parser_download_options():
    """Test parsing download options."""
    parser = cli()
    
    # Test download with options
    args = parser.parse_args([
        "--download", 
        "--images", 
        "--download-dir", "/tmp/test",
        "--max-pages", "10",
        "--no-text-pdf",
        "--no-overwrite",
        "https://polona.pl/item/test,123/"
    ])
    
    assert args.download is True
    assert args.images is True
    assert args.download_dir == "/tmp/test"
    assert args.max_pages == 10
    assert args.textpdf_skip is True
    assert args.skip is True
    assert args.query == ["https://polona.pl/item/test,123/"]


def test_parser_output_formats():
    """Test parsing output format options."""
    parser = cli()
    
    for fmt in ["ids", "urls", "yaml", "json"]:
        args = parser.parse_args(["--format", fmt, "test"])
        assert args.format == fmt


def test_parser_sort_options():
    """Test parsing sort options."""
    parser = cli()
    
    valid_sorts = ["score desc", "date desc", "date asc", "title asc", "creator asc"]
    for sort_opt in valid_sorts:
        args = parser.parse_args(["--sort", sort_opt, "test"])
        assert args.sort == sort_opt


def test_parser_language_options():
    """Test parsing language options."""
    parser = cli()
    
    args = parser.parse_args(["--lang", "polski", "angielski", "test"])
    assert args.search_languages == ["polski", "angielski"]


def test_parser_version():
    """Test version argument."""
    parser = cli()
    
    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])


def test_parser_help():
    """Test help argument."""
    parser = cli()
    
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])


@patch('pypolona.__main__.Polona')
def test_main_search_execution(mock_polona_class):
    """Test main function executes search correctly."""
    mock_polona = MagicMock()
    mock_polona_class.return_value = mock_polona
    
    from pypolona.__main__ import main
    
    # Test search execution
    test_args = ["--search", "test query"]
    with patch.object(sys, 'argv', ['ppolona'] + test_args):
        main()
    
    # Verify Polona was instantiated and called correctly
    mock_polona_class.assert_called_once()
    mock_polona.run.assert_called_once()


@patch('pypolona.__main__.Polona')
def test_main_download_execution(mock_polona_class):
    """Test main function executes download correctly."""
    mock_polona = MagicMock()
    mock_polona_class.return_value = mock_polona
    
    from pypolona.__main__ import main
    
    # Test download execution
    test_args = ["--download", "https://polona.pl/item/test,123/"]
    with patch.object(sys, 'argv', ['ppolona'] + test_args):
        main()
    
    # Verify Polona was instantiated and called correctly
    mock_polona_class.assert_called_once()
    mock_polona.run.assert_called_once()