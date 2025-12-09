Check if README documentation in `./README.md` and `./specs/` has quality issues.

---

## Purpose

Validate that documentation clearly describes what the software does with correct usage, without being pedantic about error handling.

**Philosophy:** READMEs should focus on what the software DOES, not exhaustively document every way it can fail.

---

## What to Check

### 1. Internal Contradictions

**Check:** Do READMEs contradict themselves?

**Examples:**
- README says "port defaults to 43143" in one section, "port is required" in another
- README says "starts immediately" in one place, "waits for confirmation" elsewhere
- Mutually exclusive behaviors described without clarifying when each applies

**Not contradictions:**
- Different scenarios (e.g., "with config file" vs "without config file")
- Sequential behaviors (e.g., "first X, then Y")
- Different aspects of same feature

### 2. Vague or Unobservable Specifications

**Check:** Are specifications too vague to implement or verify?

**Examples of problems:**
- "Handle errors appropriately" -- no indication what "appropriately" means
- "Secure connection" -- which protocol? which version? what validation?
- "Process requests efficiently" -- what does this mean in observable terms?
- "User-friendly interface" -- completely subjective

**Good examples (specific enough to implement):**
- "Accept connections on port 43143"
- "Use TLS 1.2 or higher for HTTPS"
- "Log each request to stdout"

**Note:** Statements like "accepts one directory argument" or "port number is required" are NOT vague - they clearly describe correct usage. Don't flag these.

### 3. Performance/Load Claims Without Observable Behavior

**Check:** Are there performance claims that can't be tested?

**Examples of problems:**
- "Handles 10,000 requests per second" -- hard to test reliably
- "Low latency response" -- subjective and environment-dependent
- "Fast startup time" -- relative, not observable
- "Scales to high traffic" -- load characteristics difficult to verify

**Good examples (observable behavior):**
- "Uses non-blocking I/O for all network operations"
- "Buffers in memory when logging falls behind"
- "Never blocks network I/O on disk writes"

**Key distinction:** Architecture/design decisions are testable (via code review), performance numbers are not.

---

## What NOT to Flag

**DO NOT flag as problems:**
- **Statements of correct usage** -- "Accepts one directory argument", "Port number is required", "Configuration file must be valid JSON" are all fine. READMEs don't need to specify what happens with every wrong input.
- **Error examples without exhaustive detail** -- If README says "show error if port in use" without specifying exact error message format, that's fine. We don't need exact error text specifications.
- **Happy path focus** -- If README documents what the software does with correct input but doesn't exhaustively document all error cases, that's acceptable. Focus on happy paths is good.
- **Absence of features** -- "Does not support UDP" is just documentation of what's not included; it's not a quality issue.
- **Build documentation** -- It's fine for READMEs to include build instructions, development prerequisites, or compilation steps. These won't generate requirements, but they're not quality problems.
- **Architecture/design decisions** -- These ARE testable via code-review tests (see 02_CODE-GEN.md and WRITE_TEST.md). Examples of testable architectural statements:
  - "Each concurrent request is handled on a separate thread" (testable by inspecting code for threading implementation)
  - "Single plugin instance serves all requests" (testable by inspecting code for singleton pattern)
  - "Uses non-blocking I/O for all network operations" (testable by inspecting code for async/await patterns)
  - Code-review tests read ./code/* and assert on implementation details. These requirements are NOT vague or untestable.

**The philosophy:** READMEs should clearly document what the software DOES with correct usage. They don't need to exhaustively specify every possible error condition, wrong input, or edge case.

---

## Your Task

1. Read `./README.md` and all files in `./specs/`
2. Check for the three categories of problems listed above
3. **If significant issues found:** Edit the files directly to fix them
4. **If no significant issues found:** Don't modify any files
5. After completing your work, describe what you did

**Important:** Do NOT just report problems -- FIX them by editing README.md and ./specs/*.md files.

**Focus on significant issues** -- ignore minor unclear wording; only fix clear problems.

**Don't be pedantic** -- if something describes correct usage clearly, don't demand error handling specifications.

---

## What to Report

After you've completed your edits (or determined no edits were needed), explain what you did:

**If you fixed issues:**
- List each file you modified
- For each modification, explain:
  - What the problem was (contradiction, vagueness, untestable claim)
  - What section/text you changed
  - How you fixed it

**If no issues found:**
- Simply state that README and specs documentation is clear and testable

**Example response:**
```
Modified ./specs/LIFECYCLE.md:
- Section "Error Handling" was vague ("handle errors appropriately")
- Changed to: "Log error to stderr and exit with code 1"
- This makes the error handling behavior testable

Modified ./specs/API.md:
- Found contradiction about port defaults
- Changed "Error Handling" section to match "Startup" section
- Now consistently documents that port defaults to 43143

No changes to README.md or other spec files -- they are clear and testable.
```
