"""Text-only prompt serialization for headless CLI clients."""

from __future__ import annotations


def _messages_to_prompt(messages: list[dict]) -> str:
    """Flatten text-only chat messages into one prompt.

    Headless CLI prompts are passed over stdin, which cannot represent image
    attachments. Reject non-text blocks rather than silently dropping them and
    letting a model reason as though it had received evidence that is absent.
    """
    parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "user").upper()
        content = msg.get("content", "")
        if isinstance(content, list):
            text_parts: list[str] = []
            for block in content:
                block_type = block.get("type") if isinstance(block, dict) else None
                if block_type != "text":
                    raise ValueError(
                        "Headless CLI prompt transport only supports text blocks; "
                        f"got {block_type or type(block).__name__!r}. "
                        "Route multimodal calls through the API LLMClient."
                    )
                text_parts.append(block.get("text", ""))
            content = "\n".join(text_parts)
        parts.append(f"[{role}]\n{content}")
    return "\n\n".join(parts)
