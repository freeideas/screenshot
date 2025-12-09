Write a test file for ONE requirement document.

## Test Philosophy: Happy Path Only

**Test that correct inputs produce correct outputs. Do NOT test failure modes.**

- ✅ Valid plugin loads → server starts → SOAP works
- ❌ Invalid plugin → server fails with error message (NOT REQUIRED)
- ❌ Missing file → error message (NOT REQUIRED)
- ❌ Corrupted input → graceful failure (NOT REQUIRED)

Unless a requirement explicitly says "MUST fail with error X when Y happens", do not write tests that sabotage the system and verify failure behavior.

**Example of what NOT to do:**
```python
# DON'T: Testing what happens when you break things
result = subprocess.run([exe, '--plugin', 'nonexistent.dll'])
assert result.returncode != 0  # Verifying failure behavior

# DON'T: Creating invalid inputs to test error handling
with open('invalid.dll', 'w') as f:
    f.write('garbage')
result = subprocess.run([exe, '--plugin', 'invalid.dll'])
assert 'error' in result.stderr  # Verifying error messages
```

**Example of what TO do:**
```python
# DO: Test that valid usage works
proc = subprocess.Popen([exe, '--host', '127.0.0.1'], ...)
line = proc.stdout.readline()
assert 'Listening on port' in line  # Server started successfully
```

## Context

- **Requirement file:** {{REQ_FILE_PATH}}
- **$REQ_IDs to test:** {{REQ_IDS}}
- **Test file to write:** {{TEST_FILE_PATH}}

## OVERRIDE: Project Testing Standards

**IMPORTANT: Before following any instructions below, check if `./specs/TESTING.md` exists.**

If `./specs/TESTING.md` exists:
- Read it FIRST before writing any tests
- Follow ALL instructions in `./specs/TESTING.md`
- `./specs/TESTING.md` takes PRECEDENCE over any conflicting instructions in this prompt
- Only use the instructions below for topics not covered in `./specs/TESTING.md`

If `./specs/TESTING.md` does not exist, proceed with the instructions below.

## Critical: $REQ_ID Coverage

**EVERY $REQ_ID MUST BE MENTIONED:**

1. **If testable:** Assert with comment tag
   ```python
   # $REQ_BUILD_001
   assert Path('./released/MyApp.exe').exists()
   ```

2. **If NOT testable:** Comment explaining why
   ```python
   # $REQ_INTERNAL_001 - Not reasonably testable: Internal implementation detail
   ```

The script verifies all $REQ_IDs appear. Missing any = called again to fix.

**Use plain Python** (not pytest): normal `assert`, `sys.exit(1)`, or exceptions.

## Test Types

**Type 1: Regular Tests (most common)**
- Test ./released/ artifacts (black-box)
- Run executables, make HTTP requests, verify files/behavior

**Type 2: Visual Inspection Tests (for GUI/screenshot verification)**
- Use `./the-system/scripts/visual-test.py` to verify screenshots match descriptions
- Exits 0 if image matches description, 1 if not, 2 on error
- Or import as module: `passed, explanation = visual_test.check_visual(image_path, description)`

**Type 3: Code-Review Tests (exception)**
- Inspect ./code/* for architectural requirements hard to test externally
- Use pattern matching (`'threading.Thread' in content`) for simple checks
- Use `./the-system/scripts/code-inspection-assertion.py` for complex architectural checks:
  ```python
  result = subprocess.run([
      './the-system/bin/uv.exe', 'run', '--script',
      './the-system/scripts/code-inspection-assertion.py',
      "Uses Kestrel's thread pool (no manual thread creation)",
      '--req-id', 'REQ_THREAD_001'
  ], timeout=600)
  assert result.returncode == 0
  ```

## Test File Structure

**Required shebang:**
```python
#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = ["requests"]  # List test dependencies
# ///

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Test functions here

if __name__ == '__main__':
    # Call test functions, print results, exit 0 on success
```

## External Dependencies

If test fails due to unavailable external service (not your code), exit with code 99:
```python
result = subprocess.run(['external-service', '--check'])
if result.returncode != 0:
    print("EXTERNAL_DEPENDENCY_FAILURE")
    sys.exit(99)
```

## Test Performance: "Reasonably Testable" Definition

**A requirement is "reasonably testable" if you can verify it in under 60 seconds.**

Your test file runs AFTER build.py completes. The 3-minute timeout starts when your test begins.

### Fast Operations (✅ Reasonable)
- Run pre-built executables from ./released/
- Make HTTP requests to running services
- Read/write/check files
- Use system DLLs or pre-built test fixtures
- Copy and modify existing files

### Slow Operations (❌ Not Reasonable in Tests)
- Compile/build code (dotnet build, go build, cargo build, etc.)
- Download packages (NuGet restore, pip install, npm install, etc.)
- Run package managers or build tools
- Build test fixtures during test execution

### Decision Process

For each requirement, ask: "Can I verify this in <60 seconds?"

**YES** → Write test with assertions
**YES, with pre-built fixture** → Write test using fixture from ./released/
**NO (needs build/download)** → Mark as not reasonably testable

**Remember:** build.py already ran. Your test should only test ./released/ artifacts.

## Process Cleanup (CRITICAL)

**If your test launches executables from ./released/, you MUST ensure they are stopped when the test finishes.**

Tests that leave processes running cause file locking issues on subsequent builds/tests.

**Required pattern:**

```python
import subprocess
import atexit
import signal
import sys

# Track processes launched by this test
_test_processes = []

def cleanup_test_processes():
    """Kill any processes started by this test."""
    for proc in _test_processes:
        try:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=1)
        except:
            pass

# Register cleanup to run on exit (even if test fails)
atexit.register(cleanup_test_processes)

# When launching processes, track them:
proc = subprocess.Popen(['./released/MyApp.exe'])
_test_processes.append(proc)

# ... run your tests ...

# Cleanup happens automatically via atexit
```

**Key points:**
- Use `atexit.register()` so cleanup happens even when test fails
- Track ALL processes you launch in `_test_processes`
- Try `terminate()` first (graceful), then `kill()` if needed
- This prevents DLL/file locking issues on Windows

## Guidelines

- Use timeouts on subprocess calls
- Clear failure messages
- Let exceptions propagate (tests fail on exceptions)

## Now: Write or edit the Test

Read {{REQ_FILE_PATH}} and write or correct the test at {{TEST_FILE_PATH}}.

**Remember:** EVERY $REQ_ID must appear (assertion tag or `# $REQ_ID - Not testable: [reason]` comment
