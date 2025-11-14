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
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
from pathlib import Path

def main():
    release_dir = Path('./release')

    # List what's actually in ./release/
    actual_files = set()
    if release_dir.exists():
        for item in release_dir.iterdir():
            if item.is_file():
                actual_files.add(item.name)

    # Define expected files based on documentation
    #
    # From README.md line 84: "AOT compiled with no runtime dependencies required"
    # From TESTING.md line 5: "Testing for `screenshot.exe` uses direct invocation of `./release/screenshot.exe`"
    # From TESTING.md line 83: "Build Artifacts -- Validates that `./release/screenshot.exe` is built correctly"
    #
    # The documentation specifies a single standalone executable with NO runtime dependencies.
    expected_files = {
        'screenshot.exe',
    }

    # Check for missing files
    missing = expected_files - actual_files
    if missing:
        print(f"ERROR: Missing files in ./release/:", flush=True)
        for f in sorted(missing):
            print(f"  - {f}", flush=True)
        print("", flush=True)
        print("Expected a single standalone executable with no runtime dependencies.", flush=True)
        print("See README.md line 84 and ./readme/TESTING.md", flush=True)
        return 1

    # Check for unexpected files
    unexpected = actual_files - expected_files
    if unexpected:
        print(f"ERROR: Unexpected files in ./release/:", flush=True)
        for f in sorted(unexpected):
            print(f"  - {f}", flush=True)
        print("", flush=True)
        print("Documentation specifies a single standalone executable with NO runtime dependencies.", flush=True)
        print("See README.md line 84: 'AOT compiled with no runtime dependencies required'", flush=True)
        print("See ./readme/TESTING.md line 5 and line 83", flush=True)
        return 1

    print("✓ Build artifacts validation: PASS", flush=True)
    print(f"  Found: {', '.join(sorted(actual_files))}", flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
