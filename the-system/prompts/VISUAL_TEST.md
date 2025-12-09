You are performing visual verification of a screenshot.

---

## Your Task

**Image file:** {IMAGE_FILE}

**Expected description:** {DESCRIPTION}

**Unique ID:** {UID}

---

## Instructions

1. **Examine the screenshot** at `{IMAGE_FILE}`

2. **Compare against the description:**
   - Does the screenshot visually match what is described?
   - Look for key visual elements mentioned in the description
   - Consider overall appearance, UI elements, colors, text, layout

3. **Make your decision:**

   **If the screenshot MATCHES the description:**
   - Write a file to `./tmp/YES_{UID}.md`
   - Content should briefly explain why it matches (2-3 sentences)

   **If the screenshot does NOT MATCH the description:**
   - Write a file to `./tmp/NO_{UID}.md`
   - Content should briefly explain why it does not match (2-3 sentences)

---

## Important Notes

- You MUST write exactly ONE file: either `./tmp/YES_{UID}.md` or `./tmp/NO_{UID}.md`
- Be reasonable in your assessment -- minor variations are acceptable
- Focus on whether the screenshot plausibly shows what is described
- Do not create any other files

---

## Examples

### Example 1: Match

**Description:** "A Windows command prompt with black background"

**Screenshot shows:** Black terminal window with white text, Windows cmd.exe title bar

**Action:** Write `./tmp/YES_{UID}.md` with content:
```
The screenshot shows a Windows command prompt window with the characteristic black background and white text. The title bar displays "cmd.exe" confirming this is the Windows Command Prompt.
```

### Example 2: No Match

**Description:** "Windows Notepad application"

**Screenshot shows:** Web browser displaying Google

**Action:** Write `./tmp/NO_{UID}.md` with content:
```
The screenshot shows a web browser (appears to be Chrome) displaying Google's homepage. This does not match the expected Windows Notepad application.
```

---

Begin your visual inspection now.
