from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from coarse.config import CoarseConfig
from coarse.llm import LLMClient, estimate_call_cost, model_cost_per_token

TEST_MODEL = "test/mock-model"


class _SimpleModel(BaseModel):
    value: str


def _make_mock_completion():
    completion = MagicMock()
    completion.usage.prompt_tokens = 100
    completion.usage.completion_tokens = 50
    completion.model = "openai/gpt-4o"
    return completion


@pytest.fixture()
def mock_instructor_client():
    """Patch the instructor module used by LLMClient."""
    with patch("coarse.llm.instructor") as mock_instructor:
        mock_client = MagicMock()
        mock_instructor.from_litellm.return_value = mock_client
        yield mock_client


def test_complete_returns_parsed_model(mock_instructor_client):
    expected = _SimpleModel(value="hello")
    mock_completion = _make_mock_completion()
    mock_instructor_client.chat.completions.create_with_completion.return_value = (
        expected,
        mock_completion,
    )

    with patch("coarse.llm.litellm.completion_cost", return_value=0.001):
        client = LLMClient(model=TEST_MODEL, config=CoarseConfig())
        result = client.complete(
            messages=[{"role": "user", "content": "hello"}],
            response_model=_SimpleModel,
        )

    assert isinstance(result, _SimpleModel)
    assert result.value == "hello"


def test_cost_accumulates_across_calls(mock_instructor_client):
    model_instance = _SimpleModel(value="x")
    mock_completion = _make_mock_completion()
    mock_instructor_client.chat.completions.create_with_completion.return_value = (
        model_instance,
        mock_completion,
    )

    with patch("coarse.llm.litellm.completion_cost", return_value=0.005):
        client = LLMClient(model=TEST_MODEL, config=CoarseConfig())
        client.complete(messages=[{"role": "user", "content": "a"}], response_model=_SimpleModel)
        client.complete(messages=[{"role": "user", "content": "b"}], response_model=_SimpleModel)

    assert abs(client.cost_usd - 0.010) < 1e-9


def test_model_cost_per_token_known_model():
    in_cost, out_cost = model_cost_per_token("openai/gpt-4o")
    assert in_cost > 0
    assert out_cost > 0


def test_model_cost_per_token_unknown_model():
    result = model_cost_per_token("bogus/nonexistent-model-xyz-999")
    assert result == (0.0, 0.0)


def test_estimate_call_cost():
    in_cost, out_cost = model_cost_per_token("gpt-4o")
    expected = in_cost * 1000 + out_cost * 500
    result = estimate_call_cost("gpt-4o", 1000, 500)
    assert result > 0
    assert abs(result - expected) < 1e-12


def test_client_uses_config_model(mock_instructor_client):
    cfg = CoarseConfig(default_model="anthropic/claude-3-5-sonnet")
    client = LLMClient(config=cfg)
    assert client.model == "anthropic/claude-3-5-sonnet"


def test_complete_instructor_validation_error(mock_instructor_client):
    try:
        _SimpleModel()  # missing required 'value' field -> ValidationError
    except ValidationError as exc:
        mock_instructor_client.chat.completions.create_with_completion.side_effect = exc

    client = LLMClient(model=TEST_MODEL, config=CoarseConfig())
    with pytest.raises(ValidationError):
        client.complete(
            messages=[{"role": "user", "content": "bad"}],
            response_model=_SimpleModel,
        )
