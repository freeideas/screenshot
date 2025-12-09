Run the test and fix code/test until it passes.

## Context

- **Requirement:** {{REQ_FILE_PATH}}
- **Test:** {{TEST_FILE_PATH}}
- **Attempt:** {{ATTEMPT}}

## OVERRIDE: Project Testing Standards

**IMPORTANT: Before following any instructions below, check if `./specs/TESTING.md` exists.**

If `./specs/TESTING.md` exists:
- Read it FIRST before fixing any tests
- Follow ALL instructions in `./specs/TESTING.md`
- `./specs/TESTING.md` takes PRECEDENCE over any conflicting instructions in this prompt
- Only use the instructions below for topics not covered in `./specs/TESTING.md`

If `./specs/TESTING.md` does not exist, proceed with the instructions below.

## Task

Iterate autonomously until the test passes. Read requirements, read test failures, fix code/test, repeat.

## CRITICAL: How to Run Tests

**ALWAYS use this command to run tests:**

```bash
./the-system/bin/uv.exe run --script ./the-system/scripts/test.py {{TEST_FILE_PATH}}
```

**NEVER run test files directly** (like `./the-system/bin/uv.exe run --script {{TEST_FILE_PATH}}`).

**Why this matters:**
- test.py runs build.py first, ensuring you test against current code
- test.py kills orphaned processes before building (prevents file locking)
- test.py writes detailed reports to ./reports/ including build failures
- Running tests directly skips the build step and gives FALSE POSITIVE results

**Exit codes you'll see:**
- **0** = Build succeeded, test passed
- **1** = Test failed (build succeeded but test assertions failed)
- **97** = Build failed (cannot run test until build is fixed)
- **99** = External dependency failure (needs human intervention)
- **124** = Test timed out (>3 minutes)

**If you see exit code 97 (build failure):**
1. Check the test.py output for build errors
2. Fix build.py or source code issues FIRST
3. Do not attempt to fix test until build succeeds

## Philosophy

- **Ruthless simplification** -- Complex code is wrong code. Delete and rewrite simply.
- **Test reveals design flaws** -- Failing test usually means implementation is wrong, not test.

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

**YES** → Fix test with assertions
**YES, with pre-built fixture** → Fix test using fixture from ./released/
**NO (needs build/download)** → Mark as not reasonably testable

### Example: Testing Invalid Input Handling

❌ **WRONG** - Compiles during test (slow):
```python
# $REQ_INVALID_INPUT_001 - Test with malformed data handler
with open('./tmp/TestHandler.cs', 'w') as f:
    f.write('public class TestHandler { /* invalid code */ }')
subprocess.run(['dotnet', 'build', './tmp/TestHandler.csproj'])  # Compiles code!
result = subprocess.run(['./tmp/TestHandler.dll'])
assert result.returncode != 0
```

✅ **RIGHT** - Tests pre-built artifact (fast):
```python
# $REQ_INVALID_INPUT_001 - Test with malformed data handler
with open('./tmp/invalid.json', 'w') as f:
    f.write('{ invalid json }}')  # Just a text file
result = subprocess.run(['./released/app.exe', '--input', './tmp/invalid.json'])
assert result.returncode == 1
assert 'invalid' in result.stderr.lower()
```

✅ **ALSO ACCEPTABLE** - Mark as not testable:
```python
# $REQ_INVALID_INPUT_001 - Not reasonably testable: Would require compiling code during test
```

**Remember:** build.py already ran. Your test should only test ./released/ artifacts.

## Tools

**Track requirements/test/code together:**
```bash
./the-system/bin/uv.exe run --script ./the-system/scripts/track-reqIDs.py --req-file {{REQ_FILE_PATH}}
```

**AI-powered code inspection (for architectural requirements):**
```bash
./the-system/bin/uv.exe run --script ./the-system/scripts/code-inspection-assertion.py "Assertion text" --req-id REQ_X
```
- Exit 0 = assertion holds (code unchanged)
- Exit 1 = assertion violated (code modified, re-run test)

**AI-powered visual verification (for GUI/screenshot testing):**
```bash
./the-system/bin/uv.exe run --script ./the-system/scripts/visual-test.py <image_path> "description"
```
- Exit 0 = screenshot matches description, 1 = doesn't match, 2 = error
- Or import as module: `passed, explanation = visual_test.check_visual(image_path, description)`

## What You Can Modify

OK ./code/* (including build.py) -- **Mark changes with $REQ_ID comments when fixing specific requirements**
OK {{TEST_FILE_PATH}} -- **Edit content ONLY. DO NOT rename or move the test file.**

**Example:**
```csharp
// $REQ_ENDPOINT_002 - Fixed port binding
app.Urls.Add("http://127.0.0.1:8080");
```

## What You Cannot Modify

FAIL {{REQ_FILE_PATH}}
FAIL README.md, ./specs/*.md
FAIL Other test files
FAIL Renaming or moving {{TEST_FILE_PATH}} -- **The test file path is fixed by the orchestration script**

**Note:** Tests use plain Python (`assert`, `sys.exit()`, exceptions), not pytest.

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

## External Dependency Failures

If test fails due to unavailable external service (not your code's fault), add to test:

```python
result = subprocess.run(['external-service', '--check'])
if result.returncode != 0:
    print("EXTERNAL_DEPENDENCY_FAILURE")
    print("External service 'external-service' is not available")
    sys.exit(99)
```

Only use exit code 99 for truly external failures needing human intervention.

## Common Issues

- **Build failures** -> Fix ./code/build.py and/or source files
  - If compiler not found on PATH, check `./compiler/` directory (see `./the-system/prompts/DOWNLOAD_COMPILER.md`)
- **Missing functionality** -> Implement what requirement says
- **Wrong behavior** -> Read requirement, implement correctly
- **Test too strict** -> Relax assertions not in requirements
- **Complex buggy code** -> Delete and rewrite simply

## Success

OK Test exits with code 0
OK All assertions pass
OK All $REQ_IDs verified

The orchestration script runs the test after you complete. Fix all issues you can identify before finishing.
