## Environment

- **GitHub**: Already logged in and authenticated
- **Project Repositories**: All project repos are located under `/home/ace/prjx`
- **Git Branch Naming**: Always use "main" instead of "master" for default branch names, as some people find "master" offensive

## Python Development

**IMPORTANT: NEVER run Python scripts with `python script.py`. ALWAYS run them with uv:**
- [OK] CORRECT: `uv run --script ./scripts/my_script.py`
- [X] WRONG: `python scripts/my_script.py` or `python3 scripts/my_script.py`

**All Python scripts MUST have this shebang as the first line:**
```python
#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
    # List PyPI packages here
]
# ///
```

**Key points:**
- Scripts can use ANY PyPI package without pre-installation - just list it in dependencies
- The script metadata block (`# /// script`) declares dependencies inline
- Use `uv run` to execute Python scripts with automatic dependency management

**When creating new Python scripts:**
1. ALWAYS start with the `#!/usr/bin/env uvrun` shebang
2. Add the script metadata block with dependencies
3. Make the script executable: `chmod +x script.py`
4. Run it directly: `./script.py` NOT `python script.py`

**Note**: If you need any standard development tools that are missing, feel free to install them.

**ALWAYS use ./tmp directory for temporary scripts:**

```bash
# Create tmp directory if it doesn't exist
mkdir -p ./tmp
# Run tests with absolute or relative paths (NO cd!)
uv run --script ./tmp/test_script.py
# Or specify output paths:
uv run --script script.py --output ./tmp/results.json

# Bad - Never create temporary files in:
# - Git repository roots (except in tmp/, which should be added to .gitignore)
# - Project source directories
# - Any version-controlled directory (except tmp/, which should be added to .gitignore)
```

Python: Always use `./tmp` directory (create it with `os.makedirs('./tmp', exist_ok=True)` if needed).

## Important Instructions

## Unicode and Subprocess Encoding

**Use Unicode characters freely (✓, ✗, •, etc.) for better readability in output and reports.**

**CRITICAL: All Python subprocess calls MUST explicitly specify `encoding='utf-8'` on Windows, but even on MacOS and Linux so they will be cross-platform ready:**

```python
# ❌ WRONG - Windows defaults to cp1252, mangles Unicode
subprocess.run(cmd, text=True)
subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE)

# ✅ CORRECT - Explicit UTF-8 encoding
subprocess.run(cmd, text=True, encoding='utf-8')
subprocess.Popen(cmd, text=True, encoding='utf-8', stdout=subprocess.PIPE)
```

**Why:** On Windows, `text=True` without explicit `encoding='utf-8'` defaults to cp1252 encoding. This causes UTF-8 characters (like ✓ and ✗) to be misread and appear as garbage characters (âœ") in captured output and reports.

**Always add `encoding='utf-8'` when using:**
- `subprocess.run(..., text=True)`
- `subprocess.Popen(..., text=True)`
- `subprocess.check_output(..., text=True)`
- Any subprocess call with `text=True` or `universal_newlines=True`

## Cross Platform
- We try to write everything in the most Windows and Linux -compatible way
- We often name shell scripts with .bat and binary executables with .exe even on Linux devices, because Linux doesn't care, but Windows does.

## Output Redirection on Windows

**NEVER pipe output to `nul` in Git Bash:**
- ❌ WRONG: `command > nul` or `command 2> nul`
- ✅ RIGHT: `command > /dev/null` or `command 2> /dev/null`

**Why:** In Git Bash, `> nul` creates an actual file named "nul" instead of discarding output. This file is nearly impossible to delete because "nul" is a reserved Windows device name. Use `/dev/null` which Git Bash handles correctly.

## Windows Process Signal Handling

**CRITICAL: Never use `os.kill(pid, signal.CTRL_C_EVENT)` or `signal.CTRL_C_EVENT` in Python tests on Windows.**

On Windows, `CTRL_C_EVENT` is broadcast to the entire console process group, including the test runner itself. This will kill your test process along with the target process.

**Instead, use HTTP shutdown endpoints when available:**
```python
# ❌ WRONG - Kills the test runner too!
os.kill(proc.pid, signal.CTRL_C_EVENT)

# ✅ CORRECT - Use HTTP shutdown endpoint
import urllib.request
req = urllib.request.Request(f"http://127.0.0.1:{port}/shutdown", method='POST')
urllib.request.urlopen(req, timeout=5)
```

**Why this happens:** Windows doesn't have Unix-style per-process signals. `CTRL_C_EVENT` is sent to all processes attached to the same console, which includes Python test scripts running the subprocess.
