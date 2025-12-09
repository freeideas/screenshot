# Why This Works

Most AI coding approaches fail for real-world business-oriented software. Here's why -- and how this approach succeeds.

---

## The Problem with "Prompt and Pray"

Consider building software that requires 1000 small steps from zero to fully tested and working. In reality there might be far more, but let's keep it simple.

Assume the AI has a 99% chance of getting each step right. Sounds good, right?

**The math says otherwise:**

- Probability of all 1000 steps correct: 0.99^1000 ≈ 0.00004%
- That's less than 1 in 20,000

Even with 99% accuracy per step, success is nearly impossible.

**It gets worse.** Errors compound. If, for example, step 12 goes wrong, every step after that builds on that mistake. By step 1000, the code may be unfixable without a complete rewrite.

---

## How This System Avoids the Trap

**Verify each step before moving to the next.**

After every step, the step is verified -- *proven correct* wherever possible -- before proceeding.

And this verification is done by software, not by the AI. The AI cannot declare "I'm done" until it has been marched through all 1000 steps, each one passing verification.

No compounding errors. No drift. No prayer required.

---

## Requirements: The Foundation of Verification

Everything in `README.md` and `specs/` documents gets transformed into dozens or hundreds of **requirements**. Each requirement is a testable assertion with a unique ID:

```
REQ-CLI-001: When launched with no arguments, a help screen displays
REQ-CLI-002: The --version flag prints the current version number
REQ-AUTH-001: Invalid credentials return a 401 status code
```

This structure enables something powerful: **programmatic verification that every requirement is tested** -- no fuzzy AI judgment needed.

---

## The Traceability Database

A database tracks the complete lineage of each requirement:

| Requirement ID | Specification Source | Test File            | Implementation     |
|----------------|----------------------|----------------------|--------------------|
| REQ-CLI-001    | specs/cli.md:12      | tests/test_cli.py:45 | src/cli/main.py:23 |
| REQ-CLI-002    | specs/cli.md:18      | tests/test_cli.py:67 | src/cli/main.py:31 |

The AI can query this database to instantly see:
- Where a requirement came from
- What test verifies it
- What code implements it

So, just like a human developer, **the AI doesn't need to read or understand the entire system** to work on a few requirements.

When tasked with fixing REQ-CLI-001, the AI queries the database and receives only:
- The specification text for that requirement
- The test file that verifies it
- The implementation code

No wading through thousands of lines of unrelated code. No hoping the AI "remembers" some detail from earlier in a massive context window.

**Focused context = clear thinking = correct software.**
