import pytest
from unittest.mock import MagicMock, patch
from src.tools import claude_tool


VALID_CONTRACT = '{"dod": ["print hello"]}'


def _make_mock_message(text: str, stop_reason: str = "end_turn") -> MagicMock:
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    msg.stop_reason = stop_reason
    return msg


def test_generate_initial_call_builds_correct_prompt():
    """피드백 없는 최초 호출 시 task와 contract만 포함된 프롬프트가 구성된다."""
    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_message("generated code")
        mock_create_client.return_value = mock_client

        from src.tools.claude_tool import generate

        result = generate(task="Write hello world", contract=VALID_CONTRACT)

    assert result == "generated code"
    call_kwargs = mock_client.messages.create.call_args.kwargs
    messages = call_kwargs["messages"]
    assert len(messages) == 1
    assert "Write hello world" in messages[0]["content"]
    assert "Previous Feedback" not in messages[0]["content"]


def test_generate_refinement_call_includes_feedback():
    """피드백이 있을 때 프롬프트에 Previous Feedback 섹션이 포함된다."""
    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_message("refined code")
        mock_create_client.return_value = mock_client

        from src.tools.claude_tool import generate

        result = generate(
            task="Write hello world",
            contract=VALID_CONTRACT,
            feedback="Add error handling",
        )

    assert result == "refined code"
    call_kwargs = mock_client.messages.create.call_args.kwargs
    messages = call_kwargs["messages"]
    assert "Previous Feedback" in messages[0]["content"]
    assert "Add error handling" in messages[0]["content"]


def test_generate_uses_correct_model_and_max_tokens():
    """설정된 모델 ID와 max_tokens로 Vertex AI가 호출된다."""
    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_message("code")
        mock_create_client.return_value = mock_client

        claude_tool.generate(task="t", contract=VALID_CONTRACT)

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == claude_tool.MODEL_ID
    assert call_kwargs["max_tokens"] == claude_tool.MAX_TOKENS


def test_create_client_requires_project_id(monkeypatch):
    """GOOGLE_CLOUD_PROJECT가 없으면 KeyError가 발생한다."""
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)

    with pytest.raises(KeyError):
        claude_tool.create_client()


def test_truncated_response_adds_warning():
    """stop_reason이 max_tokens이면 WARNING 접미사가 붙는다."""
    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_message(
            "partial code", stop_reason="max_tokens"
        )
        mock_create_client.return_value = mock_client

        result = claude_tool.generate(task="t", contract=VALID_CONTRACT)

    assert "partial code" in result
    assert "WARNING" in result
    assert "max_tokens" in result


def test_multiple_text_blocks_joined():
    """content에 TextBlock이 여러 개이면 이어붙인 텍스트를 반환한다."""
    block1 = MagicMock(text="part1")
    block2 = MagicMock(text="part2")
    msg = MagicMock()
    msg.content = [block1, block2]
    msg.stop_reason = "end_turn"

    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = msg
        mock_create_client.return_value = mock_client

        result = claude_tool.generate(task="t", contract=VALID_CONTRACT)

    assert result == "part1part2"


def test_non_text_block_raises_value_error():
    """텍스트 블록이 없으면 ValueError가 발생한다."""
    tool_use_block = MagicMock(spec=[])  # text 속성 없음
    msg = MagicMock()
    msg.content = [tool_use_block]
    msg.stop_reason = "end_turn"

    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = msg
        mock_create_client.return_value = mock_client

        with pytest.raises(ValueError, match="No text content"):
            claude_tool.generate(task="t", contract=VALID_CONTRACT)


def test_invalid_contract_raises_value_error():
    """유효하지 않은 JSON contract는 ValueError를 발생시킨다."""
    with pytest.raises(ValueError, match="contract must be valid JSON"):
        claude_tool.generate(task="t", contract="not-json")


def test_max_tokens_env_override(monkeypatch):
    """CLAUDE_MAX_TOKENS 환경변수가 max_tokens로 전달된다."""
    monkeypatch.setenv("CLAUDE_MAX_TOKENS", "1024")

    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_message("code")
        mock_create_client.return_value = mock_client

        # 모듈 재로드 없이 현재 MAX_TOKENS 값을 직접 패치
        with patch.object(claude_tool, "MAX_TOKENS", 1024):
            claude_tool.generate(task="t", contract=VALID_CONTRACT)

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["max_tokens"] == 1024
