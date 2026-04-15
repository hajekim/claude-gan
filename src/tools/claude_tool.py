import os
from anthropic import AnthropicVertex

MODEL_ID: str = os.getenv("CLAUDE_MODEL_ID", "claude-sonnet-4-6")
MAX_TOKENS: int = 4096

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
        Claude가 생성한 코드 문자열
    """
    client = create_client()
    prompt = _build_prompt(task, contract, feedback)

    message = client.messages.create(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _build_prompt(task: str, contract: str, feedback: str) -> str:
    base = f"### Task:\n{task}\n\n### Sprint Contract (DoD):\n{contract}"
    if feedback:
        return (
            base
            + f"\n\n### Previous Feedback:\n{feedback}"
            + "\n\nRefine your implementation to address all feedback points."
        )
    return base + "\n\nImplement strictly according to the Contract above."
