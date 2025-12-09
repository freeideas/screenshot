Create testable requirement flows in `./reqs/` based on use-case documentation in `./specs/` and `./README.md`.

**ONLY TWO VALID SOURCES FOR REQUIREMENTS:**
1. `./README.md`
2. Files in `./specs/*.md`

**NO OTHER SOURCES ARE VALID.** The `./docs/` directory contains reference materials (API docs, protocol specs, .wsdl files) that may help you understand README/specs, but `./docs/` can NEVER be cited as a source. Every requirement MUST be traceable to `./README.md` or a file in `./specs/`.

**Your task:** Write or edit ALL requirement files in `./reqs/` directory. Write, rewrite, or edit requirements from README/specs.

---

## THE SEVEN RULES FOR REQUIREMENTS

1. **Complete Coverage** -- Every reasonably testable behavior in README.md or ./specs/ must have a $REQ_ID
2. **No Invention** -- Only requirements from `./README.md` or `./specs/*.md` are allowed (./docs/ is NEVER a valid source)
3. **No Overspecification** -- Requirements must not be more specific than README.md or ./specs/
4. **Tell Stories** -- Flows go from start to shutdown (complete use-case scenarios)
5. **Source Attribution** -- Every $REQ_ID cites ONLY: `**Source:** ./README.md (Section: "Name")` or `**Source:** ./specs/FILE.md (Section: "Name")`
6. **Unique IDs** -- Each $REQ_ID appears exactly once. Format: `$REQ_` followed by letters/digits/underscores/hyphens (e.g., $REQ_STARTUP_001)
7. **Reasonably Testable** -- Requirements must have observable behavior that can be verified

---

## What Is a Flow?

A flow is a **sequence of steps from application start to shutdown** that can be tested end-to-end.

**If README documentation presents specific named flows or scenarios, each one MUST be represented in its own requirements document.**

**Example:** `./specs/LIFECYCLE.md` generates:
- `./reqs/install.md` -- Install to ready state
- `./reqs/startup-to-shutdown.md` -- Start server, use it, stop it
- `./reqs/uninstall.md` -- Remove from system

---

## Flow Document Format

```markdown
# Server Startup Flow

**Source:** ./specs/LIFECYCLE.md

Start server, verify ready, and shut down cleanly.

## $REQ_STARTUP_001: Launch Process
**Source:** ./specs/LIFECYCLE.md (Section: "Starting the Server")
<!-- NOTE: Source MUST be ./README.md or ./specs/*.md -- NEVER ./docs/ -->

Start the server executable with default configuration.

## $REQ_STARTUP_002: Bind to Port
**Source:** ./specs/LIFECYCLE.md (Section: "Network Binding")

Server must bind to configured port.

## $REQ_STARTUP_003: Log Ready Message
**Source:** ./specs/LIFECYCLE.md (Section: "Startup Logging")

Server must log when ready to accept connections.

## $REQ_STARTUP_004: Health Check Response
**Source:** ./specs/LIFECYCLE.md (Section: "Health Monitoring")

GET /health must return 200 OK.

## $REQ_STARTUP_005: Shutdown Cleanly
**Source:** ./specs/LIFECYCLE.md (Section: "Stopping")

Server must exit gracefully when receiving SIGTERM.
```

---

## What to Include

**Not everything in documentation needs to be a requirement.** READMEs include descriptive context to help readers understand. Extract the actual requirement, not the description.

**Examples:**
- README: "Returns simple HTML" -> Requirement: "Returns HTML with 200 OK" (not "HTML must be simple")
- README: "Returns the same HTML each time" -> Requirement: "Returns HTML" (not "Must return identical content every time")
- README: "Polls file every 500ms" -> Requirement: "Detects file changes" (not "Must poll every 500ms")

**DO write requirements for delivered software:**
- Runtime behavior of executable with correct inputs (happy paths)
- Command-line arguments and options (what they do, not what happens with wrong values)
- Network behavior, logging, file I/O
- Error handling **explicitly documented in README**
- Observable outputs and responses
- Architectural constraints (e.g., "use non-blocking I/O")
- **Build output verification** (what files must exist in `./released/`, their names, sizes, structure)

**DO NOT write requirements for:**
- Build scripts or build processes (how to compile, what commands to run)
- Development prerequisites (.NET SDK, compilers, dev tools)
- How to compile or package (step-by-step build instructions)
- Development tooling or infrastructure
- **Wrong inputs/edge cases** (unless README explicitly documents error behavior)
- **Negative capabilities** (e.g., "does not support UDP" - absence of feature)
- **Performance/load characteristics** (e.g., "handles 10k requests/sec" - hard to test reliably)
- **Natural consequences** (e.g., OOM crashes, data loss on process kill)
- **OS/runtime behavior** (e.g., process termination on SIGKILL)

**Why?** Customers receive built executable from `./released/`. Requirements focus on what the delivered product does with correct usage, not exhaustive error testing.

---

## How to Write Requirements

### Step 1: Read All Documentation

Read thoroughly:
- `./README.md`
- All files in `./specs/*.md`

You may skim `./docs/` to understand technical context (e.g., WSDL schemas, API references), but **./docs/ can NEVER be cited as a source**. If a behavior appears only in `./docs/` and not in README.md or ./specs/, it is NOT a requirement.

Identify reasonably testable behaviors **of delivered software:** anchored in README.md or ./specs/ only.
- Actions users take with executable (with correct inputs)
- System responses (to valid requests)
- Observable outputs
- Error conditions **explicitly documented in README**
- Success criteria
- **Contents of ./released/ directory** (what files must be present after build)

**Skip sections about:**
- "Building from source" (HOW to compile)
- "Development prerequisites" (what tools are needed to build)
- Build/compilation instructions (steps to run the build)
- Limitations stated as absences ("doesn't support X")
- Performance/load claims ("handles 10k req/sec")
- What happens with wrong inputs (unless README.md or ./specs/ documents it)
- Behaviors described only in `./docs/` (./docs/ is NEVER a valid source)

**Important distinction:** If specs document **WHAT must be in ./released/**, that IS a requirement (testable artifact verification). If specs document **HOW to build**, that is NOT a requirement (build process).

### Step 2: Identify User Flows

Group related behaviors into flows:
- Installation flow
- Startup flow
- Normal operation flow
- Error handling flow
- Shutdown flow
- Uninstallation flow

Each flow should be independently testable.

### Step 3: Write Flow Documents

For each flow:
1. **Create file:** `./reqs/flow-name.md`
2. **Add title:** Descriptive name
3. **Add source:** Reference README file
4. **Add description:** What this flow covers
5. **Add requirements:** One `$REQ_ID` per testable step

### Step 4: Write Each Requirement

For each requirement:
1. **ID:** Format is `$REQ_` followed by uppercase letters, digits, and underscores. Must be unique across all files. Examples: `$REQ_STARTUP_001`, `$REQ_BUILD_002`, `$REQ_HTTP_003`
2. **Title:** Short description
3. **Source:** Cite README file and section
4. **Description:** Clear, testable statement

**Make each requirement:**
- Observable (can be verified by test)
- Specific enough to test
- Not over-specified
- Traceable to source
- **Focused on happy paths** (correct usage, not wrong inputs)

---

## Critical Distinctions

**Happy paths vs. error exhaustion:**
- OK "Accepts one directory argument" -> this IS a requirement (describes correct usage)
- X "Exit with error if two directories provided" -> skip unless README explicitly documents this
- OK "Port number is required" -> this IS a requirement (describes correct usage)
- X "Show error if port missing" -> skip unless README explicitly documents this error

**Capabilities vs. absences:**
- OK "Proxies TCP connections" -> this IS a requirement (what it does)
- X "Does not support UDP" -> skip (absence of feature, nothing to test)
- OK "Returns error 'UDP not supported' if UDP attempted" -> this IS a requirement IF README documents it

**Architectural constraints vs. natural consequences:**
- OK "Never block network I/O on disk writes" -> this IS a requirement (architectural constraint)
- X "Will crash with OOM instead of blocking" -> skip (natural consequence, not a feature)
- OK "Buffer in memory when logging falls behind" -> this IS a requirement (what system does)

**Explicit error handling vs. implied validation:**
- OK README says "If config file missing, exit with error 'CONFIG_NOT_FOUND'" -> this IS a requirement
- X README says "Requires config file" without mentioning error -> skip the error behavior

**Build output vs. build process:**
- OK "After build, ./released/ must contain exactly 4 files: App.exe, Plugin.dll, Interface.dll, config.json" -> this IS a requirement (testable artifact)
- OK "ConnectorWebApp.exe must be ~80-100MB" -> this IS a requirement (verifiable size)
- X "Run `dotnet publish -c released`" -> skip (build process instruction)
- X "Requires .NET 8 SDK to compile" -> skip (development prerequisite)

---

## Over-Specification Examples

**Over-specified (WRONG):**
- README: "On startup, if config file is missing, show error and exit"
- REQ: "Print `ERROR: CONFIG_NOT_FOUND` to STDERR with exit code -3 and log to Windows Event Viewer"
- **Problem:** Exact message, stream, exit code, and Event Viewer logging not in README

**Correctly specified (RIGHT):**
- README: "On startup, if config file is missing, show error and exit"
- REQ: "Show error message if config file is missing at startup and exit"

**When to include details:**
- README explicitly states them
- Logical necessity (e.g., "crashes" implies non-zero exit)
- Standard protocols (e.g., HTTP status codes)

**When to omit details:**
- Exact error message wording (unless specified)
- Internal implementation (unless specified)
- File formats, data structures (unless specified)
- Performance numbers (unless specified)
- Output streams (unless specified)
- Specific exit codes (unless specified or necessary)
- Wrong input handling (unless specified)
- Edge case behavior (unless specified)

---

## File Naming

Use descriptive, lowercase names with hyphens:
- `install.md`
- `startup-to-shutdown.md`
- `client-usage.md`
- `error-handling.md`
- `uninstall.md`

---

## Your Task Summary

1. **Read** all documentation (`./README.md` and `./specs/*.md` -- these are the ONLY valid sources)
2. **Identify** testable flows (startup-to-shutdown sequences)
3. **Write, rewrite, or edit all files** in ./reqs/ from scratch
   - Ensure there is one .md file per flow
4. **Tag** each requirement with unique $REQ_ID
5. **Cite** source for every requirement (MUST be `./README.md` or `./specs/*.md`)

## Output

After writing, rewriting, or editing all requirement files, report:
- Number of README files processed
- Number of flow files created in ./reqs/
- List of flow files with brief description of each
