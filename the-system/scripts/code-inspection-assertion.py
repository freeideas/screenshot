# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Code inspection assertion testing.

Tests architectural/design requirements by asking AI to modify code if assertion fails.
Test passes if code remains unchanged (assertion already true).
Test fails if code was modified (assertion was violated).

Usage:
    code-inspection-assertion.py <assertion> [--code-path <path>] [--timeout <seconds>]

Examples:
    code-inspection-assertion.py "Uses Kestrel's thread pool for request handling"
    code-inspection-assertion.py "Single plugin instance serves all requests" --code-path ./code
    code-inspection-assertion.py "No mutable static state" --timeout 600

This script can also be imported and used as a module:
    from code_inspection_assertion import check_assertion
    passed = check_assertion("Uses async I/O", code_path="./code")
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import argparse
from pathlib import Path

# Change to project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
os.chdir(PROJECT_ROOT)


def import_script(script_name):
    """Import a script from the same directory as a module."""
    import importlib.util
    script_path = SCRIPT_DIR / f'{script_name}.py'
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import required modules
compute_signature = import_script('compute-signature')
prompt_ai = import_script('prompt-ai')


def take_signature(paths):
    """Helper to compute signature for given paths."""
    return compute_signature.compute_signature(paths)


def check_assertion(assertion: str, code_path: str = './code', timeout: int = 600, req_id: str = None) -> bool:
    """
    Check if code conforms to assertion.

    Args:
        assertion: The architectural/design requirement to verify
        code_path: Path to code directory to inspect (default: ./code)
        timeout: Maximum seconds for AI analysis (default: 600)
        req_id: Optional $REQ_ID to tag in report (default: None)

    Returns:
        bool: True if assertion holds (code unchanged), False if violated (code modified)

    Raises:
        RuntimeError: If AI execution fails
        FileNotFoundError: If code_path or prompt template doesn't exist
    """
    code_path = Path(code_path)

    if not code_path.exists():
        raise FileNotFoundError(f"Code path does not exist: {code_path}")

    print(f"\nChecking assertion: {assertion}")
    print(f"Code path: {code_path}")
    print()

    # Take signature BEFORE
    print("Computing signature BEFORE assertion check...")
    sig_before = take_signature([str(code_path)])
    print(f"  Signature BEFORE: {sig_before[:16]}...")
    print()

    # Load prompt template
    prompt_template_path = SCRIPT_DIR.parent / 'prompts' / 'CODE_INSPECTION_ASSERTION.md'
    if not prompt_template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_template_path}")

    prompt_template = prompt_template_path.read_text(encoding='utf-8')

    # Fill in template variables
    prompt_text = prompt_template.replace('{ASSERTION}', assertion)
    prompt_text = prompt_text.replace('{CODE_PATH}', str(code_path))
    if req_id:
        prompt_text = prompt_text.replace('{REQ_ID}', req_id)
    else:
        prompt_text = prompt_text.replace('{REQ_ID}', '(no $REQ_ID specified)')

    # Run AI prompt
    print("Running AI code inspection...")
    report_type = f'code_inspection_assertion'
    if req_id:
        report_type = f'code_inspection_{req_id}'

    try:
        response = prompt_ai.get_ai_response_text(
            prompt_text,
            report_type=report_type,
            timeout=timeout
        )
        print("AI inspection completed")
        print()
    except Exception as e:
        raise RuntimeError(f"AI execution failed: {e}")

    # Take signature AFTER
    print("Computing signature AFTER assertion check...")
    sig_after = take_signature([str(code_path)])
    print(f"  Signature AFTER: {sig_after[:16]}...")
    print()

    # Compare signatures
    if sig_before == sig_after:
        print("OK ASSERTION PASSED: Code unchanged (assertion holds)")
        print()
        return True
    else:
        print("X ASSERTION FAILED: Code was modified (assertion violated)")
        print()
        print("The AI modified your code to satisfy the assertion.")
        print("This means the assertion was NOT true before the check.")
        print()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Code inspection assertion testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Uses Kestrel's thread pool for request handling"
  %(prog)s "Single plugin instance serves all requests" --code-path ./code
  %(prog)s "No mutable static state" --timeout 600 --req-id REQ_THREAD_003
        """
    )
    parser.add_argument(
        'assertion',
        help='The architectural/design requirement to verify'
    )
    parser.add_argument(
        '--code-path',
        default='./code',
        help='Path to code directory to inspect (default: ./code)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=600,
        help='Maximum seconds for AI analysis (default: 600)'
    )
    parser.add_argument(
        '--req-id',
        help='Optional $REQ_ID to tag in report'
    )

    args = parser.parse_args()

    try:
        passed = check_assertion(
            assertion=args.assertion,
            code_path=args.code_path,
            timeout=args.timeout,
            req_id=args.req_id
        )

        sys.exit(0 if passed else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
