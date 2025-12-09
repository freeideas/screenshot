# Requirements Generation Phase

**Purpose:** Generate testable requirements from human-written documentation

---

## Philosophy

**Source of truth:** Human-written documentation (README.md, specs/, docs/)

**Disposable output:** AI-generated requirements (reqs/)

Requirements are just the first transformation -- turning your design into testable flows. Change your documentation? Run `./the-system/software-construction.bat` to regenerate everything.

See [PHILOSOPHY.md](./PHILOSOPHY.md)

---

## Actor Legend

- **HUMAN:** User actions
- **AI:** Autonomous AI operations
- **SCRIPT:** Script execution (no AI inference)

---

## Step Numbering

**P0.x** = README/Specs Quality Check
**P1.x** = Requirements Generation

---

## Workflow

### Human: Write Documentation

**Step 1 (HUMAN):** Write/revise `./README.md`
- Project overview and behavior
- Expected files in `./released/` (e.g., "MyApp.exe plus .dll files")
- Build information (e.g., "AOT compiled with native-aot")

**Step 2 (HUMAN):** Write/revise `./specs/*.md`
- Organize by workflow/use case (STARTUP.md, ENDPOINTS.md, etc.)
- Document cross-cutting concerns (LOGGING.md, ERROR_HANDLING.md, etc.)
- Write from user/operator perspective
- Focus on observable behaviors

**Step 3 (HUMAN):** (Optional) Add supporting docs in `./docs/`
- External API docs, protocol specs, .wsdl files, etc.
- Must be referenced in README.md or ./specs/ to be used

**Step 4 (HUMAN):** Run: `./the-system/software-construction.bat`

---

### P0: README/Specs Quality Check

**P0.1 (SCRIPT):** Prepare workspace (clean reports, create directories)

**P0.2 (SCRIPT):** Take signature BEFORE (script: compute-signature.py README.md ./specs/)

**P0.3 (AI):** Fix quality issues (prompt: FIX_README-SPECS.md)
- Check for contradictions, vague specs, untestable claims, missing description of ./released/ files
- Write report: `./reports/YYYYMMDD_HHMMSS_readme_specs_quality.md`
- **If issues found:** Modify README.md and/or ./specs/*.md
- **If no issues:** Make no changes

**P0.4 (SCRIPT):** Take signature AFTER (script: compute-signature.py README.md ./specs/)

**P0.5 (SCRIPT):** Check if AI made changes
- **If changed:** Prompt user to review, ENTER continues, CTRL-C exits
- **If unchanged:** Continue to P1

---

### P1: Requirements Generation

**Goal:** Generate startup-to-shutdown requirement flows in ./reqs/

**Important:** Specs (./specs/*.md) and requirements (./reqs/*.md) do NOT map 1-to-1:
- **Specs:** Organized for human understanding
- **Requirements:** Organized as testable flows (startup to shutdown)
- Example: ./specs/LOGGING.md scatters logging requirements across all ./reqs/ documents

**P1.1 (SCRIPT):** Prepare directories

**P1.2 (AI):** Generate requirements (prompt: WRITE_REQS.md)
- Read README.md, ./specs/*.md, list ./docs/*
- Write/rewrite all ./reqs/*.md files
- Tag each requirement with `$REQ_ID` (format: `$REQ_COMPONENT_NNN`)

**P1.3-8 (SCRIPT/AI):** Refinement loop (max 5 iterations):
- **P1.4** SCRIPT Signature before (script: compute-signature.py ./reqs/)
- **P1.5** SCRIPT Fix duplicate $REQ_IDs (script: fix-duplicate-req-ids.py)
- **P1.6** AI Run validation prompts IN PARALLEL (prompts: req-fix_testability.md, req-fix_completeness.md, req-fix_consistency.md, req-fix_req-ids.md)
- **P1.7** SCRIPT Signature after (script: compute-signature.py ./reqs/)
- **P1.8** SCRIPT Check convergence:
  - Converged (i.e. signature before and after are the same) -> P1.9
  - Not converged, iteration < 5 -> P1.4
  - Iteration >= 5 -> "Good enough", P1.9

**P1.9 (AI):** Order requirements by dependency (prompt: ORDER_REQS.md)
- Rename ./reqs/*.md with numeric prefixes (01_build.md, 02_startup.md, etc.)
- Order: build -> lifecycle -> core -> advanced (i.e. from most foundational to most specific)

**P1.10 (SCRIPT):** Done
- Print success, list ./reqs/*.md files
- Exit code 0

---

## Exit Conditions

**OK Success (Code 0):** Step P1.10 -> Proceed to P2 (code generation)

**NOTE README/Specs Modified:** Step P0.5 -> Review changes, ENTER or CTRL-C

**FAIL Error (Code 1):** System error -> Check ./reports/, fix, re-run
