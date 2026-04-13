"""Tests for coarse.agents.quote_repair."""

from __future__ import annotations

from unittest.mock import MagicMock

from coarse.agents.quote_repair import QuoteRepairAgent, _QuoteRepairBatch, _QuoteRepairItem


def test_quote_repair_agent_returns_number_to_quote_map():
    client = MagicMock()
    client.supports_prompt_caching = False
    client.complete.return_value = _QuoteRepairBatch(
        repairs=[
            _QuoteRepairItem(number=2, quote="Recovered quote"),
            _QuoteRepairItem(number=5, quote=""),
        ]
    )

    agent = QuoteRepairAgent(client)
    result = agent.run(
        [
            {
                "number": 2,
                "title": "Comment 2",
                "feedback": "Feedback",
                "original_quote": "Original",
                "candidate_passages": ["Candidate passage"],
                "ratio": 0.74,
                "threshold": 0.80,
            }
        ]
    )

    assert result == {2: "Recovered quote", 5: ""}
    assert client.complete.call_count == 1


def test_quote_repair_agent_empty_input_short_circuits():
    client = MagicMock()
    agent = QuoteRepairAgent(client)
    assert agent.run([]) == {}
    client.complete.assert_not_called()
