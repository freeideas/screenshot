# Code Generation and Verification Phase

**Purpose:** Generate code and verify correctness through testing

---

## Philosophy

**Source of truth:** Human-written documentation (README.md, specs/, docs/)

**Inputs for this phase:** AI-generated requirements (from phase 1)

**Disposable outputs:** Code, tests, and released artifacts

- Code generates from requirements + documentation
- Tests generate from requirements
- Tests shape code by finding and fixing bugs
- Released artifacts come from code shaped by tests

Change requirements or documentation? Run `./the-system/software-construction.bat` to regenerate everything.

See [PHILOSOPHY.md](./PHILOSOPHY.md)

---

## Actor Legend

- **HUMAN:** User actions
- **AI:** Autonomous AI operations
- **SCRIPT:** Script execution (no AI inference)

---

## Step Numbering

**P2.x** = Code Generation
**P3.x** = Test Preparation
**P4.x** = Per-Requirement Test Generation and Execution
**P5.x** = Completion

---

## Prerequisites

1. Requirements exist: ./reqs/*.md with numeric prefixes
2. Phase 1 (requirements generation) completed first
   - `./the-system/software-construction.bat` runs both phases automatically

---

## Workflow

### P2: Code Generation

**P2.1 (AI):** Generate implementation (prompt: VIBE_CODE.md)
- Read README.md and ./specs/*
- Write/rewrite all ./code/* including build.py

---

### P3: Test Preparation

**P3.1 (SCRIPT):** Prepare test directories (./tests/failing/, ./tests/passing/)

**P3.2 (SCRIPT/AI):** Remove orphan $REQ_IDs (script: find-orphan-reqIDs.py, then prompt: REMOVE_ORPHAN_REQS.md)
- find-orphan-reqIDs.py builds requirements index (./reqs/*.md, ./tests/**/*.py, ./code/**/* -> ./tmp/reqs.sqlite)
- Orphan = $REQ_ID in tests/code but not in requirements

**P3.3 (SCRIPT):** Stage tests for re-verification
- Move all existing tests from ./tests/passing/ to ./tests/failing/ (to verify they still pass after code changes)
- Delete orphan tests (tests with no matching requirement file - these cannot be matched after requirement renames)
- Note: Tests that still pass will quickly return to ./tests/passing/ in P4

**P3.4 (SCRIPT):** Kill orphan processes
- Find all executables in ./released/ directory
- Kill any running instances (safety net for tests that failed to cleanup)
- Prevents DLL/file locking issues on Windows
- Note: Tests should use atexit.register() to cleanup their own processes

---

### P4: Per-Requirement Test Generation and Execution

**Goal:** For each requirement document, generate/fix test until it passes

Process sequentially in numeric order (01_build.md, 02_startup.md, etc.)

#### Sub-Loop (One Requirement at a Time)

**P4.1** SCRIPT Find next requirement document
- All done -> Go to P5
- Found one -> Continue to P4.2

**P4.2 (A) (SCRIPT):** If test already exists for this requirement:
- Rebuild requirements index (script: build-req-index.py)
- Verify all $REQ_IDs from req file exist in test (SQL query)
- If all $REQ_IDs present: Run test (script: test.py, output saved to ./reports/)
- If test passes -> Go to P4.4 (D)
- If test fails or $REQ_IDs missing -> Continue to P4.3 (B)

**P4.3 (B) (AI):** Run test-fix loop (prompt: TEST-FIX_LOOP.md)
- AI writes/fixes test and/or code until test passes
- AI runs test internally during this step
- Test MUST mention EVERY $REQ_ID from req file
- Testable: Assertions with `# $REQ_ID` comments
- Untestable: Comment `# $REQ_ID - Not reasonably testable: [reason]`
- **Exit 99:** External dependency failure -> Exit with code 99
- **If attempt > 5:** Exit with code 98 (stuck)
- When AI reports success -> Continue to P4.4 (C)

**P4.4 (C) (SCRIPT):** Verify test REALLY passes (script: test.py, output saved to ./reports/)
- Run test again (double-check after AI fixes)
- **Exit 99:** External dependency failure -> Exit with code 99
- **Fail:** Increment attempt, go to P4.3 (B)
- **Pass:** Continue to P4.5 (D)

**P4.5 (D) (AI):** Verify test quality (prompt: VERIFY_TEST.md)
- Purpose: Check test quality and ensure it correctly tests requirements
- Take signature before/after (script: compute-signature.py <test_file>)
- **Modified:** Test was changed by verification -> Go to P4.2 (A) to re-run
- **Unchanged:** Test is valid -> Continue to P4.6 (E)

**P4.6 (E) (SCRIPT):** Move passing test
- Move test from ./tests/failing/ to ./tests/passing/
- Continue to next requirement (P4.1)

**P4.7 (SCRIPT):** Integration recheck (after all requirements processed)
- Build once for the suite; run tests without rebuilding between them
- Run all tests currently in ./tests/passing/ again to ensure they pass together (each test run saved to ./reports/)
- If ANY fail -> Move ALL tests back to ./tests/failing/ and restart P4 from the first requirement
- If ALL pass -> Proceed to P5


---

### P5: Completion

**P5.1 (SCRIPT):** All tests passing (./tests/failing/ empty)

**P5.2 (SCRIPT):** Generate summary (count $REQ_IDs, tests, list ./released/)

**P5.3 (SCRIPT):** Exit code 0 (success)

---

## Exit Conditions

**OK Success (Code 0):** P5.3 -> Software complete, artifacts in ./released/
**RETRY Stuck (Code 98):** P4.2 (>5 attempts on one req) -> Review ./reports/, fix requirements
**BLOCKED External Dependency (Code 99):** P4.8 -> Fix external component, re-run
**FAIL Error (Code 1):** System error -> Check ./reports/, fix, re-run

---

## Test Types

**Regular tests (most common):** Test ./released/ artifacts
- Run executables, make HTTP requests, verify files
- Black-box testing of compiled software

**Code-review tests (exception):** Inspect ./code/*
- For requirements difficult to test externally (e.g., "use separate threads for each request")
- AI reviews code, modifies if needed, passes if signature unchanged

