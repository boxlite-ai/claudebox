# ClaudeBox

[![BoxLite Stars](https://img.shields.io/github/stars/boxlite-labs/boxlite?style=social)](https://github.com/boxlite-labs/boxlite)

Run **Claude Code CLI** in isolated micro-VMs with desktop environment.

ClaudeBox provides a secure, sandboxed environment for running Claude Code with full capabilities—file system access, shell execution, network requests, and GUI desktop—all safely contained in hardware-isolated virtual machines.

**Powered by [BoxLite](https://github.com/boxlite-labs/boxlite)** - the lightweight micro-VM runtime that makes this security possible. If you find ClaudeBox useful, please ⭐ star BoxLite on GitHub to support the project!

## Features

- **Claude Code CLI**: Run prompts with full agentic capabilities
- **Desktop Environment**: XFCE desktop via webtop for computer use
- **Hardware Isolation**: All operations run in micro-VMs, not containers
- **Full Tool Access**: bash, file operations, web requests, GUI
- **OAuth Support**: Use your Claude Max subscription

## ⭐ Support BoxLite

ClaudeBox is built on [BoxLite](https://github.com/boxlite-labs/boxlite), an open-source micro-VM runtime that enables secure, isolated execution environments.

**[Star BoxLite on GitHub →](https://github.com/boxlite-labs/boxlite)**

Your support helps maintain and improve the infrastructure that makes ClaudeBox possible!

## Quick Start

```bash
pip install claudebox
```

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    async with ClaudeBox() as box:
        result = await box.code("Create a hello world Python script")
        print(result.response)

asyncio.run(main())
```

## Authentication

Set one of these environment variables:

```bash
# Claude Max subscription (OAuth token)
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...

# Or Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...
```

## Docker Image

The runtime image (`ghcr.io/boxlite-labs/claudebox-runtime`) includes:
- Ubuntu with XFCE desktop (webtop)
- Node.js and npm
- Claude Code CLI pre-installed

### Build locally

```bash
cd image
./build.sh           # builds :latest
./build.sh v1.0.0    # builds :v1.0.0 and :latest
```

## API

### ClaudeBox

```python
ClaudeBox(
    oauth_token: str = None,    # OAuth token (or CLAUDE_CODE_OAUTH_TOKEN env)
    api_key: str = None,        # API key (or ANTHROPIC_API_KEY env)
    image: str = "ghcr.io/boxlite-labs/claudebox-runtime:latest",
    cpus: int = 4,
    memory_mib: int = 4096,
    disk_size_gb: int = 8,
    volumes: list = None,       # [(host_path, guest_path), ...]
    ports: list = None,         # [(host_port, guest_port), ...]
    env: list = None,           # [("KEY", "VALUE"), ...]
    auto_remove: bool = True,
)
```

### Run Prompts

```python
result = await box.code(
    prompt="Fix the bug in main.py",
    max_turns=10,
    allowed_tools=["bash", "read_file"],
    disallowed_tools=["web_search"],
)

print(result.success)    # bool
print(result.response)   # Claude's response
print(result.error)      # Error message if failed
```

## Why BoxLite?

ClaudeBox leverages [BoxLite](https://github.com/boxlite-labs/boxlite) to provide true hardware isolation through micro-VMs instead of containers. This means:

- **Real Security**: Hardware-level isolation, not just process separation
- **Full Desktop**: Run GUI applications with actual window managers
- **Lightweight**: Micro-VMs that start in seconds, not minutes
- **Cross-Platform**: Works on macOS (Apple Silicon & Intel) and Linux

BoxLite is open-source and community-driven. If ClaudeBox helps you build safer AI applications, consider:

**⭐ [Starring BoxLite on GitHub](https://github.com/boxlite-labs/boxlite)** to show your support and help more developers discover this technology!

## Requirements

- Python 3.10+
- [BoxLite](https://github.com/boxlite-labs/boxlite) runtime
- macOS (Apple Silicon or Intel) or Linux

## License

MIT
