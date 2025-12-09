#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os
import subprocess
import shutil
import platform

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def find_cargo():
    """Find cargo executable, checking PATH first, then ./compiler/

    Returns: (cargo_path, extra_path) tuple
        - cargo_path: Path to cargo executable, or None if not found
        - extra_path: Directory to add to PATH for rustc, or None if not needed
    """
    # Check PATH
    cargo = shutil.which("cargo")
    if cargo:
        return cargo, None

    # Check ./compiler/ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    compiler_bin_dir = os.path.join(project_root, "compiler", "cargo", "bin")
    if platform.system() == "Windows":
        compiler_cargo = os.path.join(compiler_bin_dir, "cargo.exe")
    else:
        compiler_cargo = os.path.join(compiler_bin_dir, "cargo")

    if os.path.exists(compiler_cargo):
        return compiler_cargo, compiler_bin_dir

    return None, None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    released_dir = os.path.join(project_root, "released")

    print("✓ Finding Rust compiler...")
    cargo, extra_path = find_cargo()
    if not cargo:
        print("✗ Error: cargo not found on PATH or in ./compiler/")
        return 1

    print(f"✓ Using cargo: {cargo}")

    # Prepare environment with extra PATH if needed (for rustc)
    env = os.environ.copy()
    if extra_path:
        env["PATH"] = extra_path + os.pathsep + env.get("PATH", "")
        print(f"✓ Added {extra_path} to PATH for rustc")

    print("✓ Building screenshot in release mode...")
    result = subprocess.run(
        [cargo, "build", "--release"],
        cwd=script_dir,
        text=True,
        encoding='utf-8',
        env=env
    )

    if result.returncode != 0:
        print("✗ Build failed")
        return 1

    print("✓ Build completed successfully")

    # Determine binary name based on platform
    if platform.system() == "Windows":
        binary_name = "screenshot.exe"
    else:
        binary_name = "screenshot.exe"  # Use .exe even on non-Windows per project convention

    # Source binary location
    if platform.system() == "Windows":
        source_binary = os.path.join(script_dir, "target", "release", "screenshot.exe")
    else:
        source_binary = os.path.join(script_dir, "target", "release", "screenshot")

    if not os.path.exists(source_binary):
        print(f"✗ Error: Built binary not found at {source_binary}")
        return 1

    # Create released directory
    os.makedirs(released_dir, exist_ok=True)

    # Copy to released directory
    dest_binary = os.path.join(released_dir, binary_name)
    print(f"✓ Copying {source_binary} to {dest_binary}")
    shutil.copy2(source_binary, dest_binary)

    print(f"✓ Successfully created {dest_binary}")
    print("✓ Build complete!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
