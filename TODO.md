# PyPolona TODO List - Path to Stable v1.0

## Phase 1: Clean Up Technical Debt ⚡ PRIORITY

- [ ] **Remove vendored dependencies**
  - [ ] Delete `src/gooey` directory completely
  - [ ] Verify GUI still works with ezgooey
  - [ ] Remove empty `src/` directory if no longer needed

- [ ] **Fix git tracking issues**
  - [ ] Remove `.dccache` from git tracking (`git rm --cached .dccache`)
  - [ ] Ensure `.gitignore` entries are working properly

- [ ] **Code style standardization**
  - [ ] Configure ruff in `pyproject.toml`
  - [ ] Run `ruff format` on entire codebase
  - [ ] Fix any linting issues
  - [ ] Set up pre-commit hooks

## Phase 2: Refactor Core Module

- [ ] **Break down `polona.py` into modules**
  - [ ] Create `api.py` for Polona API interactions
  - [ ] Create `downloader.py` for download management
  - [ ] Create `pdf_builder.py` for PDF operations
  - [ ] Create `models.py` for data structures
  - [ ] Create `utils.py` for helper functions
  - [ ] Create `constants.py` for configuration

- [ ] **Implement proper data models**
  - [ ] Replace dict-based items with dataclasses
  - [ ] Create TypedDict for API responses
  - [ ] Add proper type hints throughout

- [ ] **Improve remaining code quality issues**
  - [ ] Further decompose complex methods
  - [ ] Remove remaining `# type: ignore` comments
  - [ ] Replace `Any` types with specific types
  - [ ] Improve error messages for users

## Phase 3: Testing Infrastructure

- [ ] **Set up test framework**
  - [ ] Create `tests/` directory structure
  - [ ] Configure pytest in `pyproject.toml`
  - [ ] Add test fixtures and mocks

- [ ] **Write unit tests**
  - [ ] Test API interaction functions
  - [ ] Test download logic
  - [ ] Test PDF generation
  - [ ] Test CLI argument parsing
  - [ ] Test error handling

- [ ] **Integration tests**
  - [ ] Mock Polona API responses
  - [ ] Test full download workflows
  - [ ] Test different search modes
  - [ ] Test edge cases

- [ ] **Achieve 80%+ test coverage**
  - [ ] Set up coverage reporting
  - [ ] Add missing tests
  - [ ] Document testing procedures

## Phase 4: Build & Deployment

- [ ] **Automate builds**
  - [ ] Create GitHub Actions workflow for CI
  - [ ] Set up automated testing on PR
  - [ ] Configure multi-platform builds
  - [ ] Add release automation

- [ ] **Improve packaging**
  - [ ] Verify PyInstaller specs work correctly
  - [ ] Test DMG creation on macOS
  - [ ] Test Windows installer
  - [ ] Consider Linux packaging (AppImage/Flatpak)

- [ ] **Distribution channels**
  - [ ] Prepare for PyPI publication
  - [ ] Create Homebrew formula
  - [ ] Update installation docs

## Phase 5: Performance & UX

- [ ] **Performance improvements**
  - [ ] Implement concurrent downloads
  - [ ] Add progress indicators
  - [ ] Optimize memory usage for large PDFs
  - [ ] Cache API responses

- [ ] **User experience**
  - [ ] Improve error messages
  - [ ] Add config file support
  - [ ] Create troubleshooting guide
  - [ ] Add more examples to docs

## Phase 6: Documentation

- [ ] **Code documentation**
  - [ ] Add docstrings to all functions
  - [ ] Generate API documentation
  - [ ] Create developer guide

- [ ] **User documentation**
  - [ ] Update README with new features
  - [ ] Create comprehensive user guide
  - [ ] Add video tutorials
  - [ ] Translate to Polish

## Recently Completed ✅

- [x] Initial project analysis
- [x] Created PLAN.md, TODO.md, CHANGELOG.md
- [x] Removed `app/ppolona.py` 
- [x] Cleaned `app/dmgbuild_settings.py`
- [x] Simplified `pypolona/__main__.py`
- [x] Improved variable naming in `polona.py`
- [x] Enhanced error handling with specific exceptions
- [x] Broke down large `save_downloaded()` method
- [x] Fixed `download_save_textpdf()` return type bug
- [x] Added `.dccache` to `.gitignore`

## Quick Wins (Do Today) 🎯

1. Remove `src/gooey` directory
2. Untrack `.dccache` file  
3. Run code formatter
4. Write first unit test
5. Update version to 1.7.0-dev

## Notes

- Focus on stability over new features for v1.0
- Maintain backward compatibility with existing CLI
- Test thoroughly on all platforms before release
- Keep user experience consistent during refactoring