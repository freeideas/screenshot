#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import os
import shutil
import subprocess
import sys

def main():
    # Fix Windows console encoding for Unicode characters
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    code_dir = os.path.join(project_root, "code")
    release_dir = os.path.join(project_root, "release")

    # Delete existing artifacts in ./release/ that we'll recreate
    if os.path.exists(release_dir):
        print(f"Cleaning {release_dir}/")
        shutil.rmtree(release_dir)

    os.makedirs(release_dir, exist_ok=True)

    # Build the C# project with AOT compilation
    print("Building screenshot.exe with AOT compilation...")

    result = subprocess.run(
        ["dotnet", "publish", "-c", "Release"],
        cwd=code_dir,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Build failed:", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return 1

    print(result.stdout)

    # Find the build output directory
    build_output = os.path.join(code_dir, "bin", "Release", "net8.0-windows", "win-x64", "publish")

    if not os.path.exists(build_output):
        print(f"Error: Build output directory not found: {build_output}", file=sys.stderr)
        return 1

    # Copy only the executable to ./release/
    # AOT compilation produces a single .exe with no runtime dependencies
    exe_path = os.path.join(build_output, "screenshot.exe")

    if not os.path.exists(exe_path):
        print(f"Error: screenshot.exe not found in {build_output}", file=sys.stderr)
        return 1

    dest_path = os.path.join(release_dir, "screenshot.exe")
    shutil.copy2(exe_path, dest_path)
    print(f"Copied screenshot.exe to {release_dir}/")

    # Verify the executable was copied
    if not os.path.exists(dest_path):
        print(f"Error: Failed to copy screenshot.exe to {release_dir}", file=sys.stderr)
        return 1

    print(f"\nBuild successful!")
    print(f"Release artifact: {dest_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
