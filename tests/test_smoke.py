"""Smoke tests for the harness tool registry."""
import os

import pytest

os.environ.setdefault("HARNESS_AUTO_ALLOW", "1")

from harness.tools import ToolRegistry, tool_registry  # noqa: E402


EXPECTED_TOOLS = {"Read", "Write", "Edit", "Grep", "Bash"}


def test_all_tools_registered():
    assert set(tool_registry.names()) == EXPECTED_TOOLS


def test_tool_schemas_have_required_fields():
    for schema in tool_registry.schemas():
        assert "name" in schema
        assert "description" in schema
        assert "input_schema" in schema
        assert "_fn" not in schema, "Internal _fn must not leak into schema"


def test_read_tool_returns_content(tmp_path):
    # Use pyproject.toml which definitely exists
    result = tool_registry.call("Read", {"path": "pyproject.toml"})
    assert "harness-lab" in result
    assert "anthropic" in result


def test_read_tool_missing_file():
    result = tool_registry.call("Read", {"path": "/nonexistent/path/file.txt"})
    assert "Error" in result


def test_registry_isolation():
    """A new ToolRegistry instance has the same five tools."""
    reg = ToolRegistry()
    assert set(reg.names()) == EXPECTED_TOOLS
