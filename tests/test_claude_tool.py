import pytest
from unittest.mock import MagicMock, patch


def test_generate_initial_call_builds_correct_prompt():
    """피드백 없는 최초 호출 시 task와 contract만 포함된 프롬프트가 구성된다."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="generated code")]

    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message
        mock_create_client.return_value = mock_client

        from src.tools.claude_tool import generate

        result = generate(task="Write hello world", contract='{"dod": ["print hello"]}')

    assert result == "generated code"
    call_kwargs = mock_client.messages.create.call_args.kwargs
    messages = call_kwargs["messages"]
    assert len(messages) == 1
    assert "Write hello world" in messages[0]["content"]
    assert "Previous Feedback" not in messages[0]["content"]


def test_generate_refinement_call_includes_feedback():
    """피드백이 있을 때 프롬프트에 Previous Feedback 섹션이 포함된다."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="refined code")]

    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message
        mock_create_client.return_value = mock_client

        from src.tools.claude_tool import generate

        result = generate(
            task="Write hello world",
            contract='{"dod": ["print hello"]}',
            feedback="Add error handling",
        )

    assert result == "refined code"
    call_kwargs = mock_client.messages.create.call_args.kwargs
    messages = call_kwargs["messages"]
    assert "Previous Feedback" in messages[0]["content"]
    assert "Add error handling" in messages[0]["content"]


def test_generate_uses_correct_model_and_max_tokens():
    """설정된 모델 ID와 max_tokens로 Vertex AI가 호출된다."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="code")]

    with patch("src.tools.claude_tool.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message
        mock_create_client.return_value = mock_client

        from src.tools import claude_tool
        claude_tool.generate(task="t", contract="c")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == claude_tool.MODEL_ID
    assert call_kwargs["max_tokens"] == claude_tool.MAX_TOKENS


def test_create_client_requires_project_id(monkeypatch):
    """GOOGLE_CLOUD_PROJECT가 없으면 KeyError 또는 ValueError가 발생한다."""
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)

    import importlib
    import src.tools.claude_tool as ct
    importlib.reload(ct)

    with pytest.raises((ValueError, KeyError)):
        ct.create_client()
