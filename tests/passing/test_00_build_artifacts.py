#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Build Artifacts Validation Test

IMPORTANT: Before modifying this test, read:
- ./README.md
- All files in ./readme/

This test validates that ./tests/build.py produces exactly
the artifacts specified in the documentation.

If this test fails, the problem is likely in ./tests/build.py
-- it's not building what the documentation specifies.
The documentation is the source of truth.

To regenerate this test (if documentation changes):
  Run: ./the-system/scripts/software-construction.py
  (This will regenerate the test based on current documentation)
"""

import sys

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        # On older Pythons, reconfigure may not exist; ignore.
        pass

from pathlib import Path


def list_release_files(release_dir: Path) -> set[str]:
    files: set[str] = set()
    if release_dir.exists():
        for item in release_dir.iterdir():
            if item.is_file():
                files.add(item.name)
    return files


def main() -> int:
    release_dir = Path('./release')

    # List what's actually in ./release/
    actual_files = list_release_files(release_dir)

    # Expected files based on documentation (README.md, readme/)
    # The app is a single, standalone AOT-compiled CLI tool with
    # no runtime dependencies. Therefore, we expect only the
    # executable to be shipped in ./release/.
    expected_files = {
        'screenshot.exe',
    }

    errors: list[str] = []

    missing = expected_files - actual_files
    if missing:
        errors.append("Missing files in ./release/:")
        for f in sorted(missing):
            errors.append(f"  - {f}")

    unexpected = actual_files - expected_files
    if unexpected:
        errors.append("Unexpected files in ./release/:")
        for f in sorted(unexpected):
            errors.append(f"  - {f}")

    if errors:
        print("ERROR: Build artifacts do not match documentation.")
        print()
        print("Documentation (source of truth): ./README.md and ./readme/")
        print("Expected files in ./release/:")
        for f in sorted(expected_files):
            print(f"  - {f}")
        print()
        print("Actual files found in ./release/:")
        for f in sorted(actual_files):
            print(f"  - {f}")
        print()
        print("Details:")
        for line in errors:
            print(line)
        return 1

    print("Build artifacts validation: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(main())

