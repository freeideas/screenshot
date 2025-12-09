# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import subprocess
import argparse
import time
import threading
import platform
from pathlib import Path
from datetime import datetime

# Change to project root (two levels up from this script)
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
os.chdir(project_root)

# Path to uv.exe in the-system/bin/
UV_PATH = script_dir.parent / 'bin' / 'uv.exe'

# Create reports directory
reports_dir = Path('./reports')
reports_dir.mkdir(exist_ok=True)

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
        return

    print("Checking for orphaned processes from ./released/...")

    try:
        killed_any = False

        if platform.system() == 'Windows':
            # Find all .exe files in released/
            executables = [f.name for f in released_dir.rglob('*.exe')]

            # Don't kill uv.exe (it's a tool, not a test process)
            executables = [exe for exe in executables if exe.lower() != 'uv.exe']

            for exe_name in executables:
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', exe_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    print(f"  Killed orphaned {exe_name} processes")
                    killed_any = True
                # Silently ignore "not found" errors

            if killed_any:
                # Give Windows time to released file handles
                time.sleep(1)
            else:
                print("  No orphaned processes found")

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
                    print(f"  Killed orphaned {exe_name} processes")
                    killed_any = True
                # pkill returns 1 when no processes found -- silently ignore

            if killed_any:
                time.sleep(0.5)
            else:
                print("  No orphaned processes found")

    except subprocess.TimeoutExpired:
        print("  Warning: Process cleanup timed out", file=sys.stderr)
    except FileNotFoundError:
        print("  Warning: Process cleanup tool not found (taskkill/pkill)", file=sys.stderr)
    except Exception as e:
        print(f"  Warning: Process cleanup failed: {e}", file=sys.stderr)

def run_command(cmd, description, timeout=3600, env=None):
    """Run a command and return exit code and output.

    Uses Popen with real-time output capture and proper process killing on timeout.

    Args:
        cmd: Command to run (string or list)
        description: Description for output
        timeout: Timeout in seconds
        env: Optional environment variables dict (defaults to os.environ)
    """
    print(f"\n{'=' * 60}")
    print(f"{description}")
    print(f"{'=' * 60}\n")

    import shlex
    if isinstance(cmd, str):
        cmd_list = shlex.split(cmd, posix=False)  # posix=False for Windows
    else:
        cmd_list = cmd

    # Use provided env or inherit current environment
    if env is None:
        env = os.environ

    process = subprocess.Popen(
        cmd_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        bufsize=1,  # Line buffered
        env=env
    )

    output_lines = []
    start_time = time.time()
    timed_out = False

    def read_stream(stream, output_list, prefix=""):
        """Read from stream line by line and append to output_list."""
        try:
            for line in iter(stream.readline, ''):
                if not line:
                    break
                output_list.append(prefix + line)
        except Exception as e:
            output_list.append(f"\n[ERROR reading stream: {e}]\n")

    # Start threads to read stdout and stderr concurrently
    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, output_lines))
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, output_lines, "[stderr] "))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    # Monitor for timeout
    while process.poll() is None:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            timed_out = True
            output_lines.append(f"\n{'=' * 60}\n")
            output_lines.append(f"[TIMEOUT] Process exceeded {timeout} seconds\n")
            output_lines.append(f"{'=' * 60}\n")
            output_lines.append(f"[KILLING PROCESS] Attempting to terminate PID {process.pid}...\n")

            # Try graceful termination first
            try:
                process.terminate()
                try:
                    process.wait(timeout=5)
                    output_lines.append(f"[KILLED] Process terminated gracefully\n")
                except subprocess.TimeoutExpired:
                    # Force kill if termination didn't work
                    process.kill()
                    process.wait(timeout=5)
                    output_lines.append(f"[KILLED] Process force-killed\n")
            except Exception as e:
                output_lines.append(f"[ERROR] Failed to kill process: {e}\n")

            output_lines.append(f"\n[DIAGNOSTIC] Last output above shows where the test hung\n")
            break
        time.sleep(0.1)  # Check every 100ms

    # Wait for reading threads to finish (give them a moment to catch up)
    stdout_thread.join(timeout=5)
    stderr_thread.join(timeout=5)

    # Get final return code
    if timed_out:
        returncode = 124
    else:
        returncode = process.returncode

    output = ''.join(output_lines)
    return returncode, output

def is_code_review_test(test_file):
    """Check if test is a code-review test that calls prompt-ai.

    Code-review tests need longer timeouts (3600s) because they call AI.
    Regular tests that test ./released/ artifacts use shorter timeouts (120s).
    """
    try:
        content = Path(test_file).read_text(encoding='utf-8')
        # Check for references to prompt-ai or code-inspection-assertion scripts
        return ('prompt-ai.py' in content or
                'prompt_agentic_coder' in content or
                'code-inspection-assertion.py' in content)
    except Exception:
        # If we can't read the file, assume regular test
        return False

def write_report(test_filename, exit_code, output):
    """Write a timestamped report to the reports directory."""
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]  # Millisecond precision

    # Determine status with special handling for timeouts and build failures
    if exit_code == 0:
        status = "PASS"
    elif exit_code == 97:
        status = "BUILD_FAILED"
    elif exit_code == 99:
        status = "EXTERNAL_DEPENDENCY_FAILURE"
    elif exit_code == 124:
        status = "TIMEOUT"
    else:
        status = "FAIL"

    # Extract just the filename without path for the report
    test_name = Path(test_filename).stem

    report_name = f"{timestamp}_test_{test_name}_{status}.md"
    report_path = reports_dir / report_name

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Test Report: {test_name}\n\n")
        f.write(f"**Status:** {status}\n")
        f.write(f"**Exit Code:** {exit_code}\n")
        f.write(f"**Timestamp:** {timestamp}\n")
        f.write(f"**Test File:** {test_filename}\n\n")
        f.write(f"## Output\n\n")
        f.write("```\n")
        f.write(output)
        f.write("\n```\n")

    print(f"\nReport written to: {report_path}")
    return report_path

def main():
    parser = argparse.ArgumentParser(description='Run a single test file with build step')
    parser.add_argument('test_file', help='Test file to run')
    parser.add_argument('--timeout', type=int, help='Timeout in seconds (default: auto-detect based on test type)')
    parser.add_argument('--no-build', action='store_true', help='Skip build step')

    args = parser.parse_args()

    # Validate test file exists
    test_path = Path(args.test_file)
    if not test_path.exists():
        print(f"ERROR: Test file does not exist: {args.test_file}")
        sys.exit(1)

    # Auto-detect timeout if not explicitly provided
    if args.timeout is None:
        if is_code_review_test(args.test_file):
            timeout = 3600  # 1 hour for code-review tests (call AI)
            timeout_reason = "code-review test (calls prompt-ai)"
        else:
            timeout = 180   # 3 minutes for regular tests (test ./released/)
            timeout_reason = "regular test"
        print(f"Auto-detected timeout: {timeout}s ({timeout_reason})")
    else:
        timeout = args.timeout
        print(f"Using explicit timeout: {timeout}s")

    # Step 0: Kill orphaned processes before build
    if not args.no_build:
        kill_orphan_processes()
        print()

        # Step 1: Run build script
    if not args.no_build:
        build_script = Path('./code/build.py')
        if not build_script.exists():
            print(f"ERROR: {build_script} does not exist")
            sys.exit(1)

        # Check if this is an installer test -- set BUILD_INSTALLER env var
        build_env = os.environ.copy()
        if 'installer' in str(args.test_file).lower():
            build_env['BUILD_INSTALLER'] = 'true'
            print("Detected installer test -- enabling BUILD_INSTALLER")

        print(f"\nStep 1: Running build script")
        exit_code, build_output = run_command(
            [str(UV_PATH), 'run', '--script', str(build_script)],
            'Building project',
            timeout=timeout,
            env=build_env
        )
        print(build_output)

        if exit_code != 0:
            print(f"\n{'=' * 60}")
            print(f"BUILD FAILED (exit code {exit_code})")
            print(f"{'=' * 60}")
            print("Cannot run test until build succeeds.")
            print("Check build.py output above for errors.")
            print(f"{'=' * 60}\n")

            # Write report for build failure
            write_report(args.test_file, 97, build_output)

            sys.exit(97)  # Exit code 97 = build failure
    else:
        print(f"\nStep 1: Skipping build (no-build flag)")

    # Step 2: Run the test file
    print(f"\nStep 2: Running test file")
    exit_code, test_output = run_command(
        [str(UV_PATH), 'run', '--script', str(args.test_file)],
        f'Running test: {args.test_file}',
        timeout=timeout
    )
    print(test_output)

    # Step 3: Check for external dependency failure marker
    if 'EXTERNAL_DEPENDENCY_FAILURE' in test_output:
        print(f"\n{'=' * 60}")
        print("EXTERNAL DEPENDENCY FAILURE DETECTED")
        print(f"{'=' * 60}\n")
        write_report(args.test_file, 99, test_output)
        sys.exit(99)

    # Step 4: Write report and exit with test's exit code
    write_report(args.test_file, exit_code, test_output)

    print(f"\n{'=' * 60}")
    if exit_code == 0:
        print("OK Test passed")
    else:
        print(f"X Test failed with exit code {exit_code}")
    print(f"{'=' * 60}\n")

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
