"""Anthropic SDK agentic message loop."""
from __future__ import annotations

from typing import Any

import anthropic

from .permissions import PermissionGate
from .tools import ToolRegistry

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096


class Loop:
    def __init__(
        self,
        system: str,
        tool_registry: ToolRegistry,
        permission_gate: PermissionGate | None = None,
    ) -> None:
        self.system = system
        self.registry = tool_registry
        self.gate = permission_gate or PermissionGate()
        self.client = anthropic.Anthropic()

    def run(self, user_message: str) -> str:
        """Run the agentic loop and return the final text response."""
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
        tools = self.registry.schemas()

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=self.system,
                tools=tools,
                messages=messages,
            )

            # Collect assistant content
            assistant_content: list[dict[str, Any]] = []
            tool_uses: list[dict[str, Any]] = []

            for block in response.content:
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )
                    tool_uses.append(block)

            messages.append({"role": "assistant", "content": assistant_content})

            if response.stop_reason == "end_turn" or not tool_uses:
                # Return the last text block
                for block in reversed(response.content):
                    if block.type == "text":
                        return block.text
                return ""

            # Handle tool calls
            tool_results: list[dict[str, Any]] = []
            for tool_use in tool_uses:
                allowed, reason = self.gate.check(tool_use.name, tool_use.input)
                if allowed:
                    result = self.registry.call(tool_use.name, tool_use.input)
                else:
                    result = f"Permission denied: {reason}"

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result,
                    }
                )

            messages.append({"role": "user", "content": tool_results})
