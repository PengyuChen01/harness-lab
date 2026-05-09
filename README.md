# harness-lab

A small, hackable agent harness in Python — built to learn what makes a good
harness by implementing the elements that matter, with no bloat.

## Status

Sprint 1 merged: tool registry, permission gate, Anthropic SDK loop, CLI entry,
5 smoke tests passing. See `.autonomous/conductor-state.json` for sprint
progress.

| Element | Status |
|---|---|
| Specialized tools (`Read`, `Write`, `Edit`, `Grep`, `Bash`) | ✅ |
| Permission model (auto-allow read-only, gate writes/bash) | ✅ |
| Anthropic SDK message loop | ✅ |
| Model-agnostic (swap via `MODEL` constant in `harness/loop.py`) | ✅ |
| Cross-session memory with index file pattern | ⏳ planned |
| Sub-agent / delegation for context isolation | ⏳ planned |
| Skills: pull-on-demand capability packs | ⏳ planned |
| Hooks (pre-tool, on-stop) | ⏳ planned |
| Interruptible + redirectable loop | ⏳ planned |
| Self-introspection (`/tools`, `/memory`, `/usage`) | ⏳ planned |

## Quickstart

```bash
pip install -e ".[dev]"
export ANTHROPIC_API_KEY=sk-ant-...
harness --task "list the files in the current directory"
```

The CLI prompts for confirmation on `Write` / `Edit` / `Bash`. Set
`HARNESS_AUTO_ALLOW=1` to bypass prompts (useful for tests; do not use in
contexts where you don't trust the model).

## Layout

```
harness/
  cli.py          # `harness --task <text>` entry point
  loop.py         # Anthropic SDK agentic message loop
  permissions.py  # middle-tier permission gate
  tools.py        # Read, Write, Edit, Grep, Bash + ToolRegistry
tests/
  test_smoke.py   # 5 smoke tests
```

## Development

```bash
pip install -e ".[dev]"
pytest                  # run the test suite
ruff check harness tests  # lint
```

## Stack

- Python 3.11+
- Anthropic SDK (`anthropic>=0.40`)
- `rich` for terminal output
- No web framework; CLI first
