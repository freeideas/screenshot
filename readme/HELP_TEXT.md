# Help Text and Window List

## Overview

When `screenshot.exe` is run without arguments, it displays help text followed by a list of all currently open windows.

## Help Mode Behavior

Running without arguments:
```bash
screenshot.exe
```

Outputs:
1. **Usage examples** showing the three capture modes
2. **Instruction text** explaining the no-args behavior
3. **Window list header** labeling the columns
4. **Window list** with one line per window

## Output Format

```
Usage:
  screenshot.exe --title "window title" [output.png|directory|]
  screenshot.exe --pid <process-id> [output.png|directory|]
  screenshot.exe --id <window-id> [output.png|directory|]

Output path is optional:
  - Specify .png file: saves to that exact location
  - Specify directory: saves with timestamped filename (YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png)
  - Omit output: saves to current directory with timestamped filename

Run without arguments to see list of windows with IDs and PIDs.

Currently open windows (id,pid,title):
<window-id>\t<pid>\t"window title"
<window-id>\t<pid>\t"window title"
...
```

### Field Descriptions

**Window list format:** `<window-id>\t<pid>\t"window title"`

- `<window-id>` -- Alphanumeric identifier for the window (e.g., `9007C`, `50650`)
- `<pid>` -- Numeric process ID (e.g., `8704`, `7580`)
- `"window title"` -- Exact window title in double quotes
- Fields separated by tab characters (`\t`)

## Example Output

```
Usage:
  screenshot.exe --title "window title" [output.png|directory|]
  screenshot.exe --pid <process-id> [output.png|directory|]
  screenshot.exe --id <window-id> [output.png|directory|]

Output path is optional:
  - Specify .png file: saves to that exact location
  - Specify directory: saves with timestamped filename (YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png)
  - Omit output: saves to current directory with timestamped filename

Run without arguments to see list of windows with IDs and PIDs.

Currently open windows (id,pid,title):
9007C	8704	"*new 1 - Notepad++"
50650	7580	"C:\acex\prjx\screenshot - File Explorer"
1010E	7580	"Program Manager"
504FC	12980	"Settings"
40322	7636	"Settings"
203E8	12196	"test-screenshot.py - UmniCli - Visual Studio Code [Administrator]"
208F0	12196	"TESTING.md - screenshot - Visual Studio Code [Administrator]"
```

## Exit Code

Help mode exits with status code `0` (success).

## Capture Mode Output

When a screenshot is successfully captured, the tool outputs:
```
Wrote [filepath]
```

For example:
- `Wrote ./output.png` -- when explicit file path is specified
- `Wrote ./screenshots/2025-11-10-23-30-22-293532_screenshot.png` -- when directory is specified
- `Wrote ./2025-11-10-23-30-22-293532_screenshot.png` -- when no output path is specified

## Use Cases

1. **Discover available windows** -- See what windows can be captured
2. **Get window IDs** -- Find the ID for `--id` flag
3. **Get process IDs** -- Find the PID for `--pid` flag
4. **Get exact titles** -- Copy/paste exact title text for `--title` flag
5. **Verify window visibility** -- Confirm a window is listed and capturable

## Window ID Format

Window IDs are hexadecimal values without `0x` prefix:
- `9007C` (5 characters)
- `50650` (5 characters)
- `1010E` (5 characters)
- `504FC` (5 characters)

The length may vary, but all IDs are alphanumeric (0-9, A-F).

## Process IDs

Multiple windows can share the same PID (e.g., multiple tabs/windows from same application).

In the example above, PID `7580` appears twice (File Explorer and Program Manager), and PID `12196` appears twice (two VS Code windows).
