# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-06-29

### Added
- Comprehensive development documentation: `PLAN.md`, `TODO.md`, and `CHANGELOG.md`
- `.dccache` to `.gitignore` file
- Helper methods in `polona.py` to break down complex functions:
  - `_prepare_download_paths()`
  - `_download_item_images()`
  - `_create_pdf_from_images()`
  - `_download_and_save_text_pdf()`
- Improved error handling with specific exception types
- More descriptive variable names throughout the codebase

### Changed
- **Major refactoring of `pypolona/polona.py`**:
  - Renamed variables for clarity (e.g., `r` → `response`, `jhits` → `json_hits`)
  - Replaced generic `Exception` catches with specific exceptions
  - Broke down the large `save_downloaded()` method into smaller helper functions
  - Improved type hints and reduced `# type: ignore` comments
  - Enhanced logging consistency and informativeness
- **Simplified `pypolona/__main__.py`**:
  - Removed commented-out `webgui` section using `Cli2Gui`
  - Removed redundant `if True:` block in `main()` function
- **Cleaned `app/dmgbuild_settings.py`**:
  - Removed extensive commented-out example configurations
  - Streamlined to focus on actual PyPolona settings
- **Updated `pyproject.toml`**:
  - Moved `biplist` to optional dev dependencies
  - Verified all listed dependencies are actively used

### Removed
- `app/ppolona.py` - redundant wrapper script (functionality covered by entry points)
- Commented-out code sections throughout the project
- Large Windows binary file `download/pypolona-win.zip` (42MB)

### Fixed
- Bug in `download_save_textpdf()` that was returning bytes instead of boolean
- Type safety issues in various parts of the code
- Resource management ensuring proper file closure with context managers

### Known Issues
- `src/gooey` directory still exists (vendored Gooey library) - removal pending
- `.dccache` file still tracked in git repository
- Some complex methods in `polona.py` could benefit from further decomposition
- Test coverage needs improvement

## [1.6.2] - Previous Release
- Last stable release before streamlining effort
