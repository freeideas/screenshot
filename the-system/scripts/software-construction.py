# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Software Construction System

This script orchestrates the complete software construction process:
- Phase 1 (P0-P1): Requirements Generation (req-gen.py)
- Phase 2 (P2): Code Generation (VIBE_CODE.md prompt)
- Phase 3 (P3): Test Preparation
- Phase 4 (P4): Test Generation and Verification (test-gen.py in loop)
- Phase 5 (P5): Completion and Summary

Exit codes:
  0 - Success (all phases complete)
  1 - Error
  98 - Test generation stuck (from test-gen)
  99 - External dependency failure (from test-gen)
"""

import sys
import argparse
# Fix Windows console encoding for Unicode characters
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


build_req_index = import_script('build-req-index')
find_orphan_reqIDs = import_script('find-orphan-reqIDs')
prompt_ai = import_script('prompt-ai')


def print_section(title: str):
    """Print section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print()


def run_ai_prompt(prompt_path: Path, report_type: str, timeout=600, model=None, extra_context: str | None = None):
    """Run AI prompt and return result."""
    print(f"  Running prompt: {prompt_path.name}")
    prompt_text = Path(prompt_path).read_text(encoding='utf-8')

    if extra_context:
        prompt_text = f"{prompt_text.rstrip()}\n\n---\n\n## Context\n\n{extra_context.strip()}\n"

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


def kill_orphan_processes():
    """
    Kill any orphaned processes running executables from ./released/

    This is a safety net for tests that fail to cleanup properly.
    Prevents DLL/file locking issues on Windows.

    Tests should use atexit.register() to cleanup their own processes,
    but this catches cases where they don't.
    """
    released_dir = Path('./released')
    if not released_dir.exists():
        print("  No ./released/ directory; skipping orphan process cleanup")
        return

    print("  Checking for orphaned processes from ./released/...")

    try:
        killed_any = False

        if platform.system() == 'Windows':
            # Find all .exe files in released/
            executables = [f.name for f in released_dir.rglob('*.exe')]

            for exe_name in executables:
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', exe_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    print(f"  OK Killed orphaned {exe_name} processes")
                    killed_any = True
                # Silently ignore "not found" errors

            if killed_any:
                # Give Windows time to released file handles
                time.sleep(1)
            else:
                print("  OK No orphaned processes found")

        else:
            # On Unix-like systems, find executable files
            executables = []
            for f in released_dir.rglob('*'):
                if f.is_file() and os.access(f, os.X_OK):
                    executables.append(f.name)

            for exe_name in executables:
                result = subprocess.run(
                    ['pkill', '-9', '-f', exe_name],
                    capture_output=True,
                    timeout=5
                )

                if result.returncode == 0:
                    print(f"  OK Killed orphaned {exe_name} processes")
                    killed_any = True
                # pkill returns 1 when no processes found -- silently ignore

            if killed_any:
                time.sleep(0.5)
            else:
                print("  OK No orphaned processes found")

    except subprocess.TimeoutExpired:
        print("  Warning: Process cleanup timed out", file=sys.stderr)
    except FileNotFoundError:
        print("  Warning: Process cleanup tool not found (taskkill/pkill)", file=sys.stderr)
    except Exception as e:
        print(f"  Warning: Process cleanup failed: {e}", file=sys.stderr)


def run_build_script() -> int:
    """
    Run build.py via subprocess.

    Returns exit code from build.
    """
    build_script = Path('./code/build.py')
    if not build_script.exists():
        print(f"ERROR: {build_script} does not exist", file=sys.stderr)
        return 1

    result = run_script(build_script, timeout=600, stream=True)
    return result['exit_code']


def run_test_file(test_file_path: Path, no_build: bool = False) -> int:
    """
    Run a test file via subprocess.

    test.py handles its own timeout detection and report writing.
    We use a large wrapper timeout to ensure test.py's internal timeout fires first.

    Returns exit code from test.
    """
    test_script = SCRIPT_DIR / 'test.py'
    args = [str(test_file_path)]
    if no_build:
        args.append('--no-build')

    # Large wrapper timeout - test.py will timeout internally first (180s or 3600s)
    result = run_script(test_script, args=args, timeout=3600, stream=True)

    return result['exit_code']


# ============================================================================
# PHASE 2: CODE GENERATION
# ============================================================================

def phase_2_code_generation() -> bool:
    """P2: Generate implementation code from documentation."""
    print_section("PHASE 2: CODE GENERATION")

    # P2.1: Download/setup compiler if needed
    print("P2.1: AI checking/downloading compiler...")
    download_compiler_prompt = SCRIPT_DIR.parent / 'prompts' / 'DOWNLOAD_COMPILER.md'
    if not download_compiler_prompt.exists():
        print(f"  Error: Prompt not found: {download_compiler_prompt}", file=sys.stderr)
        return False

    try:
        run_ai_prompt(download_compiler_prompt, report_type='download_compiler', timeout=1200)
        print("  OK Compiler ready")
        print()
    except Exception as e:
        print(f"  Error checking/downloading compiler: {e}", file=sys.stderr)
        return False

    # P2.2: Generate code
    print("P2.2: AI generating code from README/specs...")
    prompt_path = SCRIPT_DIR.parent / 'prompts' / 'VIBE_CODE.md'
    if not prompt_path.exists():
        print(f"  Error: Prompt not found: {prompt_path}", file=sys.stderr)
        return False

    Path('./code').mkdir(exist_ok=True)

    try:
        run_ai_prompt(prompt_path, report_type='vibe_code', timeout=3600)
        print("  OK AI generated code")
        print()
    except Exception as e:
        print(f"  Error generating code: {e}", file=sys.stderr)
        return False

    return True


# ============================================================================
# PHASE 3: TEST PREPARATION
# ============================================================================

def phase_3_test_preparation(skip_reqs: bool = False, skip_test_staging: bool = False) -> bool:
    """P3: Prepare test directories and clean up orphans."""
    print_section("PHASE 3: TEST PREPARATION")

    # P3.1: Prepare test directories
    print("P3.1: Preparing test directories...")
    for directory in ['./tests/failing', './tests/passing']:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  OK Directory ready: {directory}")
    print()

    # P3.2: Remove orphan $REQ_IDs
    if skip_reqs:
        print("P3.2: Skipping orphan $REQ_ID checks (per --skip-reqs)")
        print()
    else:
        print("P3.2: Checking for orphan $REQ_IDs...")
        print("  Building requirements index...")
        try:
            build_req_index.main()
        except SystemExit:
            pass

        print("  Finding orphan $REQ_IDs...")
        orphans = find_orphan_reqIDs.find_orphans()
        if orphans:
            print(f"  Found {len(orphans)} orphan $REQ_IDs, running REMOVE_ORPHAN_REQS prompt...")
            orphan_lines = ["Orphan $REQ_IDs to remove:"]
            for req_id in sorted(orphans.keys()):
                orphan_lines.append(f"  {req_id}:")
                for filespec, line_num, category in orphans[req_id]:
                    orphan_lines.append(f"    - {filespec}:{line_num} ({category})")
            orphan_summary = "\n".join(orphan_lines)
            print(orphan_summary)
            prompt_path = SCRIPT_DIR.parent / 'prompts' / 'REMOVE_ORPHAN_REQS.md'
            if prompt_path.exists():
                try:
                    run_ai_prompt(
                        prompt_path,
                        report_type='remove_orphan_reqs',
                        timeout=600,
                        extra_context=orphan_summary
                    )
                    print("  OK AI removed orphan $REQ_IDs")
                except Exception as e:
                    print(f"  Warning: Error removing orphans: {e}", file=sys.stderr)
            else:
                print(f"  Warning: Prompt not found: {prompt_path}")
                print("  Skipping orphan removal")
        else:
            print("  OK No orphan $REQ_IDs found")
        print()

    # P3.3: Stage tests for re-verification (unless explicitly skipped)
    if skip_test_staging:
        print("P3.3: Skipping test staging (per --skip-to-testing)")
        print()
    else:
        print("P3.3: Staging tests for re-verification...")
        req_stems = {p.stem for p in Path('./reqs').glob('*.md')}
        passing_dir = Path('./tests/passing')
        failing_dir = Path('./tests/failing')

        def req_stem_for_test(path: Path) -> str:
            return path.stem.replace('test_', '', 1) if path.stem.startswith('test_') else path.stem

        if passing_dir.exists():
            for test_file in list(passing_dir.glob('*.py')):
                stem = req_stem_for_test(test_file)
                if stem in req_stems:
                    shutil.move(str(test_file), str(failing_dir / test_file.name))
                    print(f"  Staged for re-verification: {test_file.name}")
                else:
                    test_file.unlink()
                    print(f"  Deleted orphan test (no matching req): {test_file.name}")

        if failing_dir.exists():
            for test_file in list(failing_dir.glob('*.py')):
                stem = req_stem_for_test(test_file)
                if stem not in req_stems:
                    test_file.unlink()
                    print(f"  Deleted orphan test (no matching req): {test_file.name}")

        print("  OK Tests prepared")
        print()

    # P3.4: Kill orphan processes before starting tests
    kill_orphan_processes()
    print()

    return True


# ============================================================================
# PHASE 4: TEST GENERATION (OUTER LOOP)
# ============================================================================

def phase_4_test_generation_loop() -> int:
    """
    P4: Run test-gen.py in a loop with integration recheck.

    Returns:
        0 - Success
        1 - Error
        98 - Stuck
        99 - External dependency failure
    """
    print_section("PHASE 4: TEST GENERATION AND VERIFICATION")

    while True:
        # Run test-gen.py for per-requirement test generation
        test_gen_script = SCRIPT_DIR / 'test-gen.py'
        result = run_script(test_gen_script, timeout=18000, stream=True)  # 5 hours

        if result['exit_code'] != 0:
            return result['exit_code']

        # P4.7: Integration recheck
        integration_exit = run_integration_recheck()

        if integration_exit == 0:
            break  # All tests pass together

        if integration_exit == 99:
            print("BLOCKED Integration recheck external dependency failure")
            return 99

        # Some tests failed, reset and retry
        print("RETRY Integration recheck failed; resetting tests to failing and restarting Phase 4")
        reset_tests_to_failing()

    return 0


def run_integration_recheck() -> int:
    """
    P4.7: Run all tests in ./tests/passing/ on the same build.

    Returns:
        0 - All tests pass
        1 - Some tests failed
        99 - External dependency failure
    """
    print_section("INTEGRATION RECHECK: ALL PASSING TESTS")

    passing_dir = Path('./tests/passing')
    test_files = sorted(passing_dir.glob('test_*.py')) if passing_dir.exists() else []

    if not test_files:
        print("  No tests in ./tests/passing/ to re-run")
        return 0

    # Build once
    print("Building once for integration recheck...")
    build_returncode = run_build_script()

    if build_returncode != 0:
        print(f"Build failed for integration recheck (exit {build_returncode})")
        return build_returncode

    # Run all tests without rebuilding
    any_failed = False
    for test_file in test_files:
        print(f"Re-running: {test_file.name}")
        code = run_test_file(test_file, no_build=True)

        if code == 99:
            print("EXTERNAL DEPENDENCY FAILURE DURING INTEGRATION RECHECK")
            return 99

        if code != 0:
            print(f"  X Failed: {test_file.name} (exit {code})")
            any_failed = True
        else:
            print(f"  OK Passed: {test_file.name}")

    if any_failed:
        print("One or more passing tests failed during integration recheck.")
        return 1

    print("OK All passing tests still pass together on the same build.")
    return 0


def reset_tests_to_failing():
    """Move all tests from passing back to failing."""
    passing_dir = Path('./tests/passing')
    failing_dir = Path('./tests/failing')
    failing_dir.mkdir(parents=True, exist_ok=True)

    moved = 0
    if passing_dir.exists():
        for test_file in list(passing_dir.glob('test_*.py')):
            shutil.move(str(test_file), str(failing_dir / test_file.name))
            moved += 1

    print(f"Moved {moved} tests back to ./tests/failing/.")


# ============================================================================
# PHASE 5: COMPLETION
# ============================================================================

def phase_5_completion() -> bool:
    """P5: Verify completion and generate summary."""
    print_section("PHASE 5: COMPLETION")

    # P5.1: Verify all tests passing
    print("P5.1: Verifying all tests passing...")
    failing_tests = list(Path('./tests/failing').glob('test_*.py'))

    if failing_tests:
        print(f"  Error: {len(failing_tests)} tests still failing:", file=sys.stderr)
        for test_file in failing_tests:
            print(f"    - {test_file.name}", file=sys.stderr)
        return False

    print("  OK All tests moved to ./tests/passing/")
    print()

    # P5.2: Generate summary
    print("P5.2: Generating summary...")

    db_path = './tmp/reqs.sqlite'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM req_definitions")
        num_reqs = cursor.fetchone()[0]
        conn.close()
    else:
        num_reqs = 0

    passing_tests = list(Path('./tests/passing').glob('test_*.py'))
    num_tests = len(passing_tests)

    released_dir = Path('./released')
    if released_dir.exists():
        artifacts = sorted([f for f in released_dir.rglob('*') if f.is_file()])
    else:
        artifacts = []

    print()
    print("=" * 70)
    print("BUILD SUMMARY")
    print("=" * 70)
    print(f"Requirements defined: {num_reqs}")
    print(f"Tests passing: {num_tests}")
    print(f"Artifacts in ./released/: {len(artifacts)}")

    if artifacts:
        print()
        print("Artifacts:")
        for artifact in artifacts:
            rel_path = artifact.relative_to(released_dir)
            size = artifact.stat().st_size
            print(f"  - {rel_path} ({size:,} bytes)")

    print("=" * 70)
    print()

    return True


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Software Construction System")
    parser.add_argument(
        '--skip-reqs',
        action='store_true',
        help='Skip requirement generation and any edits to ./reqs/ documents (use existing reqs instead).'
    )
    parser.add_argument(
        '--skip-to-testing',
        action='store_true',
        help='Skip directly to test generation/verification loop (skip requirements, code generation, and test staging).'
    )
    args = parser.parse_args()

    skip_reqs_phase = args.skip_reqs or args.skip_to_testing
    skip_code_generation = args.skip_to_testing
    skip_test_staging = args.skip_to_testing
    skip_reqs_reason = '--skip-to-testing' if args.skip_to_testing else '--skip-reqs'

    print()
    print("=" * 70)
    print("SOFTWARE CONSTRUCTION SYSTEM")
    print("=" * 70)
    print()
    print("This will run the complete build process:")
    if skip_reqs_phase:
        print(f"  - Phase 1: Requirements Generation (skipped via {skip_reqs_reason})")
    else:
        print("  - Phase 1: Requirements Generation (P0-P1)")
    if skip_code_generation:
        print("  - Phase 2: Code Generation (skipped via --skip-to-testing)")
    else:
        print("  - Phase 2: Code Generation (P2)")
    print("  - Phase 3: Test Preparation (P3)")
    print("  - Phase 4: Test Generation and Verification (P4)")
    print("  - Phase 5: Completion and Summary (P5)")
    print()

    # Change to project root (two levels up from this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)
    print(f"Working directory: {Path.cwd()}")
    print()

    # Add the-system/bin to PATH
    bin_dir = SCRIPT_DIR.parent / 'bin'
    if bin_dir.exists():
        os.environ['PATH'] = str(bin_dir) + os.pathsep + os.environ.get('PATH', '')
        print(f"Added to PATH: {bin_dir}")
        print()

    # Copy global CLAUDE.md to project root
    global_claude_md = SCRIPT_DIR.parent / 'prompts' / 'global_CLAUDE.md'
    if global_claude_md.exists():
        shutil.copy(global_claude_md, './CLAUDE.md')
        print(f"Copied {global_claude_md.name} to ./CLAUDE.md")
        print()

    # Cleanup temporary directories
    cleanup_script = SCRIPT_DIR / 'cleanup.py'
    result = run_script(cleanup_script, stream=True)
    if not result['success']:
        print(f"Warning: Cleanup failed (exit {result['exit_code']})", file=sys.stderr)
        print()

    # Phase 1: Requirements Generation
    if skip_reqs_phase:
        print("=" * 70)
        print(f"SKIP PHASE 1: REQUIREMENTS GENERATION ({skip_reqs_reason})")
        print("=" * 70)
        print()
        print("Using existing ./reqs/ documents; no edits will be made to requirements.")
        print()
    else:
        print("=" * 70)
        print("STARTING PHASE 1: REQUIREMENTS GENERATION")
        print("=" * 70)
        print()

        req_gen_script = SCRIPT_DIR / 'req-gen.py'
        result = run_script(req_gen_script, timeout=10800, stream=True)  # 3 hours

        if result['exit_code'] != 0:
            if result['exit_code'] == 124:
                # Timeout - but may have generated some requirements, continue anyway
                print()
                print("=" * 70)
                print("WARNING  PHASE 1 TIMED OUT (continuing with partial requirements)")
                print("=" * 70)
                print()
            else:
                # Real failure or user abort
                print()
                print("=" * 70)
                print("FAIL PHASE 1 FAILED OR ABORTED")
                print("=" * 70)
                print()
                return result['exit_code']

    # Phase 2: Code Generation
    if skip_code_generation:
        print("=" * 70)
        print("SKIP PHASE 2: CODE GENERATION (--skip-to-testing)")
        print("=" * 70)
        print()
        print("Using existing code in ./code/; no regeneration performed.")
        print()
    else:
        if not phase_2_code_generation():
            print()
            print("FAIL Phase 2 failed")
            return 1

    # Phase 3: Test Preparation
    if not phase_3_test_preparation(skip_reqs=skip_reqs_phase, skip_test_staging=skip_test_staging):
        print()
        print("FAIL Phase 3 failed")
        return 1

    # Phase 4: Test Generation Loop
    exit_code = phase_4_test_generation_loop()

    if exit_code != 0:
        print()
        print("=" * 70)
        if exit_code == 98:
            print("RETRY PHASE 4 STUCK (TEST GENERATION)")
            print("=" * 70)
            print()
            print("Review ./reports/ and fix requirements manually, then re-run")
        elif exit_code == 99:
            print("BLOCKED PHASE 4 EXTERNAL DEPENDENCY FAILURE")
            print("=" * 70)
            print()
            print("Fix external dependency and re-run")
        else:
            print("FAIL PHASE 4 FAILED")
            print("=" * 70)
        print()
        return exit_code

    # Phase 5: Completion
    if not phase_5_completion():
        print()
        print("FAIL Phase 5 failed")
        return 1

    # Success
    print()
    print("=" * 70)
    print("OK SOFTWARE CONSTRUCTION COMPLETE")
    print("=" * 70)
    print()
    print("All phases completed successfully!")
    print("Your working software is in the ./released/ directory")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
