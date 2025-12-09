# Project Philosophy

This document defines the core principles that guide all work in this project.

## Minimal Viable Project

This is a **minimal viable project**. We build only what is explicitly required:

- **NO "nice to have" features** -- if it's not required, don't build it
- **NO undocumented edge cases** -- if it's not specified, ignore it
- **NO error handling** -- except where explicitly required
- **NO gold plating** -- implement exactly what's written, nothing more
- **NO historical baggage** -- documentation reflects current desired state only

## Requirements Are the Design

**Requirements specify WHAT, and HOW only when documentation specifies HOW** -- they are the only design documents.

Requirements should specify:
- What the system must do (functional behavior)
- What constraints must be met (performance, platform, format)
- What artifacts must exist after build
- What technologies/approaches to use **only when explicitly mandated**

**If documentation doesn't specify technical details, leave them unspecified.** Implementation choices not mandated by requirements are left to the implementer's discretion and can change freely.

**Example:**
- Documentation says "web UI" -> Requirement: "MUST provide web UI accessible via browser"
- Implementer chooses React, hits deployment issues, switches to Vue
- Tests still pass (they verify web UI works, not which framework)
- No requirement changes needed

There is no intermediate specification layer between requirements and code.

## Core Philosophy: Ruthless Simplification

**Complexity is a bug. Fix it by deletion.**

All implementation artifacts -- code and tests -- are disposable and have no inherent value. Every line is a liability that must justify its existence.

**The universal rules:**
- **Delete anything not serving requirements** -- if it doesn't implement a requirement, remove it
- **Simplify immediately** -- don't wait, don't ask permission
- **Rewrite liberally** -- if you find a simpler approach, rip out the old implementation completely
- **No "just in case"** -- don't keep dead code, unused functions, or speculative features
- **Abstractions must pay rent** -- if an abstraction doesn't eliminate significant duplication, inline it
- **Clarity beats cleverness** -- replace clever code with obvious code

### Code Organization: Requirement-Focused Modularity

**Prefer many focused files over few multipurpose files.**

When implementing requirements, lean toward:
- **Separate files for distinct requirements** -- Each file serves a specific purpose tied to specific requirements
- **Clear boundaries** -- Files organized by what they accomplish, not just what data they share
- **Duplication over coupling** -- Some repeated patterns are better than tight coupling between unrelated requirements
- **Understandable in isolation** -- Each file should make sense without reading the entire codebase

This is not about being pedantic -- it's about clarity. A codebase with many focused files, each serving specific requirements, is often clearer than one with a few large files trying to do everything. When in doubt, split by requirement boundaries rather than consolidating by technical similarities.

### Tests
- Test checks behavior. If part of a test is not supported by the requirements, delete the assertion or entire test
- Keep runtime short (<1 minute when feasible); if a test file runs longer, break it into focused smaller tests
- Test is flaky, slow (>5s), or has reliability issues? Rewrite from scratch
- Complex test setup? Something is wrong. Rewrite the code and/or the test.
- Requirements changed? Rewrite tests to match -- don't try to adapt old tests
- Complex shared fixtures? Delete them -- prefer simple duplication over complex abstraction
- Mock only what you must -- prefer real implementations

### Testing: Happy Path Only

**Test success, not failure.**

- Test that correct usage works correctly
- Do NOT test what happens when you sabotage the system
- Do NOT verify error messages unless requirements explicitly mandate them
- If requirements say "must X", test that X works -- don't test what happens when X is prevented

**Examples of tests to NOT write:**
- "Missing plugin file causes error" -- sabotage test
- "Invalid DLL is rejected" -- sabotage test
- "Corrupted input fails gracefully" -- sabotage test

**Examples of tests TO write:**
- "Valid plugin loads successfully" -- happy path
- "Server starts and accepts requests" -- happy path
- "SOAP operations return correct responses" -- happy path
