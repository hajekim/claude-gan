import json
import os
from anthropic import AnthropicVertex

MODEL_ID: str = os.getenv("CLAUDE_MODEL_ID", "claude-sonnet-4-6")
MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "8192"))

_SYSTEM_PROMPT = (
    "You are a senior software engineer. "
    "Implement the task strictly according to the Sprint Contract (DoD). "
    "Respond with clean, production-ready code only."
)


def create_client() -> AnthropicVertex:
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    region = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    return AnthropicVertex(region=region, project_id=project_id)


def generate(task: str, contract: str, feedback: str = "") -> str:
    """Claude Vertex AI를 호출하여 코드를 생성하거나 개선한다.

    Args:
        task: 사용자 작업 설명
        contract: JSON 형식의 Sprint Contract (DoD 포함)
        feedback: Evaluator의 이전 피드백 (최초 호출 시 빈 문자열)

    Returns:
        Claude가 생성한 코드 문자열. 응답이 잘린 경우 WARNING 접미사 포함.
    """
    try:
        json.loads(contract)
    except json.JSONDecodeError as e:
        raise ValueError(f"contract must be valid JSON: {e}") from e

    client = create_client()
    prompt = _build_prompt(task, contract, feedback)

    message = client.messages.create(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    text = _extract_text(message.content)
    if message.stop_reason == "max_tokens":
        text += "\n\n# WARNING: Response was truncated due to max_tokens limit."
    return text


def _extract_text(content: list) -> str:
    """content block 목록에서 텍스트를 안전하게 추출한다.

    TextBlock만 수집하며, 복수의 블록은 이어붙여 반환한다.

    Raises:
        ValueError: 텍스트 블록이 하나도 없을 때
    """
    parts = [block.text for block in content if hasattr(block, "text")]
    if not parts:
        raise ValueError("No text content in Claude response.")
    return "".join(parts)


def _build_prompt(task: str, contract: str, feedback: str) -> str:
    base = f"### Task:\n{task}\n\n### Sprint Contract (DoD):\n{contract}"
    if feedback:
        return (
            base
            + f"\n\n### Previous Feedback:\n{feedback}"
            + "\n\nRefine your implementation to address all feedback points."
        )
    return base + "\n\nImplement strictly according to the Contract above."
