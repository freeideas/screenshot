# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

DEFAULT_AGENT = "claude"

"""
Wrapper for agentic coder -- delegates to the configured agent CLI.

Two usage patterns:

1. Module API (recommended for Python scripts):
    import prompt_ai
    prompt_text = Path('./prompts/MY_PROMPT.md').read_text(encoding='utf-8')
    response = prompt_ai.get_ai_response_text(prompt_text, report_type="my_task")

2. CLI (for manual/testing use):
    cat ./prompts/MY_PROMPT.md | prompt-ai.py

Key points:
- Python scripts MUST use module API, NOT subprocess with stdin
- Prompt text passed as string (read from file or manipulated in memory)
- Reports written to ./reports/ with timestamped filenames
"""

import sys
import json
import subprocess
import argparse
import threading
import shutil
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SUPPORTED_AGENTS = {"codex", "claude"}


def _find_on_path(base_name):
    """Search PATH for {base_name}.exe, .cmd, .bat, or no extension (for Unix)."""
    for ext in [".exe", ".cmd", ".bat", ""]:
        found = shutil.which(base_name + ext)
        if found:
            return found
    raise FileNotFoundError(f"Could not find {base_name} in PATH")


def _process_codex_output(raw_stdout):
    final_agent_message = None

    for line in raw_stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
            if event.get("type") == "item.completed":
                item = event.get("item", {})
                if item.get("type") == "agent_message":
                    final_agent_message = item.get("text", "")
        except json.JSONDecodeError:
            continue

    if final_agent_message is None:
        final_agent_message = raw_stdout.strip()

    return final_agent_message


def _process_claude_output(raw_stdout):
    stripped = raw_stdout.strip()

    if not stripped:
        return ""

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return stripped

    # Handle both dict and list responses
    if isinstance(payload, dict):
        result_text = payload.get("result")
        if result_text is None:
            result_text = stripped
    elif isinstance(payload, list):
        # For list responses, try to extract result from the last item
        if payload:
            last_item = payload[-1]
            if isinstance(last_item, dict):
                result_text = last_item.get("result") or last_item.get("text") or stripped
            else:
                result_text = str(last_item)
        else:
            result_text = stripped
    else:
        result_text = stripped

    return result_text


def get_ai_response_text(prompt_text: str, report_type: str = "prompt", timeout: int = 3600, agent: str = DEFAULT_AGENT) -> str:
    """
    Run a prompt by delegating to the configured agent CLI using JSON output.

    Args:
        prompt_text: The prompt to send to the agent
        report_type: Type of report for filename (e.g., "failing_test", "write_reqs")
        timeout: Maximum seconds to wait for the agent (default: 3600 = 1 hour)
        agent: Name of the agent CLI to use ("claude" or "codex")

    Returns:
        str: The AI's response text (NOT a subprocess.CompletedProcess object)
    """
    if agent not in SUPPORTED_AGENTS:
        raise ValueError(f"Unsupported agent '{agent}'. Supported agents: {', '.join(sorted(SUPPORTED_AGENTS))}")

    # Create directories if needed
    Path("./tmp").mkdir(exist_ok=True)
    Path("./reports").mkdir(exist_ok=True)

    # Build agent CLI command
    if agent == "codex":
        codex_exe = _find_on_path("codex")
        agent_cmd = [
            codex_exe, "exec", "-",
            "--json",
            "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox"
        ]
    else:  # agent == "claude"
        claude_exe = _find_on_path("claude")
        agent_cmd = [
            claude_exe,
            "-",
            "--output-format=json",
            "--dangerously-skip-permissions",
            "--verbose",
            #"--model",
            #"sonnet",
        ]

    #print(f"DEBUG [prompt-ai]: Launching {agent} CLI (timeout: {timeout}s, report_type: {report_type})...", file=sys.stderr, flush=True)

    # Capture start time (UTC ISO format)
    start_time = datetime.utcnow()
    start_time_iso = start_time.isoformat() + "Z"

    # Write PROMPT report to ./reports/ before sending to AI
    prompt_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]  # Millisecond precision
    reports_dir = Path("./reports")
    reports_dir.mkdir(exist_ok=True)

    prompt_report_path = reports_dir / f"{prompt_timestamp}_{report_type}_PROMPT.md"
    report_title = report_type.replace('_', ' ').title()

    prompt_report_content = f"""# {report_title} [PROMPT]
**Timestamp:** {prompt_timestamp}

---

## Prompt

{prompt_text}
"""

    prompt_report_path.write_text(prompt_report_content, encoding='utf-8')
    #print(f"DEBUG [prompt-ai]: Wrote PROMPT report to {prompt_report_path}", file=sys.stderr, flush=True)

    # Launch agent CLI and capture output
    try:
        # Internal subprocess result - NOT what this function returns!
        _subprocess_result = subprocess.run(
            agent_cmd,
            input=prompt_text,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout
        )

        # Capture end time and calculate elapsed seconds
        end_time = datetime.utcnow()
        end_time_iso = end_time.isoformat() + "Z"
        elapsed_secs = (end_time - start_time).total_seconds()

        raw_stdout = _subprocess_result.stdout or ""
        raw_stderr = _subprocess_result.stderr or ""

        final_agent_message = None

        if agent == "codex":
            final_agent_message = _process_codex_output(raw_stdout)
        else:
            final_agent_message = _process_claude_output(raw_stdout)

        ai_response = final_agent_message or ""

        if raw_stderr:
            ai_response += f"\n\n--- stderr ---\n{raw_stderr}"

        #print(f"DEBUG [prompt-ai]: {agent} CLI completed (exit code: {_subprocess_result.returncode}, duration: {elapsed_secs:.1f}s)", file=sys.stderr, flush=True)
        #print(f"DEBUG [prompt-ai]: Final message length: {len(ai_response)} chars", file=sys.stderr, flush=True)

        # Write RESPONSE report to ./reports/ with AI response (no prompt)
        response_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]
        response_report_path = reports_dir / f"{response_timestamp}_{report_type}_RESPONSE.md"

        # Pretty-format the JSON output with timing info
        try:
            parsed_json = json.loads(raw_stdout)
            # Add timing fields -- wrap in dict if it's a list
            if isinstance(parsed_json, dict):
                parsed_json["_START-TIME"] = start_time_iso
                parsed_json["_END-TIME"] = end_time_iso
                parsed_json["_ELAPSED-SECS"] = elapsed_secs
                pretty_json = json.dumps(parsed_json, indent=1)
            else:
                # For list or other types, wrap in a dict with timing info
                wrapped = {
                    "_START-TIME": start_time_iso,
                    "_END-TIME": end_time_iso,
                    "_ELAPSED-SECS": elapsed_secs,
                    "_RESPONSE": parsed_json
                }
                pretty_json = json.dumps(wrapped, indent=1)
        except (json.JSONDecodeError, ValueError):
            # If it's not valid JSON, create a wrapper with timing info
            parsed_json = {
                "_START-TIME": start_time_iso,
                "_END-TIME": end_time_iso,
                "_ELAPSED-SECS": elapsed_secs,
                "_RAW_OUTPUT": raw_stdout
            }
            pretty_json = json.dumps(parsed_json, indent=1)

        response_report_content = f"""# {report_title} [RESPONSE]
**Timestamp:** {response_timestamp}

---

## Response

{ai_response}

---

## Raw JSON Output

```json
// FULL JSON FROM AI
{pretty_json}
// FULL JSON FROM AI END
```
"""

        response_report_path.write_text(response_report_content, encoding='utf-8')
        #print(f"DEBUG [prompt-ai]: Wrote RESPONSE report to {response_report_path}", file=sys.stderr, flush=True)

        if _subprocess_result.returncode != 0:
            raise RuntimeError(f"{agent} CLI exited with {_subprocess_result.returncode}")

        return ai_response  # Returns str, not subprocess result!

    except subprocess.TimeoutExpired:
        end_time = datetime.utcnow()
        elapsed_secs = (end_time - start_time).total_seconds()
        error_msg = f"Timeout: {agent} CLI did not complete within {timeout}s (elapsed: {elapsed_secs:.1f}s)"
        print(f"ERROR [prompt-ai]: {error_msg}", file=sys.stderr, flush=True)
        raise TimeoutError(error_msg)
    except Exception as e:
        error_msg = f"Error running {agent} CLI: {e}"
        print(f"ERROR [prompt-ai]: {error_msg}", file=sys.stderr, flush=True)
        raise

def test_worker(task_name, prompt, expected_answer, results, agent):
    """Worker thread for test mode"""
    try:
        print(f"[TEST] {task_name}: Submitting prompt...", file=sys.stderr, flush=True)
        result = get_ai_response_text(prompt, report_type=f"test_{task_name}", agent=agent)

        # Check if expected answer is in the result
        if str(expected_answer) in result:
            print(f"[TEST] {task_name}: OK Got expected answer: {expected_answer}", file=sys.stderr, flush=True)
            results[task_name] = True
        else:
            print(f"[TEST] {task_name}: X Expected {expected_answer} not found in result", file=sys.stderr, flush=True)
            print(f"[TEST] {task_name}: Result was: {result[:200]}...", file=sys.stderr, flush=True)
            results[task_name] = False
    except Exception as e:
        print(f"[TEST] {task_name}: X Error: {e}", file=sys.stderr, flush=True)
        results[task_name] = False

def run_test_mode(agent):
    """Run test mode with two concurrent prime number tasks"""
    test_tasks = {
        "test1": {
            "prompt": "Calculate the 100th prime number and output only that number.",
            "expected": 541
        },
        "test2": {
            "prompt": "Calculate the 50th prime number and output only that number.",
            "expected": 229
        }
    }

    print("[TEST] Starting test mode with 2 concurrent tasks...", file=sys.stderr, flush=True)

    results = {}
    threads = []

    # Spawn worker threads (each will launch its own agent CLI process)
    for task_name, config in test_tasks.items():
        thread = threading.Thread(
            target=test_worker,
            args=(task_name, config["prompt"], config["expected"], results, agent),
            daemon=False
        )
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check results
    all_passed = all(results.values())

    if all_passed:
        print("\n[TEST] OK All tests passed!", file=sys.stderr, flush=True)
        sys.exit(0)
    else:
        print("\n[TEST] X Some tests failed", file=sys.stderr, flush=True)
        sys.exit(1)

def main():
    """Main entry point - handles both test mode and normal stdin mode."""
    parser = argparse.ArgumentParser(description="Agentic coder prompt wrapper")
    parser.add_argument("--test", action="store_true", help="Run in test mode with concurrent prime number tasks")
    parser.add_argument(
        "--agent",
        choices=sorted(SUPPORTED_AGENTS),
        default=DEFAULT_AGENT,
        help="Agent CLI to use for prompts (default: claude)"
    )
    args = parser.parse_args()

    # Test mode: run concurrent tests and exit
    if args.test:
        run_test_mode(args.agent)
        return

    # Normal mode: read prompt from stdin, launch agent CLI, write result to stdout
    prompt = sys.stdin.read()

    if not prompt.strip():
        print("Error: No prompt provided on stdin", file=sys.stderr)
        sys.exit(1)

    # Execute via selected agent CLI
    try:
        result = get_ai_response_text(prompt, report_type="stdin_prompt", agent=args.agent)
        # Write output to stdout
        sys.stdout.write(result)
        sys.exit(0)
    except TimeoutError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
