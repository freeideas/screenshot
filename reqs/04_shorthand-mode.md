# Shorthand Mode Flow

**Source:** ./README.md

Capture a screenshot using shorthand syntax where the selection type is auto-detected.

## $REQ_SHORT_001: Auto-Detect Title When Quoted
**Source:** ./README.md (Section: "Shorthand (no flag)")

When the first argument doesn't start with `--` and starts with a quote (`"`), match it as a window title.

## $REQ_SHORT_002: Auto-Detect ID or PID When Unquoted
**Source:** ./README.md (Section: "Shorthand (no flag)")

When the first argument doesn't start with `--` and doesn't start with a quote, match it as a window ID or process ID (whichever matches first). If a PID has multiple windows, one is captured.

## $REQ_SHORT_003: Output Success Message
**Source:** ./README.md (Section: "Arguments")

When a screenshot is successfully captured, output `Wrote [filepath]` before exiting.
