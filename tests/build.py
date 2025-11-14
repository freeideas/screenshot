#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os
import shutil
import subprocess
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    code_dir = project_root / "code"
    release_dir = project_root / "release"

    print(f"Building from: {code_dir}")
    print(f"Output to: {release_dir}")

    # Step 1: Clean existing artifacts in ./release/
    if release_dir.exists():
        print(f"Cleaning existing release directory...")
        shutil.rmtree(release_dir)

    # Create release directory
    release_dir.mkdir(exist_ok=True)

    # Step 2: Build the project with AOT compilation
    print("Building AOT-compiled executable...")

    build_result = subprocess.run(
        ["dotnet", "publish", "-c", "Release", "-r", "win-x64", "--self-contained"],
        cwd=code_dir,
        capture_output=True,
        text=True
    )

    if build_result.returncode != 0:
        print("Build failed:", file=sys.stderr)
        print(build_result.stdout, file=sys.stderr)
        print(build_result.stderr, file=sys.stderr)
        return 1

    print("Build successful")

    # Step 3: Copy only necessary runtime files to ./release/
    # The AOT-compiled executable is in code/bin/Release/net8.0-windows/win-x64/publish/
    publish_dir = code_dir / "bin" / "Release" / "net8.0-windows" / "win-x64" / "publish"

    if not publish_dir.exists():
        print(f"Error: Publish directory not found at {publish_dir}", file=sys.stderr)
        return 1

    # Copy only the executable (AOT compilation produces a single exe with no dependencies)
    exe_file = publish_dir / "screenshot.exe"

    if not exe_file.exists():
        print(f"Error: Executable not found at {exe_file}", file=sys.stderr)
        return 1

    print(f"Copying {exe_file.name} to release/")
    shutil.copy2(exe_file, release_dir / "screenshot.exe")

    print(f"\nBuild complete! Executable: {release_dir / 'screenshot.exe'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
