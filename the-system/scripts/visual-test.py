# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Visual verification testing using AI.

Asks AI to examine a screenshot and verify it matches a description.
AI writes either ./tmp/YES_{uid}.md or ./tmp/NO_{uid}.md to indicate result.

Usage:
    visual-test.py <image_file> <description>

Examples:
    visual-test.py ./tmp/screenshot.png "A Windows command prompt"
    visual-test.py ./tmp/notepad.png "Windows Notepad application"

Exit codes:
    0 - Visual verification passed (YES file found)
    1 - Visual verification failed (NO file found)
    2 - Error (neither file found, or other error)

This script can also be imported and used as a module:
    from visual_test import check_visual
    passed = check_visual("./tmp/screenshot.png", "A Windows command prompt")
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import argparse
import time
from pathlib import Path

# Change to project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
os.chdir(PROJECT_ROOT)

# Base62 characters for UID generation
BASE62_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def import_script(script_name):
    """Import a script from the same directory as a module."""
    import importlib.util
    script_path = SCRIPT_DIR / f'{script_name}.py'
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import required modules
prompt_ai = import_script('prompt-ai')


def generate_uid() -> str:
    """
    Generate a unique ID from the last 8 base62 digits of microseconds since epoch.

    Returns:
        str: 8-character base62 string
    """
    # Get microseconds since epoch
    microseconds = int(time.time() * 1_000_000)

    # Convert to base62, keeping last 8 digits
    uid = ""
    while microseconds > 0 and len(uid) < 8:
        uid = BASE62_CHARS[microseconds % 62] + uid
        microseconds //= 62

    # Pad with leading zeros if needed
    uid = uid.zfill(8)

    # Take last 8 characters
    return uid[-8:]


def check_visual(image_file: str, description: str, timeout: int = 300) -> tuple:
    """
    Check if a screenshot matches a description using AI visual verification.

    Args:
        image_file: Path to the image file to examine
        description: Expected visual description to match against
        timeout: Maximum seconds for AI analysis (default: 300)

    Returns:
        tuple: (passed: bool, explanation: str)
            - passed: True if image matches description, False otherwise
            - explanation: AI's reasoning for the decision

    Raises:
        RuntimeError: If AI execution fails or neither YES/NO file is created
        FileNotFoundError: If image file or prompt template doesn't exist
    """
    image_path = Path(image_file)

    if not image_path.exists():
        raise FileNotFoundError(f"Image file does not exist: {image_path}")

    # Generate unique ID
    uid = generate_uid()

    print(f"\nVisual verification test")
    print(f"  Image: {image_path}")
    print(f"  Description: {description}")
    print(f"  UID: {uid}")
    print()

    # Ensure tmp directory exists
    tmp_dir = Path("./tmp")
    tmp_dir.mkdir(exist_ok=True)

    # Define result file paths
    yes_file = tmp_dir / f"YES_{uid}.md"
    no_file = tmp_dir / f"NO_{uid}.md"

    # Clean up any pre-existing result files (shouldn't exist, but just in case)
    if yes_file.exists():
        yes_file.unlink()
    if no_file.exists():
        no_file.unlink()

    # Load prompt template
    prompt_template_path = SCRIPT_DIR.parent / 'prompts' / 'VISUAL_TEST.md'
    if not prompt_template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_template_path}")

    prompt_template = prompt_template_path.read_text(encoding='utf-8')

    # Fill in template variables
    prompt_text = prompt_template.replace('{IMAGE_FILE}', str(image_path.resolve()))
    prompt_text = prompt_text.replace('{DESCRIPTION}', description)
    prompt_text = prompt_text.replace('{UID}', uid)

    # Run AI prompt
    print("Running AI visual inspection...")
    try:
        response = prompt_ai.get_ai_response_text(
            prompt_text,
            report_type=f'visual_test_{uid}',
            timeout=timeout
        )
        print("AI inspection completed")
        print()
    except Exception as e:
        raise RuntimeError(f"AI execution failed: {e}")

    # Check for result files
    if yes_file.exists():
        content = yes_file.read_text(encoding='utf-8').strip()
        print(f"OK VISUAL TEST PASSED")
        print()
        print(content)
        print()
        return (True, content)
    elif no_file.exists():
        content = no_file.read_text(encoding='utf-8').strip()
        print(f"X VISUAL TEST FAILED")
        print()
        print(content)
        print()
        return (False, content)
    else:
        raise RuntimeError(f"AI did not create result file (expected ./tmp/YES_{uid}.md or ./tmp/NO_{uid}.md)")


def main():
    parser = argparse.ArgumentParser(
        description='Visual verification testing using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./tmp/screenshot.png "A Windows command prompt"
  %(prog)s ./tmp/notepad.png "Windows Notepad application"
  %(prog)s ./tmp/browser.png "Web browser showing Google" --timeout 600
        """
    )
    parser.add_argument(
        'image_file',
        help='Path to the image file to examine'
    )
    parser.add_argument(
        'description',
        help='Expected visual description to match against'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Maximum seconds for AI analysis (default: 300)'
    )

    args = parser.parse_args()

    try:
        passed, explanation = check_visual(
            image_file=args.image_file,
            description=args.description,
            timeout=args.timeout
        )

        sys.exit(0 if passed else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
