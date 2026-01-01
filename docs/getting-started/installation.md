# Installation Guide

Get ClaudeBox up and running on your system in minutes.

---

## Prerequisites

Before installing ClaudeBox, ensure you have the following:

### Required

- **Python 3.9 or higher**
  ```bash
  python3 --version  # Should show 3.9+
  ```

- **Docker** - Required for BoxLite micro-VM runtime
  ```bash
  docker --version  # Should show Docker 20.10+
  ```

  - **macOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

- **BoxLite** - Micro-VM runtime (installation covered below)

### Optional

- **Git** - For installing from source
- **Virtual environment tool** - `venv`, `virtualenv`, or `conda`

---

## Installation Methods

Choose the method that best fits your workflow.

### Method 1: Install from PyPI (Recommended)

The simplest way to install ClaudeBox:

```bash
pip install claudebox
```

This installs the latest stable release from PyPI.

**Verify installation:**
```bash
python3 -c "import claudebox; print(claudebox.__version__)"
```

### Method 2: Install from Source

For development or to use the latest unreleased features:

```bash
# Clone the repository
git clone https://github.com/boxlite-labs/claudebox.git
cd claudebox

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

**Development dependencies include:**
- `pytest` - Testing framework
- `ruff` - Linter and formatter
- `mypy` - Type checker
- `pre-commit` - Git hooks

**Verify installation:**
```bash
python3 -c "import claudebox; print(claudebox.__version__)"
```

### Method 3: Install with Docker

If you prefer containerized development:

```bash
# Pull the ClaudeBox runtime image
docker pull ghcr.io/boxlite-labs/claudebox-runtime:latest

# Use with ClaudeBox Python API
python3 -c "from claudebox import ClaudeBox; print('Ready!')"
```

---

## Installing BoxLite

ClaudeBox requires [BoxLite](https://github.com/boxlite-labs/boxlite) for micro-VM isolation.

### macOS

```bash
# Install BoxLite CLI
brew install boxlite-labs/tap/boxlite

# Verify installation
boxlite version
```

**Note**: On Apple Silicon Macs, BoxLite uses libkrun. On Intel Macs, it uses Firecracker.

### Linux

```bash
# Install BoxLite from GitHub releases
curl -fsSL https://raw.githubusercontent.com/boxlite-labs/boxlite/main/install.sh | sh

# Verify installation
boxlite version
```

### Troubleshooting BoxLite Installation

**Issue**: `boxlite: command not found`

**Solution**: Add BoxLite to your PATH:
```bash
export PATH="$HOME/.boxlite/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc for persistence
```

**Issue**: Docker permission errors

**Solution**:
```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect

# macOS: Ensure Docker Desktop is running
```

For more BoxLite issues, see the [BoxLite troubleshooting guide](https://github.com/boxlite-labs/boxlite#troubleshooting).

---

## Authentication Setup

ClaudeBox requires authentication to use Claude Code. Choose one method:

### Option 1: Claude Code OAuth Token (Recommended)

Get your OAuth token from Claude.ai:

1. Go to https://claude.ai/settings/developer
2. Create a new OAuth token
3. Copy the token (starts with `sk-ant-oat01-...`)

Set the environment variable:

```bash
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN-HERE

# Make it persistent (add to ~/.bashrc or ~/.zshrc)
echo 'export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN-HERE' >> ~/.bashrc
source ~/.bashrc
```

### Option 2: Anthropic API Key

Alternatively, use an Anthropic API key:

1. Go to https://console.anthropic.com/settings/keys
2. Create a new API key
3. Copy the key (starts with `sk-ant-...`)

Set the environment variable:

```bash
export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE

# Make it persistent
echo 'export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE' >> ~/.bashrc
source ~/.bashrc
```

**Note**: OAuth tokens are preferred for Claude Code integration. API keys work but may have different rate limits.

---

## Verify Installation

Run a quick test to ensure everything is working:

```python
import asyncio
from claudebox import ClaudeBox

async def test():
    async with ClaudeBox() as box:
        result = await box.code("print('Hello from ClaudeBox!')")
        print(result.response)
        return result.success

if __name__ == "__main__":
    success = asyncio.run(test())
    if success:
        print("✅ ClaudeBox is working correctly!")
    else:
        print("❌ Something went wrong. Check troubleshooting section below.")
```

Save as `test_install.py` and run:

```bash
python3 test_install.py
```

**Expected output:**
```
✅ ClaudeBox is working correctly!
```

---

## Troubleshooting

### Common Installation Issues

#### Issue: `ModuleNotFoundError: No module named 'claudebox'`

**Cause**: ClaudeBox not installed or not in Python path

**Solution**:
```bash
# Verify pip installation
pip list | grep claudebox

# Reinstall if missing
pip install --force-reinstall claudebox
```

#### Issue: `ImportError: cannot import name 'Boxlite'`

**Cause**: BoxLite not installed or not accessible

**Solution**:
```bash
# Verify BoxLite installation
boxlite version

# Ensure Docker is running
docker ps

# Reinstall BoxLite if needed
```

#### Issue: `Authentication error: No token found`

**Cause**: Environment variables not set

**Solution**:
```bash
# Check if token is set
echo $CLAUDE_CODE_OAUTH_TOKEN

# If empty, set it
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN-HERE
```

#### Issue: `Permission denied` when creating sessions

**Cause**: Insufficient permissions for `~/.claudebox/` directory

**Solution**:
```bash
# Check permissions
ls -la ~/.claudebox/

# Fix permissions if needed
chmod 755 ~/.claudebox/
chmod -R 755 ~/.claudebox/sessions/
```

#### Issue: `Docker daemon not running`

**Cause**: Docker Desktop not started (macOS) or Docker service not running (Linux)

**Solution**:
```bash
# macOS: Start Docker Desktop from Applications

# Linux: Start Docker service
sudo systemctl start docker
sudo systemctl enable docker  # Auto-start on boot
```

#### Issue: `Out of disk space` errors

**Cause**: ClaudeBox sessions using too much disk space

**Solution**:
```bash
# Check disk usage
du -sh ~/.claudebox/sessions/

# Clean up old sessions (see cleanup guide)
# Or increase disk limit in ClaudeBox constructor
```

### Getting Help

If you're still having issues:

1. **Check the [FAQ](../troubleshooting/faq.md)** for common questions
2. **Search [GitHub Issues](https://github.com/boxlite-labs/claudebox/issues)**
3. **Ask in [GitHub Discussions](https://github.com/boxlite-labs/claudebox/discussions)**
4. **File a [new issue](https://github.com/boxlite-labs/claudebox/issues/new)** with:
   - Python version (`python3 --version`)
   - Docker version (`docker --version`)
   - BoxLite version (`boxlite version`)
   - Error message and full traceback
   - Steps to reproduce

---

## What's Next?

Now that ClaudeBox is installed, continue with:

- **[Quick Start Tutorial](quick-start.md)** - 5-minute hands-on introduction
- **[Authentication Guide](authentication.md)** - Detailed authentication setup
- **[Your First Session](first-session.md)** - Interactive tutorial
- **[Examples](../../examples/)** - 71 comprehensive examples

---

## System Requirements

### Minimum Requirements

- **CPU**: 2 cores (4 cores recommended)
- **RAM**: 4 GB (8 GB recommended)
- **Disk**: 10 GB free space
- **OS**:
  - macOS 11+ (Big Sur or later)
  - Linux with kernel 5.10+ (Ubuntu 20.04+, Debian 11+, Fedora 33+)

### Recommended for Production

- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 50+ GB SSD
- **Network**: Stable internet connection for Claude Code API

---

## Supported Platforms

| Platform | Architecture | Status |
|----------|-------------|--------|
| macOS | Apple Silicon (M1/M2/M3) | ✅ Fully supported |
| macOS | Intel (x86_64) | ✅ Fully supported |
| Linux | x86_64 | ✅ Fully supported |
| Linux | ARM64 | ⚠️ Experimental |
| Windows | WSL2 | ⚠️ Experimental |
| Windows | Native | ❌ Not supported |

**Note**: Windows users should use WSL2 (Windows Subsystem for Linux 2) with Docker Desktop.

---

## Upgrade Guide

### Upgrading ClaudeBox

```bash
# Upgrade to latest version
pip install --upgrade claudebox

# Upgrade to specific version
pip install claudebox==0.1.2

# Verify new version
python3 -c "import claudebox; print(claudebox.__version__)"
```

### Upgrading BoxLite

```bash
# macOS
brew upgrade boxlite

# Linux
curl -fsSL https://raw.githubusercontent.com/boxlite-labs/boxlite/main/install.sh | sh
```

### Breaking Changes

See [CHANGELOG.md](../../CHANGELOG.md) for breaking changes between versions.

**v0.1.2 → v0.1.3**: No breaking changes expected
**v0.1.1 → v0.1.2**: Session workspace structure changed (automatic migration)

---

## Uninstalling

To completely remove ClaudeBox:

```bash
# Uninstall Python package
pip uninstall claudebox

# Remove session data (CAUTION: This deletes all workspaces!)
rm -rf ~/.claudebox/

# Uninstall BoxLite (optional)
# macOS
brew uninstall boxlite

# Linux
rm -rf ~/.boxlite/
```

**Warning**: Removing `~/.claudebox/` will delete all persistent session workspaces. Back up any important data first.

---

## Development Installation

For contributors developing ClaudeBox:

```bash
# Clone repository
git clone https://github.com/boxlite-labs/claudebox.git
cd claudebox

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Run linter
ruff check src/ tests/

# Run type checker
mypy src/claudebox/
```

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for detailed development setup.

---

**Installation complete!** Continue to [Quick Start](quick-start.md) →
