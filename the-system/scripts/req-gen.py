# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Requirements Generation Phase (P0-P1)

This script handles:
- P0: README/Specs Quality Check
- P1: Requirements Generation with iterative refinement

Exit codes:
  0 - Success (requirements generated)
  1 - Error
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import shutil
import threading
import importlib.util
from pathlib import Path
from datetime import datetime

# Import sibling modules (handle hyphenated filenames)
SCRIPT_DIR = Path(__file__).parent


def import_script(script_name):
    """Import a script module by filename (handles hyphens)."""
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import required modules
compute_signature = import_script('compute-signature')
fix_duplicate_req_ids = import_script('fix-duplicate-req-ids')
prompt_ai = import_script('prompt-ai')


def print_section(title):
    """Print a formatted section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print()


def prepare_workspace():
    """P0.1: Prepare workspace (clean reports, create directories)."""
    print_section("P0.1: Preparing Workspace")

    # Create necessary directories
    for directory in ['./reqs', './reports', './tmp']:
        Path(directory).mkdir(exist_ok=True)
        print(f"OK Directory ready: {directory}")

    print()


def take_signature(paths):
    """Helper to compute signature for given paths."""
    return compute_signature.compute_signature(paths)


def run_ai_prompt(prompt_path, report_type, timeout=600, model=None):
    """Helper to run an AI prompt and return the response."""
    print(f"  Running prompt: {prompt_path}")

    # Read prompt file
    prompt_text = Path(prompt_path).read_text(encoding='utf-8')

    # Determine agent and model
    agent = os.environ.get('PROMPT_AGENTIC_AGENT', 'claude')
    if model is None:
        model = os.environ.get('PROMPT_AGENTIC_MODEL', 'sonnet')

    # Set model in environment for prompt_agentic_coder
    os.environ['PROMPT_AGENTIC_MODEL'] = model

    # Run the prompt
    response = prompt_ai.get_ai_response_text(
        prompt_text,
        report_type=report_type,
        timeout=timeout,
        agent=agent
    )

    return response


def phase_0_quality_check():
    """
    P0: README/Specs Quality Check

    Returns: True if successful, False if should exit
    """
    print_section("PHASE 0: README/SPECS QUALITY CHECK")

    # P0.2: Take signature BEFORE
    print("P0.2: Computing signature BEFORE quality check...")
    signature_before = take_signature(['README.md', './specs'])
    print(f"  Signature BEFORE: {signature_before[:16]}...")
    print()

    # P0.25: Backup README and specs to ./tmp/
    print("P0.25: Creating timestamped backup of README and specs...")
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]  # Millisecond precision
    project_root = Path.cwd()
    backup_dir = project_root / 'tmp' / f'backup-readme-specs-{timestamp}'
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup README.md
    if (project_root / 'README.md').exists():
        shutil.copy2(project_root / 'README.md', backup_dir / 'README.md')

    # Backup specs directory
    specs_dir = project_root / 'specs'
    if specs_dir.exists():
        backup_specs = backup_dir / 'specs'
        shutil.copytree(specs_dir, backup_specs, dirs_exist_ok=True)

    print(f"  Backed up to: {backup_dir.relative_to(project_root)}")
    print()

    # P0.3: AI fix quality issues
    print("P0.3: AI checking README/specs quality...")
    prompt_path = SCRIPT_DIR.parent / 'prompts' / 'FIX_README-SPECS.md'

    if not prompt_path.exists():
        print(f"  Warning: Prompt not found: {prompt_path}")
        print(f"  Skipping quality check")
        return True

    try:
        response = run_ai_prompt(
            prompt_path,
            report_type='readme_specs_quality',
            timeout=900  # 15 minutes
        )
        print(f"  AI completed quality check")
        print()
    except Exception as e:
        print(f"  Error running quality check: {e}", file=sys.stderr)
        return False

    # P0.4: Take signature AFTER
    print("P0.4: Computing signature AFTER quality check...")
    signature_after = take_signature(['README.md', './specs'])
    print(f"  Signature AFTER: {signature_after[:16]}...")
    print()

    # P0.5: Check if AI made changes
    if signature_before != signature_after:
        print("P0.5: AI made changes to README.md and/or ./specs/")
        print()
        print("=" * 70)
        print("*** REVIEW REQUIRED ***")
        print("=" * 70)
        print()
        print("The AI has modified your README.md and/or specs/ files.")
        print()
        print("Please review the changes before continuing:")
        print("  - Press ENTER to accept these changes and continue")
        print("  - Press CTRL-C to abort and revise manually")
        print()
        print("=" * 70)
        sys.stdout.flush()  # Force output to appear immediately

        try:
            user_input = input("Your choice (press ENTER to continue): ")
            print()
            print("Continuing with AI changes...")
            print()
        except KeyboardInterrupt:
            print()
            print()
            print("Aborted by user. Please revise documentation and re-run.")
            return False
    else:
        print("P0.5: No changes made to README.md or ./specs/")
        print()

    return True


def phase_1_requirements_generation():
    """
    P1: Requirements Generation

    Returns: True if successful, False on error
    """
    print_section("PHASE 1: REQUIREMENTS GENERATION")

    # P1.1: Prepare directories
    print("P1.1: Preparing requirements directory...")
    reqs_dir = Path('./reqs')
    reqs_dir.mkdir(exist_ok=True)
    print(f"  OK Directory ready: ./reqs/")
    print()

    # P1.2: AI generate requirements
    print("P1.2: AI generating requirements...")
    prompt_path = SCRIPT_DIR.parent / 'prompts' / 'WRITE_REQS.md'

    if not prompt_path.exists():
        print(f"  Error: Prompt not found: {prompt_path}", file=sys.stderr)
        return False

    try:
        response = run_ai_prompt(
            prompt_path,
            report_type='write_reqs',
            timeout=1800  # 30 minutes
        )
        print(f"  OK AI generated requirements")
        print()
    except Exception as e:
        print(f"  Error generating requirements: {e}", file=sys.stderr)
        return False

    # P1.3-8: Refinement loop
    print("P1.3: Starting refinement loop (max 5 iterations)...")
    print()

    max_iterations = int(os.environ.get('MAX_REQ_ITERATIONS', '5'))

    for iteration in range(1, max_iterations + 1):
        print(f"  Iteration {iteration}/{max_iterations}")

        # P1.4: Signature before
        sig_before = take_signature(['./reqs'])
        print(f"    Signature BEFORE: {sig_before[:16]}...")

        # P1.5: Fix duplicate $REQ_IDs
        print(f"    Fixing duplicate $REQ_IDs...")
        try:
            fixes = fix_duplicate_req_ids.scan_and_fix_duplicates()
            if fixes > 0:
                print(f"    OK Fixed {fixes} duplicate(s)")
            else:
                print(f"    OK No duplicates found")
        except Exception as e:
            print(f"    Warning: Error fixing duplicates: {e}", file=sys.stderr)

        # P1.6: Run validation prompts IN PARALLEL
        print(f"    Running validation prompts in parallel...")

        validation_prompts = [
            ('req-fix_testability.md', 'req_fix_testability'),
            ('req-fix_completeness.md', 'req_fix_completeness'),
            ('req-fix_consistency.md', 'req_fix_consistency'),
            ('req-fix_req-ids.md', 'req_fix_req_ids')
        ]

        def run_validation(prompt_file, report_type, results, errors, iteration_num):
            """Worker thread for parallel validation."""
            try:
                print(f"      Iteration {iteration_num}: Running {prompt_file}...")
                prompt_path = SCRIPT_DIR.parent / 'prompts' / prompt_file
                if not prompt_path.exists():
                    errors.append(f"Prompt not found: {prompt_path}")
                    return

                response = run_ai_prompt(
                    prompt_path,
                    report_type=report_type,
                    timeout=600  # 10 minutes
                )
                results[prompt_file] = response
                print(f"      Iteration {iteration_num}: Completed {prompt_file}")
            except Exception as e:
                errors.append(f"Error in {prompt_file}: {e}")

        # Launch validation threads
        threads = []
        results = {}
        errors = []

        for prompt_file, report_type in validation_prompts:
            thread = threading.Thread(
                target=run_validation,
                args=(prompt_file, report_type, results, errors, iteration),
                daemon=False
            )
            thread.start()
            threads.append(thread)

        # Wait for all threads
        for thread in threads:
            thread.join()

        if errors:
            print(f"    Warning: Some validations had errors:")
            for error in errors:
                print(f"      - {error}")
        else:
            print(f"    OK All validations completed")

        # P1.7: Signature after
        sig_after = take_signature(['./reqs'])
        print(f"    Signature AFTER: {sig_after[:16]}...")

        # P1.8: Check convergence
        if sig_before == sig_after:
            print(f"    OK Converged (no changes)")
            print()
            break
        else:
            print(f"    Changes detected, continuing...")
            print()

            if iteration >= max_iterations:
                print(f"  Reached max iterations ({max_iterations}), good enough")
                print()

    # P1.9: AI order requirements
    print("P1.9: AI ordering requirements by dependency...")
    prompt_path = SCRIPT_DIR.parent / 'prompts' / 'ORDER_REQS.md'

    if not prompt_path.exists():
        print(f"  Warning: Prompt not found: {prompt_path}")
        print(f"  Skipping ordering")
    else:
        try:
            response = run_ai_prompt(
                prompt_path,
                report_type='order_reqs',
                timeout=600
            )
            print(f"  OK AI ordered requirements")
        except Exception as e:
            print(f"  Warning: Error ordering requirements: {e}", file=sys.stderr)

    print()

    # P1.10: Done
    print("P1.10: Requirements generation complete")
    print()

    # List generated requirements
    req_files = sorted(Path('./reqs').glob('*.md'))
    if req_files:
        print(f"Generated {len(req_files)} requirement files:")
        for req_file in req_files:
            print(f"  - {req_file.name}")
        print()
    else:
        print("  Warning: No requirement files found in ./reqs/", file=sys.stderr)
        return False

    return True


def main():
    """Main entry point."""
    print()
    print("=" * 70)
    print("REQUIREMENTS GENERATION (P0-P1)")
    print("=" * 70)

    # Change to project root (two levels up from this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)
    print(f"Working directory: {Path.cwd()}")
    print()

    # P0.1: Prepare workspace
    prepare_workspace()

    # P0: Quality check
    if not phase_0_quality_check():
        print()
        print("FAIL Phase 0 failed or was aborted")
        return 1

    # P1: Requirements generation
    if not phase_1_requirements_generation():
        print()
        print("FAIL Phase 1 failed")
        return 1

    # Success
    print()
    print("=" * 70)
    print("OK REQUIREMENTS GENERATION COMPLETE")
    print("=" * 70)
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
