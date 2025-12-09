# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Safe Script Execution Utility

Provides a consistent mechanism for executing Python scripts via subprocess,
isolating the parent process from any errors in the child script.

This handles:
- Missing scripts
- Syntax errors
- Runtime exceptions
- Timeouts
- Import errors
- Any other script failures

All scripts are executed via ./the-system/bin/uv.exe run --script to respect dependency declarations.
"""

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional


def get_uv_path() -> Path:
    """Get path to uv binary in the-system/bin/ (platform-specific)"""
    script_dir = Path(__file__).parent

    if platform.system() == 'Windows':
        uv_name = 'uv.exe'
    elif platform.system() == 'Darwin':
        uv_name = 'uv.mac'
    else:
        uv_name = 'uv.linux'

    uv_path = script_dir.parent / 'bin' / uv_name
    if not uv_path.exists():
        raise FileNotFoundError(f"{uv_name} not found at: {uv_path}")
    return uv_path


def run_script(
    script_path: str | Path,
    args: Optional[List[str]] = None,
    timeout: int = 600,
    cwd: Optional[str | Path] = None,
    stream: bool = False
) -> Dict:
    """
    Execute a Python script safely via subprocess using ./the-system/bin/uv.exe run --script.

    Args:
        script_path: Path to the Python script to execute
        args: Optional list of command-line arguments to pass to the script
        timeout: Timeout in seconds (default: 600 = 10 minutes)
        cwd: Working directory for script execution (default: current directory)
        stream: If True, stream stdout/stderr directly to parent instead of capturing

    Returns:
        Dict with keys:
            - success: bool (True if exit code was 0)
            - exit_code: int (script's exit code, or special codes for errors)
            - stdout: str (captured stdout)
            - stderr: str (captured stderr)
            - exception: str | None (exception type if subprocess itself failed)

    Special exit codes:
        - 127: Script file not found
        - 124: Timeout expired
        - Other non-zero: Script's actual exit code
    """
    script_path = Path(script_path).resolve()

    # Check if script exists
    if not script_path.exists():
        return {
            'success': False,
            'exit_code': 127,
            'stdout': '',
            'stderr': f'Script not found: {script_path}',
            'exception': 'FileNotFoundError'
        }

    # Build command using our local uv.exe
    try:
        uv_path = get_uv_path()
    except FileNotFoundError as e:
        return {
            'success': False,
            'exit_code': 127,
            'stdout': '',
            'stderr': str(e),
            'exception': 'FileNotFoundError'
        }

    cmd = [str(uv_path), 'run', '--script', str(script_path)]
    if args:
        cmd.extend(args)

    # Execute in subprocess
    try:
        if stream:
            completed = subprocess.run(
                cmd,
                text=True,
                encoding='utf-8',
                timeout=timeout,
                cwd=cwd or Path.cwd()
            )
            return {
                'success': completed.returncode == 0,
                'exit_code': completed.returncode,
                'stdout': '',
                'stderr': '',
                'exception': None
            }
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=timeout,
                cwd=cwd or Path.cwd()
            )

            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exception': None
            }

    except subprocess.TimeoutExpired as e:
        return {
            'success': False,
            'exit_code': 124,
            'stdout': e.stdout.decode('utf-8') if e.stdout else '',
            'stderr': e.stderr.decode('utf-8') if e.stderr else f'Script timed out after {timeout} seconds',
            'exception': 'TimeoutExpired'
        }

    except Exception as e:
        return {
            'success': False,
            'exit_code': 1,
            'stdout': '',
            'stderr': f'Error executing script: {e}',
            'exception': type(e).__name__
        }


def run_script_and_exit(
    script_path: str | Path,
    args: Optional[List[str]] = None,
    timeout: int = 600,
    cwd: Optional[str | Path] = None
) -> None:
    """
    Execute a script and exit with its exit code.

    Useful for wrapper scripts that just need to forward to another script.
    Prints stdout/stderr from the child script and exits with its exit code.
    """
    result = run_script(script_path, args, timeout, cwd)

    # Print captured output
    if result['stdout']:
        print(result['stdout'], end='')
    if result['stderr']:
        print(result['stderr'], end='', file=sys.stderr)

    # Exit with the script's exit code
    sys.exit(result['exit_code'])


if __name__ == '__main__':
    # When run directly, execute the script specified as first argument
    if len(sys.argv) < 2:
        print("Usage: run-script.py <script_path> [args...]", file=sys.stderr)
        sys.exit(1)

    script_path = sys.argv[1]
    script_args = sys.argv[2:] if len(sys.argv) > 2 else None

    run_script_and_exit(script_path, script_args)
