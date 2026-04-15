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
git clone https://github.com/your-repo/claude-gan.git
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
    "claude-generator": {
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
- **claude-generator**: Code generation via GAN loop. Use `claude_generate(task, contract, feedback)`
  to delegate implementation to Claude 4.6 Sonnet (Vertex AI).
  Also provides `save_artifact(content, filename)` and `save_progress(sprint_id, status, grade)`.
```

**In your execution workflow** (e.g. inside an ACT or GAN-Inspired Loop section), add:

```
For code generation tasks, delegate to Claude via the claude-generator MCP instead of
writing code directly:
1. Write a Sprint Contract (JSON DoD) based on the task.
2. Call claude_generate(task, contract, feedback="") to get Claude's implementation.
3. Evaluate the result as the Skeptical Judge (Gemini = Evaluator).
4. If Grade B/C, call claude_generate again with specific feedback. Repeat up to 3 times.
5. On Grade A, call save_artifact and save_progress to persist the result.
For non-generation tasks (surgical patches, config changes), implement directly.
```

## Usage

Restart Gemini CLI, then describe your task naturally. The GAN loop activates based on GEMINI.md instructions:

```
Python으로 가위바위보 게임을 만들어줘. 점수 기록 기능도 포함해줘.
```

```
Implement a FastAPI server with JWT authentication and input validation.
```

Gemini will:
1. Write a Sprint Contract (Definition of Done) using its own reasoning
2. Call `claude_generate` to get an implementation from Claude
3. Evaluate the result strictly against the contract
4. Iterate with actionable feedback until Grade A is achieved

### Outputs

| File | Description |
|------|-------------|
| `artifacts/solution_SPRINT-XXX.py` | Final generated code |
| `state/progress.json` | Sprint status and grade |

## Available MCP Tools

These tools are registered globally and available in all Gemini CLI sessions:

| Tool | Description |
|------|-------------|
| `claude_generate(task, contract, feedback)` | Calls Claude 4.6 Sonnet (Vertex AI) to generate or refine code |
| `save_artifact(content, filename)` | Saves output to `artifacts/` directory |
| `load_progress()` | Reads current sprint state from `state/progress.json` |
| `save_progress(sprint_id, status, grade)` | Persists sprint state |

## Project Structure

```
claude-gan/
├── src/
│   ├── mcp_server.py        # FastMCP server (stdio transport)
│   ├── tools/
│   │   └── claude_tool.py   # Claude Vertex AI call logic
│   └── config.py            # Environment config
├── tests/
│   └── test_claude_tool.py  # Unit tests
├── state/
│   └── progress.json        # Sprint state persistence
├── artifacts/               # Generated code outputs
├── GEMINI.md                # Evaluator instructions for Gemini CLI
├── gemini-extension.json    # Extension manifest (optional)
└── requirements.txt
```

## License

MIT License
