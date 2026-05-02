# harness-lab

A small, hackable agent harness in Python — built to learn what makes a good
harness by implementing the elements that matter, with no bloat.

## Goals

Implement (and keep simple) the elements a good harness needs:

- **Specialized tools** over generic shell — `read`, `write`, `edit`, `grep`, `bash`
- **Cross-session memory** with an index file pattern
- **Permission model** with a middle tier (auto-allow read-only, gate destructive ops)
- **Sub-agent / delegation** for context isolation
- **Skills**: pull-on-demand capability packs (vs. system-prompt bloat)
- **Hooks** for deterministic interception (pre-tool, on-stop)
- **Interruptible + redirectable** message loop
- **Self-introspection** (`/tools`, `/memory`, `/usage`)
- **Model-agnostic** — swap Anthropic models without code changes

## Status

Bootstrapping. See `.autonomous/conductor-state.json` for sprint progress.

## Stack

- Python 3.11+
- Anthropic SDK (`anthropic`)
- No web framework; CLI first.
