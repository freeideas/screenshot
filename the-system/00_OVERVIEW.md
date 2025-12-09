# The-System: Overview

Build working software from clear documentation with one command.

This system is:
  *REPEATABLE* -- The same specifications will result in approximately the same code and software every time
  *RELIABLE* -- Good specifications will result in good software every time
  *MAINTAINABLE*
    -- Super easy to fix bugs
    -- Best documented project you have ever seen
    -- The code is very straightfoward; doesn't look "machine generated" at all

---

## How To Use

1. Write your docs: `README.md` and files in `specs/` (optionally `docs/`).
2. Run: `./the-system/software-construction.bat`.
3. Find fully-tested and completed software in `./released/`.

### Command-Line Options

- `./the-system/software-construction.bat` -- Full build (requirements, code, tests)
- `./the-system/software-construction.bat --skip-reqs` -- Skip requirement generation, use existing `./reqs/` documents
- `./the-system/software-construction.bat --skip-to-testing` -- Skip requirements and code generation, only run test verification loop

### How To Fix Bugs or Add Features

1. Edit your `specs/` documents (correct ambiguities, add test cases, clarify requirements)
2. Re-run: `./the-system/software-construction.bat`

The system regenerates requirements, code, and tests based on your updated specs.

### How To Redesign

1. Edit your `specs/` documents with the new design
2. Delete the `code/`, `reqs/`, and `tests/` directories
3. Re-run: `./the-system/software-construction.bat`

For significant redesigns, old artifacts usually get in the way. Deleting them forces a clean regeneration from your updated specs.

---

## Source Of Truth

- You write: `README.md`, `specs/`, `docs/` - the design (WHAT to build).
- AI generates (disposable):
  - `reqs/` - testable requirement flows from your docs
  - `code/` - implementation from requirements + docs
  - `tests/` - test suite from requirements
  - `released/` - build artifacts shaped by tests

Change the docs and rerun to regenerate everything.

---

## Workflow Summary

- Generate requirements -> generate code -> generate tests -> fix until tests pass.
- Runs autonomously; prompts only when docs need fixes or external deps fail.
- Phases: requirements (01_REQ-GEN.md) then code + verification (02_CODE-GEN.md).

---

## When You Catch Bugs

1. Revise your specs/ documents
   -- Correct an ambiguity?
   -- Add a test case?
   -- More directly say what you want
2. Re-run `./the-system/software-construction.bat`

---

## If you make major changes

1. Run `./the-system/scripts/nuke.py` to start from nothing but README.md and specs/
2. Run `./the-system/software-construction.bat`

## Incremental Workflow (Re-running After Changes)

**The system is optimized for iterative refinement.**

When you modify specs and re-run `software-construction.bat`:

1. **Requirements regeneration** - AI edits existing requirement files in `reqs/` where possible
2. **Code regeneration** - AI edits existing code files in `code/` where possible
3. **Test staging** - All tests moved to `tests/failing/` for re-verification
4. **Fast re-verification** - Tests that still pass quickly return to `tests/passing/`
5. **Focused fixing** - Only genuinely broken tests require time to fix

### Why This Works

**Stage-and-re-verify pattern:**
- Ensures all tests still pass after code changes
- Fast tests zip through quickly (no rebuild needed)
- Only genuinely broken tests slow down the process
- No complex tracking of "what changed"

**Orphan test deletion:**
- If a requirement file is renamed, its test becomes orphaned (no matching requirement)
- Orphaned tests are deleted and regenerated
- This is correct - we cannot reliably match renamed tests to renamed requirements

**Result:** Minor design changes require minimal re-work. Only tests affected by actual behavior changes need fixing.

---

## Project-Invariant System

The `the-system/` directory is identical across projects and should not be edited per-project. Copy it into any repo as `./the-system/` and use it as-is.

---

## Directory Structure

```
your-project/
|-- README.md                    # You write: Overview, build info
|-- specs/                       # You write: Workflows, concerns
|-- reqs/                        # AI generates: Testable requirements
|-- code/                        # AI generates: Implementation
|-- tests/                       # AI generates: Test suite
|   |-- failing/                 # Tests in progress
|   \-- passing/                 # Tests that pass
|-- released/                    # Build produces: Final artifacts
|-- reports/                     # AI writes: Operation reports
|-- tmp/                         # Scripts create: Temp files, DB
\-- the-system/                  # System files (copy this directory)
    |-- scripts/                 # Orchestration scripts
    \-- prompts/                 # AI prompts
```

---

## More Docs

- 01_REQ-GEN.md - requirements generation workflow
- 02_CODE-GEN.md - code generation and verification workflow
- SCRIPTS.md - scripts and usage
- PROMPTS.md - prompts and purposes
- PHILOSOPHY.md - core principles