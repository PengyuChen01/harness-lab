"""Middle-tier permission gate for tool calls."""
from __future__ import annotations

import os

READ_ONLY_TOOLS = {"Read", "Grep"}


class PermissionGate:
    def __init__(self, auto_allow: bool | None = None) -> None:
        if auto_allow is None:
            auto_allow = os.environ.get("HARNESS_AUTO_ALLOW", "0") == "1"
        self.auto_allow = auto_allow

    def check(self, tool_name: str, inputs: dict) -> tuple[bool, str]:
        """Return (allowed, reason)."""
        if self.auto_allow or tool_name in READ_ONLY_TOOLS:
            return True, "auto-allowed"

        # Interactive confirmation for Write, Edit, Bash
        print(f"\n[permission] Tool: {tool_name}")
        for k, v in inputs.items():
            preview = str(v)[:120]
            print(f"  {k}: {preview}")
        answer = input("Allow? [y/N] ").strip().lower()
        if answer in ("y", "yes"):
            return True, "user approved"
        return False, "user denied"
