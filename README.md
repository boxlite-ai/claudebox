# ClaudeBox

**Run Claude Code CLI in isolated micro-VMs with persistent workspaces, modular skills, and RL training support.**

[![Build Status](https://img.shields.io/github/actions/workflow/status/boxlite-labs/claudebox/ci.yml)](https://github.com/boxlite-labs/claudebox/actions)
[![PyPI version](https://img.shields.io/pypi/v/claudebox.svg)](https://pypi.org/project/claudebox/)
[![Python](https://img.shields.io/pypi/pyversions/claudebox.svg)](https://pypi.org/project/claudebox/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![BoxLite Stars](https://img.shields.io/github/stars/boxlite-labs/boxlite?style=social)](https://github.com/boxlite-labs/boxlite)

---

## 🎯 What is ClaudeBox?

ClaudeBox provides a secure, programmable environment for running **Claude Code** in hardware-isolated micro-VMs. Think of it as a "sandbox engineering" platform that combines:

- **🔒 Isolation** - Hardware-level security via micro-VMs (not containers)
- **💾 Persistence** - Workspaces that survive across sessions
- **🧩 Modularity** - Pre-load capabilities with skills (databases, APIs, cloud)
- **🏗️ Specialization** - Templates for web dev, data science, security research
- **🎯 Research** - RL training support with reward functions & trajectory export
- **🔐 Control** - Fine-grained security policies

**Powered by [BoxLite](https://github.com/boxlite-labs/boxlite)** - If you find ClaudeBox useful, please ⭐ [star BoxLite](https://github.com/boxlite-labs/boxlite) on GitHub!

---

## ✨ Features

### Core Capabilities

- **🔒 Hardware Isolation** - Micro-VM sandboxing via BoxLite (libkrun/Firecracker)
- **🤖 Claude Code Integration** - Full agentic capabilities (bash, files, network, GUI)
- **⚡ Easy API** - Simple async Python interface

### Session Management

- **💾 Persistent Sessions** - Workspaces at `~/.claudebox/sessions/` that survive VM shutdown
- **🔄 Reconnection** - Resume long-running projects across multiple runs
- **🗂️ Session Listing** - Enumerate and manage all active sessions
- **🧹 Cleanup Control** - Manual or automatic workspace cleanup

### Extensibility

- **🧩 Modular Skills** - 9 built-in skills + custom skill creation
  - Email (SendGrid)
  - Databases (PostgreSQL, MySQL, Redis)
  - APIs (requests/httpx)
  - Cloud (AWS SDK)
  - Docker CLI
  - Web scraping (BeautifulSoup, Playwright)
  - Data science (pandas, numpy, matplotlib)

- **🏗️ Sandbox Templates** - 6 pre-configured environments
  - Web Development (Node.js, TypeScript, Docker)
  - Data Science (Jupyter, pandas, scikit-learn)
  - Security Research (nmap, wireshark) *for authorized use*
  - DevOps (Docker, Kubernetes CLI)
  - Mobile Development
  - Custom Docker images

### RL Training Support

- **🎯 Reward Functions** - 5 built-in + custom reward creation
  - Success-only (binary reward)
  - Code quality (metrics-based)
  - Safety (penalize unsafe commands)
  - Efficiency (optimize tool usage)
  - Custom (define your own logic)

- **📊 Trajectory Export** - Training data for RL research
  - State-action pair extraction
  - Trajectory merging across sessions
  - JSON/JSONL export formats

### Security & Control

- **🔐 Security Policies** - 5 pre-defined + custom policies
  - Network access control (full/restricted/none)
  - Filesystem isolation (full/workspace-only/read-only)
  - Command blocking and whitelisting
  - Resource limits (CPU, memory, disk, time)
  - Domain whitelisting/blacklisting

- **📊 Observability** - Structured logging & metrics
  - JSON Lines action logging (`history.jsonl`)
  - Session metadata tracking
  - Resource usage metrics
  - Historical analytics

---

## 🚀 Quick Start

### Installation

```bash
pip install claudebox
```

### Prerequisites

- Python 3.9+
- [BoxLite](https://github.com/boxlite-labs/boxlite) micro-VM runtime
- Docker (for BoxLite)

### Authentication

Set your Claude Code OAuth token:

```bash
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

Or use Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Basic Usage

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    # Ephemeral session (auto-cleanup)
    async with ClaudeBox() as box:
        result = await box.code("Create a hello world Python script")
        print(result.response)

asyncio.run(main())
```

### Persistent Session

```python
from claudebox import ClaudeBox

async def main():
    # Create persistent session
    async with ClaudeBox(session_id="my-project") as box:
        await box.code("Initialize a Node.js project with Express")

    # Reconnect later (workspace persists)
    async with ClaudeBox.reconnect("my-project") as box:
        await box.code("Add authentication endpoints")

    # Clean up when done
    await ClaudeBox.cleanup_session("my-project", remove_workspace=True)

asyncio.run(main())
```

### With Skills & Templates

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

---

## 📚 Documentation

### Getting Started
- [Installation Guide](docs/getting-started/installation.md)
- [Quick Start Tutorial](docs/getting-started/quick-start.md)
- [Authentication Setup](docs/getting-started/authentication.md)
- [Your First Session](docs/getting-started/first-session.md)

### User Guides
- [Session Management](docs/guides/sessions.md) - Persistent vs ephemeral sessions
- [Skills System](docs/guides/skills.md) - Using & creating skills
- [Sandbox Templates](docs/guides/templates.md) - Specialized environments
- [Security Policies](docs/guides/security.md) - Fine-grained control
- [RL Training](docs/guides/rl-training.md) - Reward functions & trajectories
- [Workspace Management](docs/guides/workspace.md) - Directory structure & persistence

### API Reference
- [ClaudeBox Class](docs/api-reference/claudebox.md)
- [Skills API](docs/api-reference/skills.md)
- [Templates API](docs/api-reference/templates.md)
- [Rewards API](docs/api-reference/rewards.md)
- [Security API](docs/api-reference/security.md)
- [Result Types](docs/api-reference/results.md)

### Architecture
- [System Overview](docs/architecture/overview.md)
- [Workspace Structure](docs/architecture/workspace.md)
- [BoxLite Integration](docs/architecture/boxlite.md)
- [Security Model](docs/architecture/security-model.md)

### Advanced Topics
- [Custom Skills](docs/advanced/custom-skills.md)
- [Production Deployment](docs/advanced/production.md)
- [Performance Tuning](docs/advanced/performance.md)
- [RL Best Practices](docs/advanced/rl-best-practices.md)

### Troubleshooting
- [Common Issues](docs/troubleshooting/common-issues.md)
- [Debugging Guide](docs/troubleshooting/debugging.md)
- [FAQ](docs/troubleshooting/faq.md)

---

## 🎨 Examples

**71 comprehensive examples** across 6 files demonstrating all features. See [examples/README.md](examples/README.md) for details.

| Example File | Examples | Focus Area |
|-------------|----------|------------|
| [01_basic_usage.py](examples/01_basic_usage.py) | 8 | Session management, persistence, reconnection |
| [02_skills.py](examples/02_skills.py) | 10 | All 9 built-in skills + custom skill creation |
| [03_templates.py](examples/03_templates.py) | 13 | All 6 templates + custom Docker images |
| [04_rl_rewards.py](examples/04_rl_rewards.py) | 13 | All 5 reward functions + trajectory export |
| [05_security.py](examples/05_security.py) | 15 | All 5 security policies + enforcement |
| [06_advanced.py](examples/06_advanced.py) | 12 | Production patterns, multi-session workflows |

### Quick Examples

<details>
<summary><strong>Persistent Sessions</strong></summary>

```python
from claudebox import ClaudeBox

# Day 1: Initialize project
async with ClaudeBox(session_id="web-app") as box:
    await box.code("Create a React app with TypeScript")

# Day 2: Add features (reconnect to same workspace)
box = await ClaudeBox.reconnect("web-app")
async with box:
    await box.code("Add authentication with JWT")

# Day 3: Testing
box = await ClaudeBox.reconnect("web-app")
async with box:
    await box.code("Write unit tests with Jest")
```
</details>

<details>
<summary><strong>Skills System</strong></summary>

```python
from claudebox import ClaudeBox, Skill, EMAIL_SKILL, POSTGRES_SKILL

# Use built-in skills
async with ClaudeBox(skills=[EMAIL_SKILL, POSTGRES_SKILL]) as box:
    await box.code("Send email notification and log to PostgreSQL")

# Create custom skill
notification_skill = Skill(
    name="slack",
    description="Send Slack notifications",
    install_cmd="pip3 install slack-sdk",
    requirements=["slack-sdk"],
    env_vars={"SLACK_TOKEN": "xoxb-..."}
)

async with ClaudeBox(skills=[notification_skill]) as box:
    await box.code("Send 'Build completed' to #engineering")
```
</details>

<details>
<summary><strong>Sandbox Templates</strong></summary>

```python
from claudebox import ClaudeBox, SandboxTemplate

# Data science environment
async with ClaudeBox(template=SandboxTemplate.DATA_SCIENCE) as box:
    await box.code("Load dataset, train model, plot results")

# Web development environment
async with ClaudeBox(template=SandboxTemplate.WEB_DEV) as box:
    await box.code("Create Express API with TypeScript")

# Security research (authorized use only)
async with ClaudeBox(template=SandboxTemplate.SECURITY) as box:
    await box.code("Scan localhost for open ports")
```
</details>

<details>
<summary><strong>RL Training</strong></summary>

```python
from claudebox import ClaudeBox, CodeQualityReward, TrajectoryExporter

# Collect training data
async with ClaudeBox(reward_fn=CodeQualityReward()) as box:
    result = await box.code("Implement binary search")
    print(f"Reward: {result.reward:.2f}")

    # Export trajectory
    exporter = TrajectoryExporter(box._session_workspace, box._session_manager)
    trajectory = exporter.export_trajectory()
    exporter.save_to_file("training_data/trajectory_001.json")
```
</details>

<details>
<summary><strong>Security Policies</strong></summary>

```python
from claudebox import ClaudeBox, SecurityPolicy, RESTRICTED_POLICY

# Use pre-defined policy
async with ClaudeBox(security_policy=RESTRICTED_POLICY) as box:
    # Workspace-only filesystem, restricted network
    await box.code("Process sensitive data")

# Create custom policy
secure_policy = SecurityPolicy(
    network_access="restricted",
    file_system="workspace_only",
    allowed_domains=["*.github.com", "*.npmjs.com"],
    blocked_commands=["rm -rf", "sudo"],
    max_disk_usage_gb=5,
    max_memory_mb=2048
)

async with ClaudeBox(security_policy=secure_policy) as box:
    await box.code("Run untrusted code")
```
</details>

---

## 🏗️ API Overview

### ClaudeBox Class

```python
ClaudeBox(
    # Session Management
    session_id: str | None = None,              # Persistent session ID
    workspace_dir: str | None = None,           # Custom workspace location
    enable_logging: bool = True,                # Structured logging

    # Extensibility
    skills: list[Skill] | None = None,          # Pre-load capabilities
    template: SandboxTemplate | str | None = None,  # Sandbox environment

    # RL Training
    reward_fn: Callable[[CodeResult], float] | None = None,  # Reward function

    # Security
    security_policy: SecurityPolicy | None = None,  # Security controls

    # Resources (inherited from BoxLite)
    cpus: int = 4,
    memory_mib: int = 4096,
    disk_size_gb: int = 8,

    # Authentication
    oauth_token: str | None = None,             # OAuth token
    api_key: str | None = None,                 # API key

    # Advanced
    image: str | None = None,                   # Custom Docker image
    volumes: list | None = None,                # Additional volumes
    ports: list | None = None,                  # Port mappings
    env: list | None = None,                    # Environment variables
    auto_remove: bool | None = None,            # Auto-cleanup (default: True if no session_id)
)
```

### Key Methods

```python
# Execute Claude Code
result = await box.code(
    prompt: str,                    # Natural language instruction
    max_turns: int = 10,            # Maximum conversation turns
    allowed_tools: list | None = None,      # Tools to allow
    disallowed_tools: list | None = None,   # Tools to block
)

# Session management
sessions = ClaudeBox.list_sessions(workspace_dir=None)
box = await ClaudeBox.reconnect(session_id: str, ...)
await ClaudeBox.cleanup_session(session_id: str, remove_workspace=False)

# Observability
metrics = await box.get_metrics()              # Current resource usage
history = await box.get_history_metrics()      # Historical metrics
```

### Result Types

```python
class CodeResult:
    success: bool                   # Execution succeeded
    response: str                   # Claude's response
    error: str | None              # Error message if failed
    exit_code: int                 # Exit code
    reward: float | None           # Reward (if reward_fn provided)
    action_log: list[ActionLog]    # Structured action history
```

---

## 🔒 Why BoxLite?

ClaudeBox leverages [BoxLite](https://github.com/boxlite-labs/boxlite) for **true hardware isolation** via micro-VMs:

- **Real Security** - Hardware-level isolation, not just process separation
- **Lightweight** - Micro-VMs start in seconds
- **Full Desktop** - Run GUI applications with window managers
- **Cross-Platform** - macOS (Apple Silicon & Intel) and Linux

**⭐ [Star BoxLite on GitHub](https://github.com/boxlite-labs/boxlite)** to support the infrastructure that makes ClaudeBox possible!

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Development setup
- Coding standards
- Pull request process
- Testing requirements
- Contributing new skills

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

### Recent Changes (v0.1.2)

- ✅ Session persistence with workspace management
- ✅ 9 built-in skills + custom skill creation
- ✅ 6 sandbox templates
- ✅ 5 reward functions for RL training
- ✅ 5 security policies with enforcement
- ✅ Structured logging & trajectory export
- ✅ Comprehensive examples (71 examples)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **BoxLite Team** - For the micro-VM runtime that powers ClaudeBox
- **Anthropic** - For Claude Code and the Claude API
- **Contributors** - Everyone who has contributed code, docs, and feedback

---

## 🔗 Links

- **GitHub**: https://github.com/boxlite-labs/claudebox
- **PyPI**: https://pypi.org/project/claudebox/
- **BoxLite**: https://github.com/boxlite-labs/boxlite
- **Documentation**: [docs/](docs/)
- **Examples**: [examples/](examples/)
- **Issues**: https://github.com/boxlite-labs/claudebox/issues
- **Discussions**: https://github.com/boxlite-labs/claudebox/discussions

---

<p align="center">
  <strong>Built with ❤️ by the BoxLite Labs team</strong><br>
  If you find ClaudeBox useful, please ⭐ <a href="https://github.com/boxlite-labs/boxlite">star BoxLite on GitHub</a>!
</p>
