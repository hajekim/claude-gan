"""FastMCP server exposing Claude Vertex AI and artifact management tools to Gemini CLI."""
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from src.tools.claude_tool import generate as _claude_generate

# Anchor all relative paths to the project root regardless of cwd when invoked globally.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ARTIFACTS_DIR = _PROJECT_ROOT / "artifacts"
_STATE_FILE = _PROJECT_ROOT / "state" / "progress.json"

load_dotenv(_PROJECT_ROOT / ".env")

mcp = FastMCP("claude-gan")


@mcp.tool()
def claude_generate(task: str, contract: str, feedback: str = "") -> str:
    """Generate or refine code using Claude 4.6 Sonnet on Vertex AI.

    Args:
        task: Description of the implementation task.
        contract: Sprint Contract as a JSON string (must include definition_of_done).
        feedback: Evaluator feedback from a previous iteration. Omit on first call.
    """
    return _claude_generate(task=task, contract=contract, feedback=feedback)


@mcp.tool()
def save_artifact(content: str, filename: str) -> str:
    """Save generated output to the artifacts/ directory.

    Args:
        content: The content to save (code, text, etc.).
        filename: File name only — no path separators allowed (e.g. 'solution.py').

    Returns:
        Absolute path of the saved file.
    """
    # Guard against path traversal and null bytes.
    safe_name = Path(filename).name
    if "\x00" in filename or safe_name != filename or not safe_name:
        raise ValueError(f"Invalid filename '{filename}': must be a plain file name with no path separators.")

    _ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    path = _ARTIFACTS_DIR / safe_name
    path.write_text(content, encoding="utf-8")
    return str(path)


@mcp.tool()
def load_progress() -> str:
    """Load the current sprint state from state/progress.json.

    Returns:
        JSON string of the current state, or '{}' if no state file exists yet.
    """
    try:
        return json.dumps(json.loads(_STATE_FILE.read_text(encoding="utf-8")), ensure_ascii=False)
    except (FileNotFoundError, json.JSONDecodeError):
        return "{}"


@mcp.tool()
def save_progress(sprint_id: str, status: str, grade: str = "") -> str:
    """Persist the current sprint status to state/progress.json.

    Args:
        sprint_id: Sprint identifier (e.g. 'SPRINT-001').
        status: One of 'IN_PROGRESS', 'SUCCESS', or 'PARTIAL_SUCCESS'.
        grade: Evaluator grade ('A', 'B', or 'C').

    Returns:
        Confirmation message.
    """
    _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "sprint_id": sprint_id,
        "status": status,
        "grade": grade,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"Progress saved: {sprint_id} → {status} (Grade: {grade or 'N/A'})"


if __name__ == "__main__":
    mcp.run()
