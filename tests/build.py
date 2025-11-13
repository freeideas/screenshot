#!/usr/bin/env -S uv run --script
# type: ignore

"""
Build script for screenshot (C#) with NativeAOT.

Usage:
  uv run --script ./tests/build.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code" / "screenshot"
CSProj = CODE_DIR / "Screenshot.csproj"
RELEASE_DIR = ROOT / "release"


def main() -> int:
    # Pre-flight checks
    if not CSProj.exists():
        print(f"Missing project file: {CSProj}", file=sys.stderr)
        return 2

    # Clean release directory for artifacts we recreate
    if RELEASE_DIR.exists():
        # Remove everything to avoid stale artifacts
        shutil.rmtree(RELEASE_DIR)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    # Build AOT self-contained
    publish_aot_cmd = [
        "dotnet",
        "publish",
        str(CSProj),
        "-c",
        "Release",
        "-r",
        "win-x64",
        "-p:PublishAot=true",
        "-p:SelfContained=true",
        "-o",
        str(RELEASE_DIR),
        "--nologo",
        "--verbosity",
        "minimal",
    ]

    print("Building (AOT, self-contained)...")
    aot = subprocess.run(publish_aot_cmd, cwd=ROOT)
    if aot.returncode != 0:
        print("AOT build failed; falling back to non-AOT self-contained build...", file=sys.stderr)
        # Fallback: non-AOT, single-file, ReadyToRun to improve startup
        publish_fallback_cmd = [
            "dotnet",
            "publish",
            str(CSProj),
            "-c",
            "Release",
            "-r",
            "win-x64",
            "-p:PublishAot=false",
            "-p:PublishReadyToRun=true",
            "-p:PublishSingleFile=true",
            "-p:SelfContained=true",
            "-o",
            str(RELEASE_DIR),
            "--nologo",
            "--verbosity",
            "minimal",
        ]
        fb = subprocess.run(publish_fallback_cmd, cwd=ROOT)
        if fb.returncode != 0:
            print("Fallback build failed as well.", file=sys.stderr)
            return fb.returncode or 1

    # Verify artifact
    exe = RELEASE_DIR / ("screenshot.exe" if os.name == "nt" else "screenshot")
    if not exe.exists():
        print(f"Build succeeded but artifact missing: {exe}", file=sys.stderr)
        return 3

    # Keep release/ aligned with documentation: only ship the executable.
    # Remove any debug symbol files or other extras emitted by publish.
    for item in RELEASE_DIR.iterdir():
        if item.is_file() and item.suffix.lower() == ".pdb":
            try:
                item.unlink()
            except Exception as e:
                print(f"Warning: failed to remove {item.name}: {e}", file=sys.stderr)

    size = exe.stat().st_size
    print(f"Built: {exe} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
