#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import subprocess
import re
import os
from pathlib import Path
from datetime import datetime

def main():
    """Test capture by window ID flow -- verify all window ID capture requirements."""

    created_files = []

    try:
        print("Starting capture by ID test...", flush=True)

        # Step 1: Get window list to find a valid window ID
        print("Getting window list to find a valid window ID...", flush=True)
        result = subprocess.run(
            ['./release/screenshot.exe'],
            capture_output=True,
            timeout=10
        )
        print(f"Screenshot.exe exited with code {result.returncode}", flush=True)

        # Decode output
        try:
            output = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            output = result.stdout.decode('cp1252', errors='replace')

        # Parse window list to extract first window ID
        print("Parsing window list...", flush=True)
        lines = output.split('\n')
        window_id = None
        window_title = None

        for line in lines:
            # Look for lines with tab separators and quoted titles
            if '\t' in line and '"' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    candidate_id = parts[0].strip()
                    # Verify it's alphanumeric hexadecimal
                    if re.match(r'^[0-9A-Fa-f]+$', candidate_id):
                        window_id = candidate_id
                        # Extract title from quoted string
                        title_part = '\t'.join(parts[2:])
                        match = re.search(r'"([^"]*)"', title_part)
                        if match:
                            window_title = match.group(1)
                        break

        assert window_id is not None, "Could not find a valid window ID from window list"  # $REQ_ID_001
        print(f"✓ Found window ID: {window_id}", flush=True)
        print(f"  Window title: {window_title}", flush=True)

        # $REQ_ID_001: Accept Window ID Argument
        # Verify that window ID is alphanumeric
        assert re.match(r'^[0-9A-Fa-f]+$', window_id), f"Window ID '{window_id}' is not alphanumeric"  # $REQ_ID_001
        print("✓ Window ID is alphanumeric", flush=True)

        # Ensure tmp directory exists
        os.makedirs('./tmp', exist_ok=True)
        print("✓ Created ./tmp directory", flush=True)

        # Step 2: Test capture with explicit file path
        print(f"\nTest 1: Capture by ID with explicit file path...", flush=True)
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
        output_file1 = f'./tmp/{timestamp}_capture-by-id-test1.png'
        print(f"Capturing to {output_file1}...", flush=True)

        result = subprocess.run(
            ['./release/screenshot.exe', '--id', window_id, output_file1],
            capture_output=True,
            timeout=10
        )
        print(f"Screenshot.exe exited with code {result.returncode}", flush=True)

        # Decode output
        try:
            capture_output = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            capture_output = result.stdout.decode('cp1252', errors='replace')

        print(f"Output: {capture_output}", flush=True)

        # $REQ_ID_002: Capture Window by ID
        assert result.returncode == 0, f"Capture by ID failed with exit code {result.returncode}"  # $REQ_ID_002
        print("✓ Capture by ID succeeded", flush=True)

        # $REQ_ID_003: Save to Explicit File Path
        assert os.path.exists(output_file1), f"Output file {output_file1} was not created"  # $REQ_ID_003
        created_files.append(output_file1)
        print(f"✓ File created at explicit path: {output_file1}", flush=True)

        # $REQ_ID_006: Output Success Message
        assert 'Wrote' in capture_output, "Missing 'Wrote' in output message"  # $REQ_ID_006
        assert output_file1 in capture_output or output_file1.replace('./', '') in capture_output or Path(output_file1).resolve().as_posix() in capture_output, f"Output message does not contain filepath {output_file1}"  # $REQ_ID_006
        print("✓ Success message shows 'Wrote [filepath]'", flush=True)

        # $REQ_ID_007: PNG Format Output
        with open(output_file1, 'rb') as f:
            header = f.read(8)
            # PNG signature: 89 50 4E 47 0D 0A 1A 0A
            assert header == b'\x89PNG\r\n\x1a\n', "File is not a valid PNG (incorrect signature)"  # $REQ_ID_007
        print("✓ File is valid PNG format", flush=True)

        # Verify file has content
        file_size = os.path.getsize(output_file1)
        assert file_size > 1000, f"Screenshot file is suspiciously small: {file_size} bytes"  # $REQ_ID_002
        print(f"✓ File size is reasonable: {file_size} bytes", flush=True)

        # Step 3: Test capture to directory with timestamped filename
        print(f"\nTest 2: Capture by ID to directory...", flush=True)
        print(f"Capturing to ./tmp/ directory...", flush=True)

        result = subprocess.run(
            ['./release/screenshot.exe', '--id', window_id, './tmp/'],
            capture_output=True,
            timeout=10
        )
        print(f"Screenshot.exe exited with code {result.returncode}", flush=True)

        # Decode output
        try:
            capture_output2 = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            capture_output2 = result.stdout.decode('cp1252', errors='replace')

        print(f"Output: {capture_output2}", flush=True)

        assert result.returncode == 0, f"Capture to directory failed with exit code {result.returncode}"  # $REQ_ID_004
        print("✓ Capture to directory succeeded", flush=True)

        # $REQ_ID_004: Save to Directory with Timestamped Filename
        # Extract filename from output message
        match = re.search(r'Wrote (.+)', capture_output2)
        assert match, "Could not find 'Wrote [filepath]' in output"  # $REQ_ID_004
        output_file2 = match.group(1).strip()
        print(f"Output file: {output_file2}", flush=True)

        # Verify file exists
        assert os.path.exists(output_file2), f"Output file {output_file2} was not created"  # $REQ_ID_004
        created_files.append(output_file2)

        # Verify filename format: YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png
        filename = os.path.basename(output_file2)
        assert re.match(r'^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d+_screenshot\.png$', filename), \
            f"Filename '{filename}' does not match timestamped format YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png"  # $REQ_ID_004
        print(f"✓ Timestamped filename format correct: {filename}", flush=True)

        # Step 4: Test capture to current directory (omitted path)
        print(f"\nTest 3: Capture by ID with omitted output path...", flush=True)
        print(f"Capturing with no output path specified...", flush=True)

        result = subprocess.run(
            ['./release/screenshot.exe', '--id', window_id],
            capture_output=True,
            timeout=10
        )
        print(f"Screenshot.exe exited with code {result.returncode}", flush=True)

        # Decode output
        try:
            capture_output3 = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            capture_output3 = result.stdout.decode('cp1252', errors='replace')

        print(f"Output: {capture_output3}", flush=True)

        assert result.returncode == 0, f"Capture with omitted path failed with exit code {result.returncode}"  # $REQ_ID_005
        print("✓ Capture with omitted path succeeded", flush=True)

        # $REQ_ID_005: Save to Current Directory with Timestamped Filename
        # Extract filename from output message
        match = re.search(r'Wrote (.+)', capture_output3)
        assert match, "Could not find 'Wrote [filepath]' in output"  # $REQ_ID_005
        output_file3 = match.group(1).strip()
        print(f"Output file: {output_file3}", flush=True)

        # Verify file exists
        assert os.path.exists(output_file3), f"Output file {output_file3} was not created"  # $REQ_ID_005
        created_files.append(output_file3)

        # Verify filename is in current directory (not a subdirectory)
        # The file should be in ./ or current directory
        file_dir = os.path.dirname(output_file3) if os.path.dirname(output_file3) else '.'
        assert file_dir == '.' or file_dir == '', \
            f"File '{output_file3}' was not created in current directory (found in '{file_dir}')"  # $REQ_ID_005
        print(f"✓ File created in current directory", flush=True)

        # Verify filename format
        filename = os.path.basename(output_file3)
        assert re.match(r'^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d+_screenshot\.png$', filename), \
            f"Filename '{filename}' does not match timestamped format"  # $REQ_ID_005
        print(f"✓ Timestamped filename format correct: {filename}", flush=True)

        # Step 5: AI-based visual verification for window decorations
        print(f"\nTest 4: AI visual verification of window capture...", flush=True)
        print(f"Using prompt_agentic_coder to verify window decorations...", flush=True)

        # Import the prompt_agentic_coder module
        sys.path.insert(0, './the-system/scripts')
        from prompt_agentic_coder import get_ai_response_text

        # Use first captured file for AI verification
        prompt = f"""Verify this screenshot shows a complete window capture with:
1. Window title bar visible at the top
2. Window borders/decorations around the edges
3. The window content area

This should be a full window screenshot, not just the content area.

Screenshot file: {Path(output_file1).absolute()}

IMPORTANT: Analyze the screenshot and determine if it matches the description above.
- If it matches, start your response with "YES" on its own line, followed by your explanation.
- If it does NOT match, start your response with "NO" on its own line, followed by your explanation."""

        try:
            ai_response = get_ai_response_text(prompt, report_type="screenshot_test")
            print(f"AI response: {ai_response[:200]}...", flush=True)

            # Check for YES or NO in the response
            lines = ai_response.splitlines()
            result = None

            for line in lines:
                stripped = line.strip().upper()
                # Look for YES or NO at the start of a line
                if stripped.startswith('YES'):
                    result = 'YES'
                    break
                if stripped.startswith('NO'):
                    result = 'NO'
                    break

            # $REQ_ID_008: Capture Full Window
            assert result == 'YES', f"AI verification failed - screenshot may not show full window with decorations. AI said: {result}"  # $REQ_ID_008
            print("✓ AI confirms screenshot shows full window with title bar and decorations", flush=True)
        except Exception as e:
            print(f"Error during AI verification: {e}", flush=True)
            raise

        print("\n✓ All tests passed", flush=True)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}", flush=True)
        return 1
    except subprocess.TimeoutExpired:
        print("\n✗ Test failed: subprocess timed out", flush=True)
        return 1
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Clean up created files
        print("\nCleaning up test files...", flush=True)
        for filepath in created_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Removed {filepath}", flush=True)
            except Exception as e:
                print(f"Failed to remove {filepath}: {e}", flush=True)

if __name__ == '__main__':
    sys.exit(main())
