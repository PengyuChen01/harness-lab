"""Tool registry with five tools: Read, Write, Edit, Grep, Bash."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any


def _read(path: str, offset: int = 0, limit: int = 2000) -> str:
    p = Path(path)
    if not p.exists():
        return f"Error: file not found: {path}"
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    chunk = lines[offset : offset + limit]
    return "\n".join(f"{offset + i + 1}\t{line}" for i, line in enumerate(chunk))


def _write(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written {len(content)} bytes to {path}"


def _edit(path: str, old_string: str, new_string: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"Error: file not found: {path}"
    text = p.read_text(encoding="utf-8")
    if old_string not in text:
        return f"Error: old_string not found in {path}"
    count = text.count(old_string)
    if count > 1:
        return f"Error: old_string appears {count} times; make it unique"
    p.write_text(text.replace(old_string, new_string, 1), encoding="utf-8")
    return f"Edited {path}"


def _grep(pattern: str, path: str = ".", glob: str = "*") -> str:
    try:
        result = subprocess.run(
            ["rg", "--glob", glob, "-n", pattern, path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = result.stdout or result.stderr
    except FileNotFoundError:
        # fall back to Python grep if ripgrep not available
        matches: list[str] = []
        for f in Path(path).rglob(glob):
            if not f.is_file():
                continue
            try:
                for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if re.search(pattern, line):
                        matches.append(f"{f}:{i}:{line}")
            except Exception:
                pass
        out = "\n".join(matches[:200])
    return out.strip() or "(no matches)"


def _bash(command: str, timeout: int = 60) -> str:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    parts = []
    if result.stdout:
        parts.append(result.stdout)
    if result.stderr:
        parts.append(f"[stderr]\n{result.stderr}")
    if result.returncode != 0:
        parts.append(f"[exit {result.returncode}]")
    return "\n".join(parts).strip() or "(no output)"


# ---------------------------------------------------------------------------
# Tool definitions — Anthropic tool_use API format
# ---------------------------------------------------------------------------

TOOLS: dict[str, dict[str, Any]] = {
    "Read": {
        "name": "Read",
        "description": "Read a file from the filesystem. Returns lines with line numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute or relative file path"},
                "offset": {"type": "integer", "description": "Line offset to start reading from", "default": 0},
                "limit": {"type": "integer", "description": "Maximum lines to return", "default": 2000},
            },
            "required": ["path"],
        },
        "_fn": _read,
    },
    "Write": {
        "name": "Write",
        "description": "Write content to a file, creating parent directories as needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write"},
                "content": {"type": "string", "description": "Full content to write"},
            },
            "required": ["path", "content"],
        },
        "_fn": _write,
    },
    "Edit": {
        "name": "Edit",
        "description": "Replace an exact string in a file. old_string must appear exactly once.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to edit"},
                "old_string": {"type": "string", "description": "Exact text to find"},
                "new_string": {"type": "string", "description": "Text to replace it with"},
            },
            "required": ["path", "old_string", "new_string"],
        },
        "_fn": _edit,
    },
    "Grep": {
        "name": "Grep",
        "description": "Search file contents with a regex pattern.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern to search for"},
                "path": {"type": "string", "description": "Directory or file to search", "default": "."},
                "glob": {"type": "string", "description": "Glob filter for file names", "default": "*"},
            },
            "required": ["pattern"],
        },
        "_fn": _grep,
    },
    "Bash": {
        "name": "Bash",
        "description": "Run a shell command and return stdout/stderr.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"},
                "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 60},
            },
            "required": ["command"],
        },
        "_fn": _bash,
    },
}


class ToolRegistry:
    """Simple registry that maps tool names to their schema + callable."""

    def __init__(self, tools: dict[str, dict[str, Any]] | None = None) -> None:
        self._tools = dict(tools or TOOLS)

    def schemas(self) -> list[dict[str, Any]]:
        """Return Anthropic-compatible tool schema list (no _fn key)."""
        return [
            {k: v for k, v in t.items() if k != "_fn"}
            for t in self._tools.values()
        ]

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def call(self, name: str, inputs: dict[str, Any]) -> str:
        if name not in self._tools:
            return f"Error: unknown tool '{name}'"
        fn = self._tools[name]["_fn"]
        try:
            return fn(**inputs)
        except Exception as exc:
            return f"Error: {exc}"


tool_registry = ToolRegistry()
