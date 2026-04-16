# Claude-GAN: Gemini CLI MCP Extension

A GAN-inspired development system where **Gemini CLI acts natively as the Evaluator (Brain)** and calls **Claude 4.6 Sonnet (Vertex AI) as the Generator (Hands)** via MCP (Model Context Protocol).

## How It Works

```
Gemini CLI (Evaluator — native reasoning)
  │
  ├─ 1. Writes Sprint Contract (JSON DoD) using its own reasoning
  ├─ 2. Calls claude_generate MCP tool ──▶ Claude 4.6 Sonnet (Vertex AI)
  ├─ 3. Evaluates the returned code against the contract
  └─ 4. Repeats with specific feedback until Grade A
```

Gemini CLI's built-in Gemini model IS the Evaluator. Claude is a callable MCP tool — not a subprocess. The GAN loop runs entirely within the Gemini CLI session.

## Prerequisites

- **Google Cloud Project** with Vertex AI API enabled and Claude 4.6 Sonnet access in the `global` region
- **Gemini CLI** installed and authenticated
- **Python 3.10+** with pip
- `gcloud auth application-default login` completed

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/hajekim/claude-gan.git
cd claude-gan
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Register the MCP Server Globally

Add the following entry to `~/.gemini/settings.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "claude-gan": {
      "command": "/path/to/python3",
      "args": ["/absolute/path/to/claude-gan/src/mcp_server.py"],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "your-gcp-project-id",
        "GOOGLE_CLOUD_LOCATION": "global",
        "PYTHONPATH": "/absolute/path/to/claude-gan"
      }
    }
  }
}
```

Replace all `/absolute/path/to/claude-gan` with the actual path where you cloned the repository, and `/path/to/python3` with the output of `which python3`.

### 4. Add GAN Instructions to Your GEMINI.md

Add the following two snippets to your existing `~/.gemini/GEMINI.md`. Do **not** overwrite the file — append to the relevant sections instead.

**In your MCP Servers list**, add one entry:

```
- **claude-gan**: Code generation via GAN loop. Use `claude_generate(task, contract, feedback)`
  to delegate implementation to Claude 4.6 Sonnet (Vertex AI).
  Also provides `save_artifact(content, filename)` and
  `save_progress(sprint_id, status, grade, input_tokens, output_tokens)`.
```

**In your execution workflow** (e.g. inside an ACT or GAN-Inspired Loop section), add:

```
For code generation tasks, delegate to Claude via the claude-gan MCP instead of
writing code directly:
1. Write a Sprint Contract (JSON DoD) based on the task.
2. Call claude_generate(task, contract, feedback="") to get Claude's implementation.
   The response ends with "# USAGE: input_tokens=X, output_tokens=Y" — note these values.
3. Evaluate the result as the Skeptical Judge (Gemini = Evaluator).
4. If Grade B/C, call claude_generate again with specific feedback. Repeat up to 3 times.
5. On Grade A, call save_artifact to save the code, then call
   save_progress(sprint_id, status, grade, input_tokens=X, output_tokens=Y) with the token counts.
For non-generation tasks (surgical patches, config changes), implement directly.
```

## Usage

Restart Gemini CLI, then describe your task naturally:

```
Implement a Python calculator with add, subtract, multiply, divide and unit tests using the GAN loop.
```

### Example Session

**Planning phase** — Gemini drafts a Sprint Contract and asks for approval:

```
✦ I've created a development plan (PLAN.md) for a Python calculator with full unit test
  coverage. Using the GAN loop (Gemini as Evaluator, Claude as Generator) to ensure
  PEP 8 compliance and complete test coverage.

  Shall I break this into sprint tasks (DEFINE.md) and begin implementation?

  PLAN.md Summary:
   - Goal: Python calculator module with four operations and pytest unit tests.
   - Strategy: Generate code via Claude 4.6 Sonnet (claude_generate), validated by Gemini.
   - Verification Contract: All four operations correct, ZeroDivisionError handled,
     PEP 8 compliant, tests passing.
   - Grade Target: Grade A — complete functionality and clean style.
```

**Implementation phase** — after approval, the GAN loop runs and delivers:

```
✦ The GAN loop (Claude Generator + Gemini Evaluator) has completed a high-quality
  Python calculator. All four operations are implemented with full pytest coverage.

  Output: calculator.py + tests/test_calculator.py
   - Features:
       - add(), subtract(), multiply(), divide() with correct return types.
       - ZeroDivisionError handled gracefully in divide().
       - 8 unit tests covering all operations and edge cases.
       - PEP 8 compliant throughout.

  GAN Loop Results:
   - Generator (Claude 4.6 Sonnet): Clean, well-documented module with clear signatures.
   - Evaluator (Gemini): Verified edge-case handling, test coverage, and style — Grade A.
```

### Outputs

| File | Description |
|------|-------------|
| `artifacts/solution_SPRINT-XXX.py` | Final generated code |
| `state/progress.json` | Sprint status, grade, and token usage |

## Available MCP Tools

These tools are registered globally and available in all Gemini CLI sessions:

| Tool | Description |
|------|-------------|
| `claude_generate(task, contract, feedback="")` | Calls Claude 4.6 Sonnet (Vertex AI) to generate or refine code |
| `save_artifact(content, filename)` | Saves output to `artifacts/` directory |
| `load_progress()` | Reads current sprint state from `state/progress.json` |
| `save_progress(sprint_id, status, grade, input_tokens=0, output_tokens=0)` | Persists sprint state and token usage |

## Project Structure

```
claude-gan/
├── src/
│   ├── mcp_server.py                # FastMCP server (stdio transport)
│   └── tools/
│       └── claude_tool.py           # Claude Vertex AI call logic
├── tests/
│   └── test_claude_tool.py          # Unit tests
├── state/
│   └── progress.json                # Sprint state (runtime, gitignored)
├── artifacts/                       # Generated code outputs (runtime, gitignored)
├── gemini-extension.json.template   # Extension manifest template (copy and fill in paths)
└── requirements.txt
```

## License

MIT License
