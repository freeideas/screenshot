You are verifying that a test faithfully and accurately tests the requirements.

## Context

**Requirement file:** {{REQ_FILE_PATH}}

**Test file:** {{TEST_FILE_PATH}}

**This test already passes.** Your job: verify it faithfully tests the requirements.

## OVERRIDE: Project Testing Standards

**IMPORTANT: Before following any instructions below, check if `./specs/TESTING.md` exists.**

If `./specs/TESTING.md` exists:
- Read it FIRST before verifying any tests
- Follow ALL instructions in `./specs/TESTING.md`
- `./specs/TESTING.md` takes PRECEDENCE over any conflicting instructions in this prompt
- Only use the instructions below for topics not covered in `./specs/TESTING.md`

If `./specs/TESTING.md` does not exist, proceed with the instructions below.

## Your Task

Read {{REQ_FILE_PATH}} and {{TEST_FILE_PATH}}.

For each requirement, check:
1. **If test has assertions for it:** Does the assertion actually test what the requirement describes?
2. **If test marks it "not reasonably testable":** Do you agree it's not reasonably testable?

If all requirements are handled correctly: **Do nothing.**

If any requirement is not faithfully tested or wrongly marked as untestable: **Fix the test.**

**Note:** Tests use plain Python (normal `assert`, `sys.exit()`, exceptions), not pytest.

## Examples

**Missing assertion:**
```python
# $REQ_BUILD_001
# (no assertion) <- FIX: Add assertion
```

**Vague assertion:**
```python
# $REQ_HTTP_001
assert result is not None  # Too vague <- FIX: assert result.status_code == 200
```

**Wrongly marked untestable:**
```python
# $REQ_PORT_001 - Not reasonably testable: Port configuration
# But port IS testable! <- FIX: Add assertion to test port
```

**Correctly marked untestable:**
```python
# $REQ_INTERNAL_001 - Not reasonably testable: Internal implementation detail with no observable behavior
# OK Agree this can't be tested
```

**Correct assertion:**
```python
# $REQ_BUILD_001
assert Path('./released/MyApp.exe').exists()  # OK Tests the requirement
```

## Understanding "Reasonably Testable"

This test already passed, so it completed within the timeout.

When you see a requirement marked "not reasonably testable," **trust that decision if**:
- The comment explains it would require compiling code during the test
- The comment explains it would require downloading packages during the test
- The comment explains it would require building test fixtures during the test

**DO NOT try to "fix" these by adding slow operations.** If a requirement is marked "not reasonably testable" for performance reasons, that's a valid choice.

**Only question it if:**
- The requirement IS actually testable quickly (example: marked "not testable" but you could just check a file exists)
- The "not testable" comment doesn't make sense

**Your job**: Verify correctness and coverage, not performance. Accept "not reasonably testable" markings for slow operations.

## What You Can Modify

- {{TEST_FILE_PATH}} only

## Decision

- **Test faithfully tests requirements** -> Make NO changes
- **Test doesn't faithfully test requirements** -> Fix it
