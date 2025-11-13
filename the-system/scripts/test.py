#!/usr/bin/env uvrun
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
import signal
from pathlib import Path
from datetime import datetime

# Change to project root (two levels up from this script)
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
os.chdir(project_root)

# Path to bundled uv.exe
UV_EXE = str(project_root / 'the-system' / 'bin' / 'uv.exe')

# Create reports directory
reports_dir = Path('./reports')
reports_dir.mkdir(exist_ok=True)

def run_command(cmd, description, capture_output=False, test_filename=None, timeout=3600):
    """Run a command and return exit code, optionally capturing output.

    Uses Popen with real-time output capture and proper process killing on timeout.
    """
    print(f"\n{'=' * 60}")
    print(f"{description}")
    print(f"{'=' * 60}\n")
    # Convert command string to list for shell=False (better Windows compatibility)
    import shlex
    if isinstance(cmd, str):
        cmd_list = shlex.split(cmd, posix=False)  # posix=False for Windows
    else:
        cmd_list = cmd

    if not capture_output:
        # For non-captured output (like build), use simple subprocess.run
        try:
            result = subprocess.run(cmd_list, shell=False, timeout=timeout)
            return result.returncode
        except subprocess.TimeoutExpired:
            print(f"\nCommand timed out after {timeout} seconds\n")
            return 124

    # For captured output, use Popen with real-time streaming and proper kill
    process = subprocess.Popen(
        cmd_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered
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
    stdout_thread.join(timeout=1)
    stderr_thread.join(timeout=1)

    # Get final return code
    if timed_out:
        returncode = 124
    else:
        returncode = process.returncode

    output = ''.join(output_lines)
    return returncode, output

def write_report(test_filename, exit_code, output):
    """Write a timestamped report to the reports directory."""
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    status = "PASS" if exit_code == 0 else "FAIL"

    # Extract just the filename without path for the report
    test_name = Path(test_filename).name

    report_name = f"{timestamp}_{test_name}.txt"
    report_path = reports_dir / report_name

    with open(report_path, 'w') as f:
        f.write(f"{test_name} {status}\n")
        f.write(output)

    # Print report file path for parent scripts to read
    print(f"report file: {report_path}")

    return report_path

def main():
    parser = argparse.ArgumentParser(description='Run tests with build step')
    parser.add_argument('--passing', action='store_true', help='Run only passing tests')
    parser.add_argument('--failing', action='store_true', help='Run only failing tests')
    parser.add_argument('test_file', nargs='?', help='Specific test file to run')

    args = parser.parse_args()

    # Step 1: Run build script
    if not os.path.exists('./tests/build.py'):
        print("ERROR: ./tests/build.py does not exist")
        print("Run work-queue.py to see what needs to be done")
        sys.exit(1)

    exit_code = run_command([UV_EXE, 'run', '--script', './tests/build.py'], 'Building project')
    if exit_code != 0:
        print(f"\nBuild failed with exit code {exit_code}")
        sys.exit(exit_code)

    # Step 2: Determine which tests to run
    if args.test_file:
        # Run specific test file
        test_target = args.test_file
    elif args.passing:
        # Run all passing tests
        test_target = './tests/passing'
        if not os.path.exists(test_target) or not os.listdir(test_target):
            print("\nNo passing tests found")
            sys.exit(0)
    elif args.failing:
        # Run all failing tests
        test_target = './tests/failing'
        if not os.path.exists(test_target) or not os.listdir(test_target):
            print("\nNo failing tests found")
            sys.exit(0)
    else:
        # Default: run failing tests if they exist, otherwise passing tests
        if os.path.exists('./tests/failing') and os.listdir('./tests/failing'):
            test_target = './tests/failing'
        elif os.path.exists('./tests/passing') and os.listdir('./tests/passing'):
            test_target = './tests/passing'
        else:
            print("\nNo tests found")
            sys.exit(0)

    # Step 3: Run tests directly (no pytest)
    if args.test_file:
        # Run single test file
        exit_code, output = run_command(
            [UV_EXE, 'run', '--script', test_target],
            f'Running test: {test_target}',
            capture_output=True,
            test_filename=test_target,
            timeout=120,
        )
        print(output)  # Print output to console
        write_report(test_target, exit_code, output)
    else:
        # Run all tests in directory
        import glob
        test_files = glob.glob(f'{test_target}/test_*.py') + glob.glob(f'{test_target}/_test_*.py')
        if not test_files:
            print(f"\nNo test files found in {test_target}")
            return 0

        failed = []
        for test_file in test_files:
            exit_code, output = run_command(
                [UV_EXE, 'run', '--script', test_file],
                f'Running test: {test_file}',
                capture_output=True,
                test_filename=test_file,
                timeout=120,
            )
            print(output)  # Print output to console
            report_path = write_report(test_file, exit_code, output)
            print(f"Report written to: {report_path}")
            if exit_code != 0:
                failed.append(test_file)

        if failed:
            print(f"\n✗ {len(failed)} test(s) failed:")
            for f in failed:
                print(f"  - {f}")
            exit_code = 1
        else:
            print(f"\n✓ All {len(test_files)} test(s) passed")
            exit_code = 0

    print(f"\n{'=' * 60}")
    if exit_code == 0:
        print("✓ All tests passed")
    else:
        print(f"✗ Tests failed with exit code {exit_code}")
    print(f"{'=' * 60}\n")

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
