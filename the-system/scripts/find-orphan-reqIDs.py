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
from pathlib import Path
from collections import defaultdict

# Import build-req-index to rebuild database
import importlib.util
_build_req_index_spec = importlib.util.spec_from_file_location("build_req_index", Path(__file__).parent / "build-req-index.py")
build_req_index = importlib.util.module_from_spec(_build_req_index_spec)
_build_req_index_spec.loader.exec_module(build_req_index)

def find_orphans(db_path='./tmp/reqs.sqlite'):
    """Find $REQ_IDs in tests/code without requirement definitions.

    Args:
        db_path: Path to the SQLite database (default: ./tmp/reqs.sqlite)

    Returns:
        dict: Orphan req_ids with their locations
              Format: {req_id: [(filespec, line_num, category), ...]}
              Empty dict if no orphans found
    """
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}", file=sys.stderr)
        print("Run build-req-index.py first to create the database", file=sys.stderr)
        return None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find req_ids that appear in tests or code but NOT in req_definitions
    # This is an orphan: referenced but never defined
    cursor.execute('''
        SELECT DISTINCT rl.req_id, rl.filespec, rl.line_num, rl.category
        FROM req_locations rl
        WHERE rl.category IN ('tests', 'code')
          AND rl.req_id NOT IN (SELECT req_id FROM req_definitions)
        ORDER BY rl.req_id, rl.filespec, rl.line_num
    ''')

    results = cursor.fetchall()
    conn.close()

    # Group by req_id
    orphans = defaultdict(list)
    for req_id, filespec, line_num, category in results:
        orphans[req_id].append((filespec, line_num, category))

    return dict(orphans)

def print_orphans(orphans):
    """Print orphan req_ids in a human-readable format.

    Args:
        orphans: dict from find_orphans()

    Returns:
        Number of orphan req_ids found
    """
    if not orphans:
        return 0

    print("=" * 60)
    print("ORPHAN $REQ_IDs FOUND")
    print("=" * 60)
    print()
    print("The following $REQ_IDs appear in tests/code but have no")
    print("definition in ./reqs/*.md:")
    print()

    for req_id in sorted(orphans.keys()):
        locations = orphans[req_id]
        print(f"{req_id}")

        # Group locations by category
        tests_locs = [(f, l) for f, l, c in locations if c == 'tests']
        code_locs = [(f, l) for f, l, c in locations if c == 'code']

        if tests_locs:
            print(f"  In tests:")
            for filespec, line_num in tests_locs:
                print(f"    {filespec}:{line_num}")

        if code_locs:
            print(f"  In code:")
            for filespec, line_num in code_locs:
                print(f"    {filespec}:{line_num}")

        print()

    print("=" * 60)
    print(f"Total orphans: {len(orphans)}")
    print("=" * 60)
    print()

    return len(orphans)

def main():
    """Main entry point when run from command line."""
    # Change to project root (two levels up from this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)

    # Update the requirements index before checking for orphans
    try:
        # Import and run build-req-index to ensure database is current
        build_req_index.main()
    except Exception as e:
        print(f"Error building index: {e}", file=sys.stderr)
        return 1

    print()

    orphans = find_orphans()

    if orphans is None:
        # Database not found (shouldn't happen after building)
        return 1

    num_orphans = print_orphans(orphans)

    if num_orphans > 0:
        print("Action needed: Remove these orphan $REQ_IDs or add their")
        print("definitions to ./reqs/*.md")
        print()
        return 1
    else:
        print("OK No orphan $REQ_IDs found")
        print()
        return 0

if __name__ == '__main__':
    sys.exit(main())
