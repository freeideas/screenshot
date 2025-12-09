# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Test Generation and Verification Loop (P4)

Per-requirement test generation: for each requirement, generate/fix test until it passes.
Follows the workflow defined in ../02_CODE-GEN.md (Phase 4)

Exit codes:
  0 - Success (all tests passing)
  1 - Error
  98 - Test generation stuck (>5 attempts on one requirement)
  99 - External dependency failure
"""

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import shutil
import sqlite3
import subprocess
import platform
import time
import importlib.util
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent

# Import run-script utility
_run_script_spec = importlib.util.spec_from_file_location("run_script", SCRIPT_DIR / "run-script.py")
run_script_module = importlib.util.module_from_spec(_run_script_spec)
_run_script_spec.loader.exec_module(run_script_module)
run_script = run_script_module.run_script

# Import helper scripts
def import_script(script_name: str):
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


compute_signature = import_script('compute-signature')
build_req_index = import_script('build-req-index')
prompt_ai = import_script('prompt-ai')


def kill_orphan_processes():
    """
    Kill any orphaned processes running executables from ./released/

    This prevents file locking issues on Windows during builds.
    """
    released_dir = Path('./released')
    if not released_dir.exists():
        return

    try:
        if platform.system() == 'Windows':
            executables = [f.name for f in released_dir.rglob('*.exe')]
            for exe_name in executables:
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', exe_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"  Killed orphaned {exe_name} processes")
            time.sleep(1)  # Give Windows time to released file handles
        else:
            executables = []
            for f in released_dir.rglob('*'):
                if f.is_file() and os.access(f, os.X_OK):
                    executables.append(f.name)
            for exe_name in executables:
                subprocess.run(['pkill', '-9', '-f', exe_name], capture_output=True, timeout=5)
            time.sleep(0.5)
    except Exception:
        pass  # Silently ignore cleanup failures


def take_signature(paths):
    """Compute signature of files."""
    return compute_signature.compute_signature(paths)


def run_ai_prompt(prompt_path: Path, report_type: str, timeout=600, model=None, template_vars=None):
    """Run AI prompt and return result."""
    print(f"  Running prompt: {prompt_path.name}")
    prompt_text = Path(prompt_path).read_text(encoding='utf-8')

    if template_vars:
        for placeholder, value in template_vars.items():
            prompt_text = prompt_text.replace(placeholder, value)

    agent = os.environ.get('PROMPT_AGENTIC_AGENT', 'claude')
    if model is None:
        model = os.environ.get('PROMPT_AGENTIC_MODEL', 'sonnet')
    os.environ['PROMPT_AGENTIC_MODEL'] = model

    return prompt_ai.get_ai_response_text(
        prompt_text,
        report_type=report_type,
        timeout=timeout,
        agent=agent
    )


def write_decision_report(req_file: Path, test_file_path: Path, attempt: int, decision: str, details: dict = None):
    """
    Write a simple decision report explaining what action we're taking and why.

    Args:
        req_file: Requirement file being processed
        test_file_path: Test file path
        attempt: Current attempt number
        decision: The decision/action being taken
        details: Additional context
    """
    Path('./reports').mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]
    req_name = req_file.stem
    test_name = test_file_path.stem

    # Extract action type from decision for filename
    action_map = {
        "test_missing": "creating_test",
        "test_failed": "fixing_test",
        "build_failed": "build_failed",
        "missing_coverage": "adding_coverage",
        "verifying_quality": "verifying_quality",
        "test_passed": "test_passed",
        "retrying": "retrying"
    }
    action = action_map.get(decision, "decision")
    report_path = Path('./reports') / f"{timestamp}_{action}_{req_name}_attempt{attempt}.md"

    details = details or {}

    # Build simple, clear report
    report_content = f"""# {req_name} -- Attempt {attempt}/5

**Test:** `{test_name}.py`
**Timestamp:** {timestamp}

---

"""

    if decision == "test_missing":
        report_content += """## Decision: Creating Test

Test file does not exist yet. Asking AI to create initial test from requirements.

**Next Step:** Run TEST-FIX_LOOP to generate test
"""

    elif decision == "test_failed":
        exit_code = details.get('exit_code', 'unknown')
        report_content += f"""## Decision: Fixing Test

Test failed with exit code {exit_code}. Asking AI to fix either the test or the code.

**Next Step:** Run TEST-FIX_LOOP to fix failures
"""

    elif decision == "build_failed":
        exit_code = details.get('exit_code', 97)
        report_content += f"""## Decision: Build Failed

Build failed with exit code {exit_code}. Cannot run test until build succeeds.

**Next Step:** Run TEST-FIX_LOOP to fix build issues

**Common build failures:**
- Missing dependency DLLs from sister projects
- File locking (orphaned processes holding files)
- Incorrect paths in build script
- Compilation errors in source code

Check ./reports/ for test.py report with BUILD_FAILED status showing build output.
"""

    elif decision == "missing_coverage":
        missing = details.get('missing_ids', [])
        report_content += f"""## Decision: Adding Coverage

Test exists but doesn't cover all requirements.

**Missing Requirements:** {', '.join(missing)}

**Next Step:** Run TEST-FIX_LOOP to add missing requirement coverage
"""

    elif decision == "verifying_quality":
        report_content += """## Decision: Verifying Quality

Test passed. Now asking AI to verify the test faithfully tests all requirements.

**Next Step:** Run VERIFY_TEST to check test quality
"""

    elif decision == "test_passed":
        report_content += """## Decision: Test Complete

Test passed and quality verification confirmed it faithfully tests requirements.

**Next Step:** Move test to passing/ directory
"""

    elif decision == "retrying":
        reason = details.get('reason', 'unknown')
        report_content += f"""## Decision: Retrying

Quality verification modified the test. Restarting verification loop.

**Reason:** {reason}

**Next Step:** Re-verify test from step (A)
"""

    else:
        report_content += f"""## Decision: {decision}

{details}
"""

    report_path.write_text(report_content, encoding='utf-8')
    print(f"  Decision: {report_path.name}")


def run_test_file(test_file_path: Path, no_build: bool = False) -> int:
    """
    Run a test file via subprocess.

    test.py handles its own timeout detection and report writing.
    We use a large wrapper timeout (3600s) to ensure test.py's internal timeout fires first.

    Returns exit code from test.
    """
    test_script = SCRIPT_DIR / 'test.py'
    args = [str(test_file_path)]
    if no_build:
        args.append('--no-build')

    # Large wrapper timeout - test.py will timeout internally first (180s or 3600s)
    result = run_script(test_script, args=args, timeout=3600, stream=True)

    return result['exit_code']


def verify_all_req_ids_in_test(req_file_path: Path, test_file_path: Path):
    """Check if all $REQ_IDs from requirement file are present in test."""
    db_path = './tmp/reqs.sqlite'
    if not os.path.exists(db_path):
        print(f"  Warning: Database not found at {db_path}", file=sys.stderr)
        return (False, [])

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT req_id FROM req_definitions WHERE flow_file = ? ORDER BY req_id", (str(req_file_path),))
    required = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT req_id FROM req_locations WHERE filespec = ? AND category = 'tests' ORDER BY req_id", (str(test_file_path),))
    found = [r[0] for r in cur.fetchall()]
    conn.close()

    missing = [rid for rid in required if rid not in found]
    return (len(missing) == 0, missing)


def verify_test_quality(req_file: Path, test_file_path: Path, test_file_name: str, attempt: int) -> bool:
    """
    P4.5 (D): Verify test quality.

    Returns:
        True - Test is good, move to passing
        False - Test was modified, retry
    """
    print("  (D) Verifying test quality...")

    passing_path = Path('./tests/passing') / test_file_name
    sig_before = take_signature([str(test_file_path)])
    prompt_path = SCRIPT_DIR.parent / 'prompts' / 'VERIFY_TEST.md'

    if prompt_path.exists():
        try:
            run_ai_prompt(
                prompt_path,
                report_type=f'verify_test_{req_file.stem}_attempt{attempt}',
                timeout=600,
                template_vars={
                    '{{REQ_FILE_PATH}}': str(req_file),
                    '{{TEST_FILE_PATH}}': str(test_file_path)
                }
            )

            # Check if AI moved test to passing/ and move it back
            move_test_from_passing_to_failing(test_file_path, passing_path)

            sig_after = take_signature([str(test_file_path)])

            if sig_before != sig_after:
                print("    X Test modified by verification; retrying from P4.2 (A)...")
                write_decision_report(req_file, test_file_path, attempt, "retrying",
                                     {'reason': 'Quality verification modified the test'})
                return False
            else:
                print("    OK Test quality verified")
                write_decision_report(req_file, test_file_path, attempt, "test_passed")

        except Exception as e:
            print(f"    Warning: Error verifying test: {e}")
            print("    Continuing anyway...")

    # P4.6 (E): Move to passing
    if passing_path.exists():
        passing_path.unlink()
    shutil.move(str(test_file_path), str(passing_path))
    print("    OK Moved to ./tests/passing/")
    print()

    return True


def move_test_from_passing_to_failing(test_file_path: Path, passing_test_path: Path) -> bool:
    """
    Check if AI moved test to passing/ and move it back to failing/.

    Returns True if test was moved, False otherwise.
    """
    if passing_test_path.exists():
        print(f"    ! AI moved test to passing/, moving back to failing/ for verification...")
        if test_file_path.exists():
            test_file_path.unlink()
        shutil.move(str(passing_test_path), str(test_file_path))
        print(f"    OK Moved back to failing/")
        return True
    return False


def phase_4_per_requirement_testing() -> int:
    """
    P4: For each requirement, generate/fix test until it passes.

    Returns:
        0 - Success
        1 - Error
        98 - Stuck (>5 attempts)
        99 - External dependency failure
    """
    req_files = sorted(Path('./reqs').glob('*.md'))
    if not req_files:
        print("  Error: No requirement files found in ./reqs/", file=sys.stderr)
        return 1

    print(f"Processing {len(req_files)} requirement files...")
    print()

    for req_file in req_files:
        print(f"Processing: {req_file.name}")
        print("-" * 70)

        test_file_name = f"test_{req_file.stem}.py"
        test_file_path = Path('./tests/failing') / test_file_name
        passing_test_path = Path('./tests/passing') / test_file_name

        # If test is in passing/ directory, move it to failing/ for re-verification
        # (AI sometimes puts tests directly in passing/ during TEST-FIX_LOOP)
        # Clobber any existing failing version -- passing version is newer/better
        if passing_test_path.exists():
            print(f"  Found test in passing/ directory, moving to failing/ for re-verification...")
            if test_file_path.exists():
                test_file_path.unlink()
            shutil.move(str(passing_test_path), str(test_file_path))
            print(f"    OK Moved to failing/")

        # Attempt loop: try up to 5 times
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            print(f"  Attempt {attempt}/{max_attempts}")

            # Check if AI moved test to passing/ in previous attempt and move it back
            move_test_from_passing_to_failing(test_file_path, passing_test_path)

            # P4.2 (A): If test exists, check if it passes
            if test_file_path.exists():
                print("  (A) Test exists; checking if it passes...")

                # Rebuild requirements index
                try:
                    build_req_index.main()
                except SystemExit:
                    pass

                # Verify all $REQ_IDs present
                all_present, missing_ids = verify_all_req_ids_in_test(req_file, test_file_path)

                if all_present:
                    # Run test
                    exit_code = run_test_file(test_file_path)

                    if exit_code == 99:
                        print("  EXTERNAL DEPENDENCY FAILURE")
                        return 99

                    if exit_code == 97:
                        print("  BUILD FAILED")
                        write_decision_report(req_file, test_file_path, attempt, "build_failed",
                                            {'exit_code': exit_code})
                        # Don't return immediately - let AI try to fix build issues
                        # Fall through to TEST-FIX_LOOP below

                    elif exit_code == 0:
                        print("    OK Existing test passed")
                        # Write decision: test passed, now verifying quality
                        write_decision_report(req_file, test_file_path, attempt, "verifying_quality")
                        # Skip to P4.5 (D) - verify test quality
                        if verify_test_quality(req_file, test_file_path, test_file_name, attempt):
                            break  # Success, move to next requirement
                        else:
                            continue  # Test modified, retry from (A)
                    else:
                        # Test failed (could be timeout 124, failure 1, etc.)
                        # test.py already wrote a report
                        print(f"    X Test failed (exit {exit_code})")
                        write_decision_report(req_file, test_file_path, attempt, "test_failed",
                                                {'exit_code': exit_code})
                else:
                    print(f"    X Test missing $REQ_IDs: {', '.join(missing_ids)}")
                    # Write decision: test missing coverage
                    write_decision_report(req_file, test_file_path, attempt, "missing_coverage",
                                            {'missing_ids': missing_ids})
            else:
                # Test doesn't exist
                print("  Test does not exist yet")
                write_decision_report(req_file, test_file_path, attempt, "test_missing")

            # P4.3 (B): Run TEST-FIX_LOOP
            print("  (B) Running AI test-fix loop...")
            prompt_path = SCRIPT_DIR.parent / 'prompts' / 'TEST-FIX_LOOP.md'
            if not prompt_path.exists():
                print(f"    Error: Prompt not found: {prompt_path}", file=sys.stderr)
                return 1

            try:
                run_ai_prompt(
                    prompt_path,
                    report_type=f'test_fix_loop_{req_file.stem}_attempt{attempt}',
                    timeout=1800,
                    template_vars={
                        '{{REQ_FILE_PATH}}': str(req_file),
                        '{{TEST_FILE_PATH}}': str(test_file_path),
                        '{{ATTEMPT}}': str(attempt)
                    }
                )

                # Rebuild requirements index after AI makes changes
                try:
                    build_req_index.main()
                except SystemExit:
                    pass

                print("    OK AI completed test-fix loop")

                # Kill any orphaned processes AI may have started
                kill_orphan_processes()

            except SystemExit:
                pass
            except Exception as e:
                if 'EXTERNAL_DEPENDENCY_FAILURE' in str(e):
                    print("  EXTERNAL DEPENDENCY FAILURE")
                    return 99
                print(f"    Warning: Error in test-fix loop: {e}", file=sys.stderr)

            # Check if AI moved test to passing/ and move it back
            # (Must happen regardless of exceptions above)
            move_test_from_passing_to_failing(test_file_path, passing_test_path)

            # P4.4 (C): Verify test REALLY passes
            print("  (C) Verifying test actually passes...")
            if not test_file_path.exists():
                print(f"    X Test file does not exist: {test_file_path}")
                print("    Retrying...")
                continue

            exit_code = run_test_file(test_file_path)

            if exit_code == 99:
                print("  EXTERNAL DEPENDENCY FAILURE")
                return 99

            if exit_code == 97:
                print("  BUILD FAILED")
                print("  Retrying...")
                continue

            if exit_code != 0:
                # Test failed (includes timeouts, normal failures, etc.)
                # test.py already wrote a report
                print(f"    X Test failed (exit code: {exit_code})")
                print("    Retrying...")
                continue

            print("    OK Test passed")

            # P4.5 (D): Verify test quality
            if verify_test_quality(req_file, test_file_path, test_file_name, attempt):
                break  # Success, move to next requirement
            else:
                continue  # Test modified, retry from (A)

        # Check if we hit max attempts
        if attempt >= max_attempts and test_file_path.exists():
            print()
            print("=" * 70)
            print("ERROR: Test generation stuck after 5 attempts")
            print("=" * 70)
            print(f"Requirement: {req_file}")
            print(f"Test: {test_file_path}")
            print()
            print("Please review ./reports/ and fix requirements manually")
            return 98

    return 0


def main() -> int:
    """Main entry point."""
    print()
    print("=" * 70)
    print("TEST GENERATION AND VERIFICATION (P4)")
    print("=" * 70)

    project_root = SCRIPT_DIR.parent.parent
    os.chdir(project_root)
    print(f"Working directory: {Path.cwd()}")
    print()

    # Phase 4: Per-Requirement Testing
    exit_code = phase_4_per_requirement_testing()

    if exit_code != 0:
        print()
        if exit_code == 98:
            print("RETRY Phase 4 stuck (test generation)")
        elif exit_code == 99:
            print("BLOCKED Phase 4 external dependency failure")
        else:
            print("FAIL Phase 4 failed")
        return exit_code

    print()
    print("=" * 70)
    print("OK TEST GENERATION AND VERIFICATION COMPLETE")
    print("=" * 70)
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
