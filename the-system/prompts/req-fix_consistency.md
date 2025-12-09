Check if requirements in `./reqs/` accurately reflect `./README.md` and `./specs/*.md`.

---

## THE SEVEN RULES FOR REQUIREMENTS

1. **Complete Coverage** -- Every reasonably testable behavior in `./README.md` or `./specs/*.md` must have a $REQ_ID
2. **No Invention** -- Only requirements from `./README.md` or `./specs/*.md` are allowed (./docs/ is NEVER a valid source)
3. **No Overspecification** -- Requirements must not be more specific than `./README.md` or `./specs/*.md`
4. **Tell Stories** -- Flows go from start to shutdown (complete use-case scenarios)
5. **Source Attribution** -- Every $REQ_ID cites ONLY: `**Source:** ./README.md (Section: "Name")` or `**Source:** ./specs/FILE.md (Section: "Name")`
6. **Unique IDs** -- Each $REQ_ID appears exactly once. Format: `$REQ_` followed by letters/digits/underscores/hyphens (e.g., $REQ_STARTUP_001)
7. **Reasonably Testable** -- Requirements must have observable behavior that can be verified

---

## What Is Inaccurate?

A requirement is inaccurate when it misrepresents what `./README.md` or `./specs/*.md` says.

**Common inaccuracies:**

### 1. Inverting Behavior

**README:** "Port defaults to 43143 if not provided"
**Inaccurate req:** "Must display error and exit if port not provided"
**Problem:** Opposite of what README says

### 2. Misinterpreting Examples as Requirements

**README:** "For example, if buffer fills memory, the process will crash with OOM instead of blocking connections"
**Inaccurate req:** "Must crash with OOM when buffer fills"
**Problem:** Example was illustrating non-blocking behavior, not requiring OOM crash

### 3. Adding Error Handling Not in README

**README:** "Accepts one directory argument"
**Inaccurate req:** "Must exit with error code 1 if multiple directories provided"
**Problem:** Added error handling not stated in README -- focus on happy path unless README explicitly documents error behavior

### 4. Requirements That Contradict Each Other

When two requirements can't both be true, at least one misrepresents the README:

**Req A:** "Must start immediately when launched"
**Req B:** "Must wait for user confirmation before starting"
**Problem:** Both can't be true -- check README to see which is correct

Contradictions between requirements are evidence of misinterpretation.

---

## Your Task

1. Read `./README.md` and all files in `./specs/`
2. Read all flow files in `./reqs/`
3. For each requirement, verify it accurately reflects the cited README source
4. Look for contradictions between requirements as symptoms of inaccuracy
5. Fix requirements to match README documentation
6. **Focus on significant inaccuracies** -- ignore minor wording differences; only fix clear misrepresentations
n**CRITICAL: Avoid trivial changes that trigger unnecessary regeneration:**
- Do NOT reword requirements that are already correct (different wording is fine if meaning matches)
- Do NOT make cosmetic changes (formatting, spacing, capitalization)
- Do NOT "improve clarity" of requirements that are already clear
- ONLY modify when there's an actual error: wrong behavior, contradiction, or misrepresentation
- When in doubt, leave it unchanged

---

## Output Format

**Do NOT create any report files.** Just respond with a simple list.

**If significant issues found:** For each change, list:
- File: (which file was edited)
- Before: (the inaccurate requirement text, including $REQ_ID)
- After: (the corrected requirement text)
- Why: (how it misrepresented README)

**If no significant issues found:** State that requirements accurately reflect README documentation.
