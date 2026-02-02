# ClaudeBox [![Discord](https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white)](https://discord.gg/bCmaK4Ce)

Run Claude Code in hardware-isolated micro-VMs with persistent workspaces and a clean Python API.

[![Build Status](https://img.shields.io/github/actions/workflow/status/boxlite-labs/claudebox/ci.yml)](https://github.com/boxlite-labs/claudebox/actions)
[![PyPI version](https://img.shields.io/pypi/v/claudebox.svg)](https://pypi.org/project/claudebox/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

ClaudeBox uses [BoxLite](https://github.com/boxlite-ai/boxlite) to run Claude Code in lightweight local-first sandboxes. It gives you:

- hardware isolation (not containers)
- persistent workspaces under `~/.claudebox/sessions/`
- optional skills and templates for common stacks
- security policies and resource limits
- optional RL training hooks (rewards and trajectory export)

If you like the runtime, consider starring BoxLite.

## Install

```bash
pip install claudebox
```

## Requirements

- Python 3.10+
- BoxLite runtime
- Docker (required by BoxLite)

## Authentication

```bash
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

or:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Quick start

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    async with ClaudeBox() as box:
        result = await box.code("Create a hello world Python script")
        print(result.response)

asyncio.run(main())
```

## Persistent sessions

```python
from claudebox import ClaudeBox

async def main():
    async with ClaudeBox(session_id="my-project") as box:
        await box.code("Initialize a Node.js project with Express")

    async with ClaudeBox.reconnect("my-project") as box:
        await box.code("Add authentication endpoints")

    await ClaudeBox.cleanup_session("my-project", remove_workspace=True)

asyncio.run(main())
```

## Skills and templates

```python
from claudebox import ClaudeBox, SandboxTemplate, DATA_SCIENCE_SKILL

async def main():
    async with ClaudeBox(
        session_id="ml-project",
        template=SandboxTemplate.DATA_SCIENCE,
        skills=[DATA_SCIENCE_SKILL],
    ) as box:
        result = await box.code("Analyze dataset.csv and create visualizations")
        print(result.response)

asyncio.run(main())
```

## Docs

- Getting started: `docs/getting-started/`
- Guides: `docs/guides/`
- API reference: `docs/api-reference/`
- Architecture: `docs/architecture/`
- Troubleshooting: `docs/troubleshooting/`

## Examples

See `examples/README.md` for a curated list of runnable examples.

## API snapshot

```python
from claudebox import ClaudeBox

box = ClaudeBox(
    session_id="my-project",
    skills=[...],
    template=...,
    security_policy=...,
)
```

Key methods:

- `await box.code(prompt, ...)`
- `await ClaudeBox.reconnect(session_id, ...)`
- `await ClaudeBox.cleanup_session(session_id, remove_workspace=False)`
- `ClaudeBox.list_sessions(workspace_dir=None)`

## Contributing

See `CONTRIBUTING.md` for development setup, standards, and tests.

## License

MIT License - see `LICENSE`.