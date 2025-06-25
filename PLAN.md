# PyPolona Streamlining Plan (MVP v1.0 Focus)

This document outlines the detailed steps to streamline the PyPolona codebase, focusing on creating a performant and focused Minimum Viable Product (MVP) v1.0.

1.  **Initial Setup & Analysis:**
    *   (Completed) Verified understanding of the project structure and main functionalities by reviewing `llms.txt`.
    *   (Current) Create `PLAN.md` (this file), `TODO.md` (checklist version), and `CHANGELOG.md` (initialized).

2.  **Remove Vendored Gooey (`src/gooey`):**
    *   **Rationale:** The `src/gooey` directory appears to be a local copy of the Gooey library. `ezgooey` is listed as a dependency in `pyproject.toml`, which should provide the necessary GUI functionality, making the vendored copy redundant and a source of maintenance overhead.
    *   **Action:**
        *   Confirm that `ezgooey` is sufficient. This might involve a quick check of `ezgooey`'s capabilities or assuming it wraps/replaces the need for a direct Gooey copy.
        *   Delete the entire `src/gooey` directory from the repository.
        *   If the `src/` directory becomes empty or only contains project-specific code, ensure it's correctly handled by version control (e.g., no empty `src/` directory unless intended).
    *   **Verification:**
        *   Run the application with the GUI (`ppolona` or `pypolona-gui`).
        *   Manually test basic GUI interactions (opening, input fields, starting a task) to ensure no regressions.
        *   The CI pipeline runs `pytest`; if any tests cover GUI aspects that might break, they should indicate issues.

3.  **Simplify `pypolona/__main__.py`:**
    *   **Rationale:** The current `__main__.py` contains commented-out code and a slightly verbose structure for initializing the application.
    *   **Actions:**
        *   Remove the commented-out `webgui` section that uses `Cli2Gui`. This functionality is not active and adds clutter.
        *   Simplify the `main()` function: The `if True:` block is redundant. The logic can be streamlined to directly call `gui(*args, **kwargs)` and then `parser.parse_args()`.
    *   **Verification:**
        *   Run the CLI with various arguments (e.g., `ppolona -h`, `ppolona --search test --download`).
        *   Run the GUI.
        *   Ensure both modes start correctly and parse arguments as expected.

4.  **Refactor `pypolona/polona.py` (Core Logic):**
    *   **Rationale:** This is the largest and most complex file, offering significant opportunities for improving clarity, maintainability, and robustness.
    *   **Sub-tasks:**
        *   **Improve Readability and Reduce Complexity:**
            *   Identify long methods like `save_downloaded()` and `pdf_add_meta()`. If they handle multiple distinct stages, consider breaking them into smaller, private helper methods. For example, `save_downloaded` deals with path creation, YAML saving, image downloading, PDF creation, and text PDF handling.
            *   Rename variables for better clarity (e.g., `r` to `response`, `jhits` to `json_hits`, `hit_data` to `item_data_json`).
            *   Review complex conditional logic or nested loops for potential simplification.
        *   **Error Handling:**
            *   Go through each `try...except Exception as e:` block.
            *   Replace `Exception` with more specific exceptions like `requests.exceptions.RequestException`, `json.JSONDecodeError`, `IOError`/`OSError`, `pikepdf.PdfError`, `TypeError`, `KeyError`, etc., where the type of error can be anticipated. This allows for more granular error handling and reporting.
        *   **Type Hinting:**
            *   Attempt to resolve existing `# type: ignore` comments by providing correct type information or refactoring the code to be more type-friendly.
            *   Replace `Any` with more specific types (e.g., `dict[str, str]`, `list[HitObject]`, custom `TypedDict`s or dataclasses if beneficial for complex structures like `hit`).
        *   **Logging:**
            *   Ensure a consistent logging strategy:
                *   `log.debug()` for detailed information useful for developers.
                *   `log.info()` for user-facing progress messages and successful operations.
                *   `log.warn()` for potential issues or recoverable errors (e.g., skipping an existing file).
                *   `log.error()` for errors that prevent a specific part of the process from completing (e.g., failing to download a single image).
                *   `log.critical()` for errors that prevent the application from continuing meaningfully.
            *   Review log messages: ensure they are informative, include relevant context (like item IDs or file paths), and avoid excessive verbosity at default levels.
        *   **Consolidate Helper Functions:**
            *   Review `_requests_encode_dict()`: `requests` can handle dictionary parameters directly for GET requests using the `params` argument. Check if this custom encoding is strictly necessary for Polona's API or if it can be simplified/removed.
        *   **Resource Management:**
            *   Double-check all file operations (`open()`) use the `with` statement to ensure files are closed properly, even if errors occur. (This seems largely in place but worth a final check).
    *   **Verification:**
        *   This is the most critical part. Extensive manual testing of all core functionalities (search types, download formats, options) will be required.
        *   Pay close attention to edge cases (e.g., no results found, item with no images, API errors).
        *   Run existing `pytest` tests.

5.  **Streamline `app/` Directory:**
    *   **Rationale:** Reduce boilerplate and simplify the application's packaging structure.
    *   **Actions:**
        *   **`app/ppolona.py`:** This script (`#!/usr/bin/env python3\nfrom pypolona.__main__ import *\nmain()`) is likely redundant. The `pyproject.toml` entries for `[project.scripts]` (`ppolona = "pypolona.__main__:main"`) and `[project.gui-scripts]` should allow direct execution. Verify this and remove `app/ppolona.py` if confirmed.
        *   **`app/dmgbuild_settings.py`:** This file contains many comments and example settings from `dmgbuild`. Remove commented-out sections that are not actively used by PyPolona to make the file cleaner and focused on actual configuration.
    *   **Verification:**
        *   If `app/ppolona.py` is removed, ensure the application can still be launched via the defined script/gui-script entry points.
        *   Building the DMG (on macOS) should still work correctly after cleaning `dmgbuild_settings.py`.

6.  **Review and Update Dependencies (`pyproject.toml`):**
    *   **Rationale:** Ensure the project only depends on necessary libraries and that versions are appropriate for an MVP.
    *   **Actions:**
        *   Cross-reference imported libraries in the code against `pyproject.toml` to ensure no unused dependencies are listed.
        *   For the MVP, major dependency updates (e.g., for `pikepdf`, `lxml`) will be deferred unless an existing version has a known critical issue impacting core functionality. The goal is stability for MVP. Log these as potential post-MVP improvements.
        *   Confirm `requests` is present (it is).
    *   **Verification:**
        *   The application should install and run correctly with the specified dependencies.
        *   CI pipeline (which installs dependencies) should pass.

7.  **Handle `.dccache` file:**
    *   **Rationale:** This file appears to be a local cache file (possibly from an IDE or linting tool like `pylint`) that should not be part of the repository.
    *   **Actions:**
        *   Remove `.dccache` from version control using `git rm --cached .dccache` (if tracked) or just delete it if untracked but present.
        *   Add `.dccache` to the `.gitignore` file to prevent it from being accidentally committed in the future.
    *   **Verification:**
        *   `git status` should not show `.dccache` as a tracked or untracked file (after adding to `.gitignore`).

8.  **Testing and Validation:**
    *   **Rationale:** Ensure all changes haven't introduced regressions and the application remains functional.
    *   **Actions:**
        *   **Manual Testing:** Systematically test all core features as outlined in the plan's "Testing and Validation" step. This includes:
            *   Different search modes (URL, simple search, advanced search, IDs).
            *   Download formats (JPEGs in subfolders, single PDF).
            *   Option to download/skip searchable text PDFs.
            *   Key options: `--max-pages`, `--no-overwrite` (formerly `--skip`), language filters, sort orders.
            *   Error conditions: invalid input, network errors (if mockable or by temporarily disconnecting), items with no downloadable content.
        *   **Automated Tests:**
            *   The CI configuration in `.github/workflows/ci.yml` specifies `pytest`. Run these tests locally after major refactoring steps, especially for `polona.py`.
            *   If test coverage is low for core logic, this is a high-priority item for post-MVP improvement. For the MVP, robust manual testing will be key.
    *   **Verification:** All manual tests pass. All existing automated tests pass.

9.  **Update Documentation:**
    *   **Rationale:** Keep user-facing and developer documentation synchronized with the changes.
    *   **Actions:**
        *   **`README.md`:**
            *   Review installation instructions, especially if `app/ppolona.py` is removed or build processes change.
            *   Update any command-line examples or GUI descriptions if features were altered (e.g., `--skip` changed to `--no-overwrite` was already in README, but verify).
            *   Ensure screenshots are still representative if GUI elements changed (unlikely with `ezgooey` abstraction).
        *   **`PLAN.md` (this file) and `TODO.md`:** Mark completed steps.
        *   **`CHANGELOG.md`:** Add entries for all significant changes, bug fixes, and refactorings made during this streamlining process.
    *   **Verification:** Documentation is accurate and reflects the current state of the application.

10. **Final Review and Submission:**
    *   **Rationale:** A final quality check before concluding the task.
    *   **Actions:**
        *   Perform a self-review of all code changes.
        *   Ensure all temporary files or debug statements have been removed.
        *   Ensure the application builds correctly (if applicable to the testing environment).
        *   Create a comprehensive commit message summarizing the streamlining effort.
        *   Submit the changes to the designated branch.
    *   **Verification:** Code is clean, well-formatted, and meets the goals of the MVP streamlining.
---
(This `PLAN.md` will be created in the filesystem)
