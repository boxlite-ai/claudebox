# Workspace Management Guide

Understand ClaudeBox workspace structure, persistence, and file access patterns.

---

## Overview

ClaudeBox **workspaces** are host-mounted directories that persist your session files:

- **Location:** `~/.claudebox/sessions/{session_id}/`
- **Persistence:** Files survive VM shutdown
- **Access:** Available from both host and VM
- **Version Control:** Can use git directly

---

## Workspace Directory Structure

```
~/.claudebox/
└── sessions/
    └── {session_id}/
        ├── workspace/          # Your project files (mounted in VM)
        │   ├── code/
        │   ├── data/
        │   ├── output/
        │   └── ...
        └── .claudebox/        # Metadata (mounted in VM)
            ├── session.json   # Session metadata
            └── history.jsonl  # Action log
```

### workspace/

**Purpose:** Your project files and code

**Mounted at:** `/config/workspace/` in VM

**Contents:**
- Source code
- Data files
- Build artifacts
- Dependencies (node_modules, venv, etc.)
- Any files created by Claude Code

**Access:**
```bash
# From host
cd ~/.claudebox/sessions/my-project/workspace/
ls -la

# From VM (during session)
cd /config/workspace/
ls -la
```

### .claudebox/

**Purpose:** Session metadata and logs

**Mounted at:** `/config/.claudebox/` in VM

**Contents:**
- `session.json` - Session metadata
- `history.jsonl` - Action log (JSON Lines)

---

## Session Metadata (session.json)

**Location:** `~/.claudebox/sessions/{session_id}/.claudebox/session.json`

**Structure:**
```json
{
  "session_id": "my-project",
  "box_id": "box-abc123",
  "created_at": "2025-01-01T10:00:00.000000",
  "updated_at": "2025-01-01T10:30:00.000000",
  "total_commands": 15,
  "total_files_created": 8,
  "workspace_path": "/Users/name/.claudebox/sessions/my-project/workspace"
}
```

**Reading metadata:**
```python
import json

def read_session_metadata(session_id):
    with open(f"~/.claudebox/sessions/{session_id}/.claudebox/session.json") as f:
        return json.load(f)

metadata = read_session_metadata("my-project")
print(f"Created: {metadata['created_at']}")
print(f"Files: {metadata['total_files_created']}")
```

---

## Action History (history.jsonl)

**Location:** `~/.claudebox/sessions/{session_id}/.claudebox/history.jsonl`

**Format:** JSON Lines (one JSON object per line)

**Example:**
```jsonl
{"timestamp": "2025-01-01T10:00:00", "action": "session_created", "context": {"session_id": "my-project"}}
{"timestamp": "2025-01-01T10:01:00", "action": "code_execution", "context": {"prompt": "Create app.py", "success": true}}
{"timestamp": "2025-01-01T10:02:00", "action": "file_created", "context": {"file": "app.py", "size": 1024}}
```

**Reading history:**
```python
import json

def read_action_history(session_id):
    actions = []
    history_file = f"~/.claudebox/sessions/{session_id}/.claudebox/history.jsonl"

    with open(history_file) as f:
        for line in f:
            actions.append(json.loads(line))

    return actions

history = read_action_history("my-project")
for action in history:
    print(f"{action['timestamp']}: {action['action']}")
```

---

## Volume Mounting

### How It Works

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  HOST MACHINE                                      │
│  ────────────                                      │
│                                                     │
│  ~/.claudebox/sessions/my-project/                │
│  │                                                  │
│  ├── workspace/          ← Your files             │
│  │   └── app.py                                    │
│  │                                                  │
│  └── .claudebox/         ← Metadata               │
│      ├── session.json                              │
│      └── history.jsonl                             │
│                                                     │
└─────────────────────────────────────────────────────┘
                        ↕
              VOLUME MOUNT (bidirectional)
                        ↕
┌─────────────────────────────────────────────────────┐
│                                                     │
│  MICRO-VM (BoxLite)                                │
│  ──────────────────                                │
│                                                     │
│  /config/workspace/      ← Mounted from host      │
│  │                                                  │
│  └── app.py              ← Same file!             │
│                                                     │
│  /config/.claudebox/     ← Mounted from host      │
│  │                                                  │
│  ├── session.json                                  │
│  └── history.jsonl                                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Key points:**
- ✅ **Bidirectional** - Changes sync both ways
- ✅ **Real-time** - Instant file updates
- ✅ **Persistent** - Files survive VM restart
- ✅ **Accessible** - Edit from host or VM

---

## Accessing Workspace Files

### From Host

**View files:**
```bash
# List files
ls -la ~/.claudebox/sessions/my-project/workspace/

# View file content
cat ~/.claudebox/sessions/my-project/workspace/app.py

# Edit with your favorite editor
code ~/.claudebox/sessions/my-project/workspace/
```

**Direct access in code:**
```python
async with ClaudeBox(session_id="my-project") as box:
    print(f"Workspace: {box.workspace_path}")
    # /Users/name/.claudebox/sessions/my-project/workspace

# Access files from host
import os
workspace = os.path.expanduser("~/.claudebox/sessions/my-project/workspace")
with open(f"{workspace}/app.py") as f:
    code = f.read()
```

### From VM

**During session:**
```python
async with ClaudeBox(session_id="my-project") as box:
    await box.code("ls -la /config/workspace/")
    await box.code("cat /config/workspace/app.py")
```

---

## Workspace Patterns

### Pattern 1: Pre-populate Workspace

```python
import os
import shutil

async def prepopulated_workspace():
    """Create session with pre-existing files."""
    session_id = "my-project"
    workspace = f"~/.claudebox/sessions/{session_id}/workspace"
    workspace = os.path.expanduser(workspace)

    # Create workspace directory
    os.makedirs(workspace, exist_ok=True)

    # Copy template files
    shutil.copy("templates/app.py", f"{workspace}/app.py")
    shutil.copy("templates/config.json", f"{workspace}/config.json")

    # Now start session with pre-populated files
    async with ClaudeBox(session_id=session_id) as box:
        await box.code("Review and modify app.py")
```

### Pattern 2: Share Workspace Between Sessions

```python
async def shared_workspace():
    """Two sessions accessing same data directory."""
    # Session 1: Data preparation
    async with ClaudeBox(session_id="data-prep") as box:
        await box.code("Download and clean dataset to data/")

    # Session 2: Analysis (copy data from session 1)
    import shutil
    shutil.copytree(
        "~/.claudebox/sessions/data-prep/workspace/data",
        "~/.claudebox/sessions/analysis/workspace/data"
    )

    async with ClaudeBox(session_id="analysis") as box:
        await box.code("Analyze data from data/ directory")
```

### Pattern 3: Version Control Integration

```python
async def git_workflow():
    """Use git to track workspace changes."""
    async with ClaudeBox(session_id="git-project") as box:
        # Initialize git
        await box.code("git init")
        await box.code("git add .")
        await box.code("git commit -m 'Initial commit'")

        # Make changes
        await box.code("Create feature.py")

        # Commit changes
        await box.code("git add feature.py")
        await box.code("git commit -m 'Add feature'")

    # Can also use git from host
    import subprocess
    workspace = "~/.claudebox/sessions/git-project/workspace"
    subprocess.run(["git", "log"], cwd=workspace)
```

### Pattern 4: Backup and Restore

```python
import shutil
from datetime import datetime

async def backup_workspace(session_id: str, backup_dir: str = "backups"):
    """Backup workspace to external directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace = f"~/.claudebox/sessions/{session_id}/workspace"
    backup_path = f"{backup_dir}/{session_id}_{timestamp}"

    shutil.copytree(workspace, backup_path)
    print(f"Backup created: {backup_path}")

async def restore_workspace(backup_path: str, session_id: str):
    """Restore workspace from backup."""
    workspace = f"~/.claudebox/sessions/{session_id}/workspace"

    # Remove existing workspace
    shutil.rmtree(workspace, ignore_errors=True)

    # Restore from backup
    shutil.copytree(backup_path, workspace)
    print(f"Restored from: {backup_path}")
```

---

## Workspace Cleanup

### Manual Cleanup

```bash
# Remove entire session
rm -rf ~/.claudebox/sessions/my-project/

# Keep metadata, remove workspace
rm -rf ~/.claudebox/sessions/my-project/workspace/

# Remove specific files
rm ~/.claudebox/sessions/my-project/workspace/temp.txt
```

### Programmatic Cleanup

```python
async def selective_cleanup(session_id: str):
    """Remove large files but keep code."""
    import os

    workspace = f"~/.claudebox/sessions/{session_id}/workspace"

    for root, dirs, files in os.walk(workspace):
        for file in files:
            filepath = os.path.join(root, file)
            size_mb = os.path.getsize(filepath) / (1024 * 1024)

            # Remove files > 10MB
            if size_mb > 10:
                os.remove(filepath)
                print(f"Removed large file: {file} ({size_mb:.2f} MB)")
```

---

## Disk Space Management

### Check Workspace Size

```python
import os

def get_workspace_size(session_id: str) -> float:
    """Get workspace size in MB."""
    workspace = f"~/.claudebox/sessions/{session_id}/workspace"
    workspace = os.path.expanduser(workspace)

    total_size = 0
    for root, dirs, files in os.walk(workspace):
        for file in files:
            filepath = os.path.join(root, file)
            total_size += os.path.getsize(filepath)

    return total_size / (1024 * 1024)  # Convert to MB

size = get_workspace_size("my-project")
print(f"Workspace size: {size:.2f} MB")
```

### Monitor All Sessions

```python
from claudebox import ClaudeBox

def monitor_disk_usage():
    """Monitor disk usage across all sessions."""
    sessions = ClaudeBox.list_sessions()

    total_size = 0
    for session in sessions:
        size = get_workspace_size(session.session_id)
        total_size += size
        print(f"{session.session_id}: {size:.2f} MB")

    print(f"\nTotal: {total_size:.2f} MB")
    return total_size
```

---

## Best Practices

### 1. Organize Workspace Structure

```python
async def organized_workspace():
    """Create organized directory structure."""
    async with ClaudeBox(session_id="organized-project") as box:
        await box.code("""
        Create directory structure:
        - src/ (source code)
        - tests/ (unit tests)
        - data/ (datasets)
        - output/ (results)
        - docs/ (documentation)
        """)
```

### 2. Use .gitignore

```python
async def gitignore_setup():
    """Add .gitignore for large files."""
    async with ClaudeBox(session_id="my-project") as box:
        await box.code("""
        Create .gitignore with:
        - node_modules/
        - venv/
        - __pycache__/
        - *.pyc
        - data/*.csv (large datasets)
        - output/*.png (generated files)
        """)
```

### 3. Regular Backups

```python
import schedule
import time

def backup_scheduler():
    """Schedule daily backups."""
    schedule.every().day.at("02:00").do(
        lambda: backup_workspace("my-project")
    )

    while True:
        schedule.run_pending()
        time.sleep(60)
```

### 4. Monitor Disk Usage

```python
async def disk_usage_check():
    """Alert if workspace exceeds limit."""
    size_mb = get_workspace_size("my-project")

    if size_mb > 1000:  # 1GB limit
        print(f"⚠️ Workspace exceeds 1GB: {size_mb:.2f} MB")
        print("Consider cleanup or archiving old files")
```

---

## Troubleshooting

### Issue: Permission Denied

**Error:** `Permission denied: ~/.claudebox/sessions/`

**Solution:**
```bash
# Fix permissions
chmod 755 ~/.claudebox/
chmod -R 755 ~/.claudebox/sessions/
```

### Issue: Workspace Files Not Visible

**Problem:** Files created in VM not showing on host

**Solution:** Check volume mount
```python
async with ClaudeBox(session_id="test") as box:
    print(box.workspace_path)  # Verify path
    await box.code("pwd")  # Should be /config/workspace
    await box.code("ls -la")  # List files
```

### Issue: Disk Space Full

**Error:** `OSError: No space left on device`

**Solution:**
```bash
# Check disk usage
du -sh ~/.claudebox/sessions/*

# Clean up old sessions
rm -rf ~/.claudebox/sessions/old-session/

# Or use cleanup_session
await ClaudeBox.cleanup_session("old-session", remove_workspace=True)
```

---

## Next Steps

- **[Sessions Guide](sessions.md)** - Session lifecycle management
- **[Examples](../../examples/)** - Workspace usage examples
- **[API Reference](../api-reference/claudebox.md)** - ClaudeBox API

---

**Master workspaces, control your data!**
