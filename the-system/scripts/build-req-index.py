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
import sqlite3
import re
from pathlib import Path

# Change to project root (two levels up from this script)
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
os.chdir(project_root)

def create_database():
    """Create the requirements database with schema."""
    db_path = './tmp/reqs.sqlite'

    # Ensure tmp directory exists
    os.makedirs('./tmp', exist_ok=True)

    # Remove old database if exists
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create req_definitions table
    cursor.execute('''
        CREATE TABLE req_definitions (
            req_id TEXT PRIMARY KEY,
            req_text TEXT,
            source_attribution TEXT,
            flow_file TEXT
        )
    ''')

    # Create req_locations table
    cursor.execute('''
        CREATE TABLE req_locations (
            req_id TEXT,
            filespec TEXT,
            line_num INTEGER,
            category TEXT
        )
    ''')

    # Create index for faster queries
    cursor.execute('CREATE INDEX idx_req_locations_id ON req_locations(req_id)')

    conn.commit()
    conn.close()

    return db_path

def scan_reqs_files(conn):
    """Scan ./reqs/*.md files for requirement definitions and locations."""
    cursor = conn.cursor()
    reqs_dir = Path('./reqs')

    if not reqs_dir.exists():
        return

    for req_file in sorted(reqs_dir.glob('*.md')):
        with open(req_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, start=1):
            # Find all $REQ_ID mentions in this line
            req_ids = re.findall(r'\$REQ_[A-Z0-9_]+', line)

            for req_id in req_ids:
                # Check if this is a definition header (## $REQ_ID: Title)
                is_definition_header = line.strip().startswith('##') and ':' in line

                if is_definition_header:
                    # Extract requirement text (title after the colon)
                    text_after_id = line.split(req_id, 1)[1] if req_id in line else ""
                    req_text = text_after_id.strip()

                    # Look for source attribution on the next line
                    source_attribution = None
                    if line_num < len(lines):
                        next_line = lines[line_num].strip()  # line_num is already 1-based, so lines[line_num] is next line
                        if next_line.startswith('**Source:**'):
                            # Extract everything after '**Source:**'
                            source_attribution = next_line.replace('**Source:**', '').strip()

                    # Store definition (only if not already stored)
                    cursor.execute(
                        "SELECT req_id FROM req_definitions WHERE req_id = ?",
                        (req_id,)
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO req_definitions (req_id, req_text, source_attribution, flow_file) VALUES (?, ?, ?, ?)",
                            (req_id, req_text, source_attribution, str(req_file))
                        )

                # Store location for all occurrences (definition or reference)
                cursor.execute(
                    "INSERT INTO req_locations (req_id, filespec, line_num, category) VALUES (?, ?, ?, ?)",
                    (req_id, str(req_file), line_num, 'reqs')
                )

    conn.commit()

def scan_test_files(conn):
    """Scan ./tests/**/*.py files for requirement references."""
    cursor = conn.cursor()
    tests_dir = Path('./tests')

    if not tests_dir.exists():
        return

    for test_file in tests_dir.rglob('*.py'):
        with open(test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, start=1):
            # Find all $REQ_ID mentions in this line
            req_ids = re.findall(r'\$REQ_[A-Z0-9_]+', line)

            for req_id in req_ids:
                # Store location
                cursor.execute(
                    "INSERT INTO req_locations (req_id, filespec, line_num, category) VALUES (?, ?, ?, ?)",
                    (req_id, str(test_file), line_num, 'tests')
                )

    conn.commit()

def scan_code_files(conn):
    """Scan ./code/**/* files for requirement references."""
    cursor = conn.cursor()
    code_dir = Path('./code')

    if not code_dir.exists():
        return

    # Scan all files (not just specific extensions, to catch all code files)
    for code_file in code_dir.rglob('*'):
        # Skip directories
        if code_file.is_dir():
            continue

        # Skip binary files (simple heuristic: check extension)
        binary_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin', '.obj', '.o', '.a', '.lib'}
        if code_file.suffix.lower() in binary_extensions:
            continue

        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, start=1):
                # Find all $REQ_ID mentions in this line
                req_ids = re.findall(r'\$REQ_[A-Z0-9_]+', line)

                for req_id in req_ids:
                    # Store location
                    cursor.execute(
                        "INSERT INTO req_locations (req_id, filespec, line_num, category) VALUES (?, ?, ?, ?)",
                        (req_id, str(code_file), line_num, 'code')
                    )
        except (UnicodeDecodeError, IOError):
            # Skip files that can't be read as text
            continue

    conn.commit()

def print_summary(conn):
    """Print a summary of the database contents."""
    cursor = conn.cursor()

    # Count definitions
    cursor.execute("SELECT COUNT(*) FROM req_definitions")
    num_definitions = cursor.fetchone()[0]

    # Count unique req_ids in locations
    cursor.execute("SELECT COUNT(DISTINCT req_id) FROM req_locations")
    num_referenced = cursor.fetchone()[0]

    # Count by category
    cursor.execute("SELECT category, COUNT(*) FROM req_locations GROUP BY category")
    category_counts = cursor.fetchall()

    print(f"OK Requirements index built successfully")
    print(f"  Database: ./tmp/reqs.sqlite")
    print(f"  Definitions: {num_definitions}")
    print(f"  Referenced: {num_referenced}")

    if category_counts:
        print(f"  Locations:")
        for category, count in category_counts:
            print(f"    {category}: {count}")

def main():
    print("Building requirements index...")

    # Create database
    db_path = create_database()
    conn = sqlite3.connect(db_path)

    # Scan all directories
    scan_reqs_files(conn)
    scan_test_files(conn)
    scan_code_files(conn)

    # Print summary
    print_summary(conn)

    conn.close()

if __name__ == '__main__':
    main()
