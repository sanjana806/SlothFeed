"""Unit tests for SlothFeed Gemma 2 runner and prompt turn formatting."""

import pytest
import asyncio
from backend.gemma_runner import (
    format_gemma_prompt,
    clean_and_parse_json,
    GemmaRunner
)


def test_format_gemma_prompt_turn_tags():
    content = "Gemma 2 provides state of the art open weights with 2B and 9B variants."
    prompt = format_gemma_prompt(content)
    
    assert "<start_of_turn>user" in prompt
    assert "<end_of_turn>" in prompt
    assert "<start_of_turn>model" in prompt
    assert "sloth_verdict" in prompt
    assert "two_line_brief" in prompt
    assert "action_item" in prompt
    assert content in prompt


def test_clean_and_parse_json_direct():
    raw = '{"sloth_verdict": "Read", "two_line_brief": "Line 1. Line 2.", "action_item": "Adopt now."}'
    parsed = clean_and_parse_json(raw)
    assert parsed is not None
    assert parsed["sloth_verdict"] == "Read"
    assert parsed["action_item"] == "Adopt now."


def test_clean_and_parse_json_with_markdown_fences():
    raw = """
    Here is your requested output:
    ```json
    {
      "sloth_verdict": "Skip",
      "two_line_brief": "This is clickbait. Safely avoid.",
      "action_item": "None: safely ignore"
    }
    ```
    Hope this saves you time!
    """
    parsed = clean_and_parse_json(raw)
    assert parsed is not None
    assert parsed["sloth_verdict"] == "Skip"
    assert parsed["action_item"] == "None: safely ignore"


def test_gemma_runner_embedded_inference():
    async def _run():
        runner = GemmaRunner()
        text = "Today Google DeepMind released Gemma 2 with revolutionary architecture and high performance open weights."
        res = await runner.generate_digest(text, title="Gemma 2 Release")

        assert res["sloth_verdict"] in ["Read", "Skim", "Skip"]
        assert len(res["two_line_brief"]) > 10
        assert "action_item" in res
        assert "google/gemma-2-2b-it" in res["model"]

    asyncio.run(_run())
