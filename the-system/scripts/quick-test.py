# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Quick Test Runner

Runs all tests in tests/passing/ and tests/failing/ (sorted by filename)
and reports which passed and which failed. Does NOT build first.

Usage:
    ./the-system/scripts/quick-test.py
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import subprocess
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
# Path to uv.exe in the-system/bin/
SCRIPT_DIR = Path(__file__).parent
UV_PATH = SCRIPT_DIR.parent / 'bin' / 'uv.exe'

def run_cleanup():
    """Run the cleanup script before testing."""
    cleanup_script = Path('./the-system/scripts/cleanup.py')
    if not cleanup_script.exists():
        print(f"Warning: Cleanup script not found at {cleanup_script}")
        return

    print("Running cleanup...")
    try:
        result = subprocess.run(
            [str(UV_PATH), 'run', '--script', str(cleanup_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"Warning: Cleanup exited with code {result.returncode}")
    except Exception as e:
        print(f"Warning: Cleanup failed: {e}")
    print()

def find_tests() -> List[Path]:
    """Find all test files in tests/passing/ and tests/failing/, sorted by filename stem."""
    tests = []

    passing_dir = Path('./tests/passing')
    failing_dir = Path('./tests/failing')

    if passing_dir.exists():
        tests.extend(passing_dir.glob('*.py'))

    if failing_dir.exists():
        tests.extend(failing_dir.glob('*.py'))

    # Sort by filename stem (not including directory)
    tests.sort(key=lambda p: p.stem)

    return tests

def write_test_report(test_path: Path, passed: bool, output: str, location: str):
    """Write a report for a test run to ./reports/ with timestamp prefix."""
    # Create reports directory if it doesn't exist
    reports_dir = Path('./reports')
    reports_dir.mkdir(exist_ok=True)

    # Generate timestamp in same format as prompt-ai.py (millisecond precision)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]

    # Create report filename: {timestamp}_{test_stem}_{PASS|FAIL}.md
    status = "PASS" if passed else "FAIL"
    report_filename = f"{timestamp}_{test_path.stem}_{status}.md"
    report_path = reports_dir / report_filename

    # Build report content
    report_content = f"""# Test Report: {test_path.name}
**Timestamp:** {timestamp}
**Status:** {status}
**Location:** tests/{location}/
**Test File:** {test_path}

---

## Output

```
{output}
```

---

**Result:** {"✓ PASS" if passed else "✗ FAIL"}
"""

    # Write report
    report_path.write_text(report_content, encoding='utf-8')

def is_code_review_test(test_path: Path) -> bool:
    """Check if test is a code-review test that calls prompt-ai.

    Code-review tests need longer timeouts (3600s) because they call AI.
    Regular tests that test ./released/ artifacts use shorter timeouts (180s).
    """
    try:
        content = test_path.read_text(encoding='utf-8')
        # Check for references to prompt-ai or code-inspection-assertion scripts
        return ('prompt-ai.py' in content or
                'prompt_agentic_coder' in content or
                'code-inspection-assertion.py' in content)
    except Exception:
        # If we can't read the file, assume regular test
        return False

def run_test(test_path: Path) -> Tuple[bool, str]:
    """
    Run a single test and return (passed, output).

    Returns:
        (True, output) if test passed (exit code 0)
        (False, output) if test failed (non-zero exit code)
    """
    # Auto-detect timeout based on test type
    if is_code_review_test(test_path):
        timeout = 3600  # 1 hour for code-review tests (call AI)
    else:
        timeout = 180   # 3 minutes for regular tests (test ./released/)

    try:
        result = subprocess.run(
            [str(UV_PATH), 'run', '--script', str(test_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        passed = (result.returncode == 0)
        output = result.stdout + result.stderr
        return passed, output
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT ({timeout}s)"
    except Exception as e:
        return False, f"ERROR: {e}"

def main():
    # Run cleanup first
    run_cleanup()

    tests = find_tests()

    if not tests:
        print("No tests found in tests/passing/ or tests/failing/")
        return 1

    print(f"Running {len(tests)} tests...\n")

    passed_tests = []
    failed_tests = []

    for test_path in tests:
        # Determine which directory the test is in
        if 'passing' in test_path.parts:
            location = "passing"
        else:
            location = "failing"

        print(f"Running {test_path.name} ({location})... ", end='', flush=True)

        passed, output = run_test(test_path)

        # Write report for this test
        write_test_report(test_path, passed, output, location)

        if passed:
            print("✓ PASS")
            passed_tests.append((test_path, location))
        else:
            print("✗ FAIL")
            failed_tests.append((test_path, location, output))

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if passed_tests:
        print(f"\n✓ PASSED ({len(passed_tests)}):")
        for test_path, location in passed_tests:
            print(f"  {test_path.name} ({location})")

    if failed_tests:
        print(f"\n✗ FAILED ({len(failed_tests)}):")
        for test_path, location, output in failed_tests:
            print(f"  {test_path.name} ({location})")

    print(f"\nTotal: {len(passed_tests)} passed, {len(failed_tests)} failed")

    # Exit with 0 if all passed, 1 if any failed
    return 0 if len(failed_tests) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
