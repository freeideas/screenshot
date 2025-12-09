# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Compute content signature for change detection.

Takes one or more file or directory paths and produces a single signature
that represents the content of all files. The signature is order-independent
and deterministic - the same set of files will always produce the same signature
regardless of argument order or whether files are specified individually or via directory.

Usage:
    compute-signature.py <path> [<path2> ...]

Examples:
    compute-signature.py README.md ./specs/
    compute-signature.py ./reqs/
    compute-signature.py file1.md file2.md file3.md
"""

import sys
import hashlib
from pathlib import Path


def collect_files(paths: list[str]) -> set[Path]:
    """
    Collect all files from given paths (files and/or directories).
    Returns a set of absolute Path objects.
    """
    files = set()

    for path_str in paths:
        path = Path(path_str).resolve()

        if not path.exists():
            print(f"Error: Path does not exist: {path}", file=sys.stderr)
            sys.exit(1)

        if path.is_file():
            files.add(path)
        elif path.is_dir():
            # Recursively collect all files
            for item in path.rglob('*'):
                if item.is_file():
                    files.add(item)

    return files


def compute_signature(paths: list[str]) -> str:
    """
    Compute a signature for the given paths.

    Returns a hex digest string representing the content of all files.
    """
    # Collect all files
    files = collect_files(paths)

    if not files:
        print("Error: No files found", file=sys.stderr)
        sys.exit(1)

    # Sort files by their absolute path for determinism
    sorted_files = sorted(files)

    # Compute combined hash
    combined_hash = hashlib.sha256()

    for file_path in sorted_files:
        # Hash the relative path (relative to current working directory)
        try:
            rel_path = file_path.relative_to(Path.cwd())
        except ValueError:
            # If file is outside cwd, use absolute path
            rel_path = file_path

        path_str = str(rel_path).replace('\\', '/')  # Normalize path separators
        combined_hash.update(path_str.encode('utf-8'))
        combined_hash.update(b'\x00')  # Null separator

        # Hash the file content
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
                combined_hash.update(file_content)
                combined_hash.update(b'\x00')  # Null separator
        except Exception as e:
            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

    return combined_hash.hexdigest()


def main():
    if len(sys.argv) < 2:
        print("Usage: compute-signature.py <path> [<path2> ...]", file=sys.stderr)
        sys.exit(1)

    paths = sys.argv[1:]
    signature = compute_signature(paths)
    print(signature)


if __name__ == '__main__':
    main()
