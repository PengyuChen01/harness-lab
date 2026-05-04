"""CLI entry point for harness."""
from __future__ import annotations

import argparse

from .loop import Loop
from .permissions import PermissionGate
from .tools import tool_registry

SYSTEM_PROMPT = (
    "You are a helpful coding assistant. You have access to tools to read, write, "
    "and edit files and run shell commands. Use them to complete the user's task."
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Harness agent")
    parser.add_argument("--task", required=True, help="Task description for the agent")
    args = parser.parse_args()

    gate = PermissionGate()
    loop = Loop(system=SYSTEM_PROMPT, tool_registry=tool_registry, permission_gate=gate)
    result = loop.run(args.task)
    print(result)


if __name__ == "__main__":
    main()
