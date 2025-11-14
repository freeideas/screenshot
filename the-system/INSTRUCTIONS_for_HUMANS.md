# How to Build Software with This System

Transform README documentation into working, tested software through two AI-driven phases.

---

## Prerequisites

**Configure your AI agent:**
- Must have a clco.bat (for claude code) and/or cdxcli.bat (for codex) in your PATH
- (optional) Edit near the top of `./the-system/scripts/prompt_agentic_coder.py` to switch between "claude" and "codex"
- (optional) Put uv.exe on your path; this is the best way to run python scripts
  wget https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip -OutFile uv.zip

**Note:** No Python installation needed! The `.exe` files in `./the-system/` bundle everything required.

---

## Phase 1: Requirements Generation

**Goal:** Transform your README documentation into testable requirement flows.

### Step 1: Write README documents

Create use-case oriented documentation:
- `README.md` -- Project overview, what the software does
- `./readme/*.md` -- One file per use case, user perspective, or workflow

**Example for a web server:**
- `README.md` -- Overview and what goes in `./release/`
- `./readme/STARTUP.md` -- Starting and stopping the server
- `./readme/API.md` -- API endpoints and responses
- `./readme/DEPLOYMENT.md` -- Production deployment

**You probably want to write a TESTING.md:**
- Usually `./readme/TESTING.md` -- says what in particular is important to test "in addition to other tests" (so the ai won't skip the usual tests)
- Two special kinds of tests are available to you:
    -- Say "use code review to verify" things like "each connection runs in its own thread" or "output is buffered in memory so disk i/o won't block".
       Such things are difficult to test for externally, but easy to see in the code.
    -- Say "check a screenshot to make sure the UI looks as the README documents describe".
       The AI can take screenshots of the app it is testing and analyze them -- this is new and experimental; see test-screenshot.py

**Performance and load testing:** This system tests functional behavior, not performance characteristics. Write "must handle multiple connections" (testable), not "must handle 10,000 connections" (not reliably testable). Specific throughput numbers, latency requirements, and load testing are not what this system does.

### Step 2: Generate Flows

```bash
./the-system/reqs-gen.exe
# Or: uv run --script ./the-system/scripts/reqs-gen.py
```

The AI reads your documentation and generates testable requirement flows in `./reqs/`.

**Common issues:** If the script reports problems (READMEBUG status), it means your README documentation needs clarification. For example, if you say "port number is required" but don't specify what happens when it's missing (error? default? ignore?), the AI can't write testable requirements.

If there are problems with your readme docs, the script will stop. Look under the ./reports directory and figure out what to do. Usually you will want to edit your readme docs, but sometimes you will just tell the process to continue because the problems in the report are not really problems. Use your own judgement.


### Step 3: Review and Iterate

1. When the ai stops writing and revising ./req documents
2. Look at the console; if it stopped because all reqs looked good to the ai, then proceed to phase 2
3. Look at the last 5 or so report documents in the ./reports directory; ask yourself, "were these significant problems or are they unimportant?"
4. If the problems were significant then consider revising your README documents and starting reqs-gen again.
5. If the problems were trivial (which is the most likely scenario) proceed to phase 2

**Important:** The flows in `./reqs/` are what gets implemented and tested, so they must be good before proceeding to Phase 2.

---

## Phase 2: Software Construction

**Goal:** Build and test software from the requirement flows.

### Step 4: Build Software

```bash
./the-system/software-construction.exe
# Or: uv run --script ./the-system/scripts/software-construction.py
```

The AI automatically:
1. Creates a build script (`./tests/build.py`)
2. Writes tests for all requirements
3. Implements code to pass the tests
4. Fixes failures until all tests pass

The script runs iteratively -- it will keep working until all tests pass with no changes needed.

### Step 5: Monitor Progress

Watch `./reports/` directory for AI activity reports. If you see the process going the wrong way or want to change requirements:
1. Stop the construction script (Ctrl+C)
2. Revise `./readme/` documentation
3. Re-run `reqs-gen.py` to regenerate flows
4. Re-run `software-construction.py` to continue building

** WARNING: ** You will often realize the README docs are not what you really wanted, by reading these reports.

---

## Summary

Two phases, both with human oversight:

1. **Requirements Generation** -- Write/revise READMEs → AI generates flows → Review flows → Iterate until correct
2. **Software Construction** -- AI writes tests and code → Runs tests → Fixes failures → Done when all tests pass

Any change to README documentation (usually) requires re-running `reqs-gen.py`.

### Exceptions
1. Trivial changes: (e.g. misspelling of a word in an error message): Change README, and ask the ai directly to make the corresponding change to the code. and to any ./reqs/ docs that are affected.
2. Redesigns: You might be better off nuking the project (e.g. delete everything except README docs and "the-system" directory); and starting at phase 1

---

## When Bugs Escape Detection

If you find bugs after construction completes:
1. Interactively prompt the ai to understand the root cause
2. Update README docs to clarify expected behavior
3. Re-run `reqs-gen.exe` to regenerate flows
4. Re-run `software-construction.exe` to fix the bug

---

## Need More Detail?

See `@the-system/HOW_THIS_WORKS.md` for detailed explanation of flows, tests, and traceability.
