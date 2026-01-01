# Session Management Guide

Master persistent and ephemeral sessions in ClaudeBox for efficient project workflows.

---

## Overview

Sessions are ClaudeBox's persistence mechanism. They determine whether your work survives after the micro-VM stops.

**Two session types:**
1. **Ephemeral Sessions** - Temporary, auto-cleanup
2. **Persistent Sessions** - Survive across runs, manual cleanup

---

## Ephemeral vs Persistent Sessions

### Ephemeral Sessions

**Definition:** Temporary sessions that auto-delete when the context manager exits.

**Creating ephemeral sessions:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    # No session_id = ephemeral
    async with ClaudeBox() as box:
        result = await box.code("Create hello.py")
        print(result.response)
    # Workspace automatically deleted here

asyncio.run(main())
```

**Characteristics:**
- ✅ **Auto-cleanup** - No manual cleanup needed
- ✅ **Simple** - Just create and use
- ❌ **Non-persistent** - Files deleted on exit
- ❌ **No reconnection** - Cannot resume work

**When to use:**
- Quick one-off tasks
- Temporary analysis
- Testing/experimentation
- Tasks that don't need preserved output

### Persistent Sessions

**Definition:** Named sessions with workspaces that survive VM shutdown.

**Creating persistent sessions:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    # With session_id = persistent
    async with ClaudeBox(session_id="my-project") as box:
        result = await box.code("Create project structure")
        print(f"Workspace: {box.workspace_path}")
    # Workspace persists at ~/.claudebox/sessions/my-project/

asyncio.run(main())
```

**Characteristics:**
- ✅ **Persistent** - Files survive VM shutdown
- ✅ **Reconnectable** - Resume work later
- ✅ **Inspectable** - Workspace accessible from host
- ✅ **Versioned** - Can use git for version control
- ⚠️ **Manual cleanup** - Must explicitly clean up

**When to use:**
- Multi-day projects
- Iterative development
- Work you need to inspect from host
- Projects requiring version control

---

## Session Lifecycle

### Complete Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. CREATE SESSION                                             │
│  ─────────────────                                             │
│                                                                 │
│  ClaudeBox(session_id="proj")                                 │
│         ↓                                                       │
│  Session created                                               │
│  Workspace: ~/.claudebox/sessions/proj/workspace/             │
│  Metadata: ~/.claudebox/sessions/proj/.claudebox/             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  2. WORK IN SESSION (Day 1)                                   │
│  ───────────────────────                                       │
│                                                                 │
│  async with ClaudeBox(session_id="proj") as box:              │
│      await box.code("Initialize project")                     │
│      await box.code("Add feature A")                          │
│         ↓                                                       │
│  Files created in workspace/                                   │
│  Actions logged to .claudebox/history.jsonl                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  3. SESSION EXIT                                               │
│  ───────────────                                               │
│                                                                 │
│  # Context manager exits                                       │
│         ↓                                                       │
│  VM stops, but workspace persists!                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  4. RECONNECT (Day 2, 3, ...)                                 │
│  ──────────────────────────                                    │
│                                                                 │
│  async with ClaudeBox.reconnect("proj") as box:               │
│      await box.code("Add feature B")                          │
│         ↓                                                       │
│  Same workspace, continue where left off                      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  5. CLEANUP (When finished)                                    │
│  ────────────────────────                                      │
│                                                                 │
│  await ClaudeBox.cleanup_session("proj",                      │
│                                  remove_workspace=True)        │
│         ↓                                                       │
│  Session & workspace deleted                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### State Transitions

```
┌──────────────┐
│   NOT        │  ClaudeBox(session_id="x")
│   EXISTS     │──────────────────────────────┐
└──────────────┘                              │
                                              ↓
                                    ┌──────────────────┐
       ClaudeBox.reconnect("x") ←───│   CREATED        │
                │                   │   (stopped)      │
                │                   └──────────────────┘
                │                           │
                │                           │ async with ...
                │                           ↓
                │                   ┌──────────────────┐
                └──────────────────→│   RUNNING        │
                                    │   (VM active)    │
                                    └──────────────────┘
                                           │
                                           │ exit context
                                           ↓
                                    ┌──────────────────┐
                                    │   STOPPED        │
                                    │   (workspace OK) │
                                    └──────────────────┘
                                           │
                                           │ cleanup_session()
                                           ↓
                                    ┌──────────────────┐
                                    │   DELETED        │
                                    └──────────────────┘
```

---

## Session ID Naming Conventions

### Best Practices

**Good session IDs:**
```python
# ✅ Descriptive, kebab-case
"web-api-server"
"data-analysis-2024"
"ml-training-experiment"

# ✅ Project-based
"customer-dashboard"
"auth-service"
"analytics-pipeline"

# ✅ Date-stamped for experiments
"experiment-2024-01-15"
"test-run-20240115"
```

**Bad session IDs:**
```python
# ❌ Too generic
"test"
"demo"
"temp"

# ❌ Spaces (will cause issues)
"my project"
"web app"

# ❌ Special characters
"project@123"
"app#1"
"test/version"
```

### Naming Rules

- **Allowed characters:** `a-z`, `A-Z`, `0-9`, `-`, `_`
- **Avoid:** Spaces, special characters (@, #, /, etc.)
- **Max length:** 255 characters (but keep it short)
- **Case-sensitive:** "Project" ≠ "project"

### Organizational Strategies

**By project:**
```python
"frontend-app"
"backend-api"
"database-migration"
```

**By environment:**
```python
"dev-environment"
"staging-test"
"prod-analysis"
```

**By feature:**
```python
"feature-user-auth"
"feature-payment-gateway"
"feature-analytics-dashboard"
```

**By date (for experiments):**
```python
"exp-2024-01-15-model-a"
"exp-2024-01-16-model-b"
```

---

## Creating Sessions

### Ephemeral Session

```python
async def quick_task():
    async with ClaudeBox() as box:
        result = await box.code("Quick analysis task")
        # Process result
    # Auto-cleanup happens here
```

### Persistent Session (First Time)

```python
async def create_project():
    async with ClaudeBox(session_id="my-project") as box:
        result = await box.code("Initialize project structure")
        print(f"Workspace: {box.workspace_path}")
        # Workspace persists after exit
```

### Checking if Session Exists

```python
from claudebox import ClaudeBox, SessionNotFoundError

async def safe_create():
    session_id = "my-project"

    # Check if already exists
    sessions = ClaudeBox.list_sessions()
    exists = any(s.session_id == session_id for s in sessions)

    if exists:
        print(f"Session '{session_id}' exists, reconnecting...")
        async with ClaudeBox.reconnect(session_id) as box:
            ...
    else:
        print(f"Creating new session '{session_id}'...")
        async with ClaudeBox(session_id=session_id) as box:
            ...
```

---

## Reconnecting to Sessions

### Basic Reconnection

```python
async def reconnect_example():
    # Day 1: Create
    async with ClaudeBox(session_id="project") as box:
        await box.code("Initialize")

    # Day 2: Reconnect
    async with ClaudeBox.reconnect("project") as box:
        await box.code("Continue work")
```

### Safe Reconnection with Error Handling

```python
from claudebox import ClaudeBox, SessionNotFoundError

async def safe_reconnect(session_id: str):
    try:
        async with ClaudeBox.reconnect(session_id) as box:
            result = await box.code("Continue work")
            return result
    except SessionNotFoundError:
        print(f"Session '{session_id}' not found. Create it first!")
        return None
```

### Reconnect vs Create Logic

```python
async def smart_session(session_id: str):
    """Create if doesn't exist, reconnect if it does."""
    sessions = ClaudeBox.list_sessions()
    exists = any(s.session_id == session_id for s in sessions)

    if exists:
        box = await ClaudeBox.reconnect(session_id)
    else:
        box = ClaudeBox(session_id=session_id)

    async with box:
        # Work here
        result = await box.code("Task")
        return result
```

---

## Listing Sessions

### List All Sessions

```python
from claudebox import ClaudeBox

def list_all_sessions():
    sessions = ClaudeBox.list_sessions()

    for session in sessions:
        print(f"ID: {session.session_id}")
        print(f"Status: {session.status}")
        print(f"Created: {session.created_at}")
        print(f"Workspace: {session.workspace_path}")
        print()
```

### Filter Sessions

```python
def find_session(search_term: str):
    """Find sessions matching search term."""
    sessions = ClaudeBox.list_sessions()
    matches = [s for s in sessions if search_term in s.session_id]

    print(f"Found {len(matches)} matching session(s):")
    for session in matches:
        print(f"  - {session.session_id} (created {session.created_at})")
```

### Get Session Details

```python
import json

def get_session_info(session_id: str):
    """Get detailed info about a session."""
    import os
    session_file = os.path.expanduser(
        f"~/.claudebox/sessions/{session_id}/.claudebox/session.json"
    )

    if not os.path.exists(session_file):
        print(f"Session '{session_id}' not found")
        return None

    with open(session_file, 'r') as f:
        metadata = json.load(f)

    return metadata
```

---

## Session Cleanup

### Cleanup Options

**Option 1: Remove box, keep workspace**
```python
async def cleanup_keep_workspace():
    # Removes VM, keeps files for inspection
    await ClaudeBox.cleanup_session("my-project", remove_workspace=False)
    # Files still at ~/.claudebox/sessions/my-project/
```

**Option 2: Remove everything**
```python
async def cleanup_everything():
    # Removes VM and all workspace files
    await ClaudeBox.cleanup_session("my-project", remove_workspace=True)
    # ~/.claudebox/sessions/my-project/ deleted
```

### Cleanup Strategies

**Strategy 1: Manual cleanup after archiving**
```python
import shutil
import os

async def archive_and_cleanup(session_id: str, archive_dir: str):
    """Archive workspace before cleanup."""
    workspace = f"~/.claudebox/sessions/{session_id}/workspace"
    workspace = os.path.expanduser(workspace)

    # Archive to external location
    archive_path = f"{archive_dir}/{session_id}"
    shutil.copytree(workspace, archive_path)
    print(f"Archived to {archive_path}")

    # Now safe to cleanup
    await ClaudeBox.cleanup_session(session_id, remove_workspace=True)
    print(f"Cleaned up session '{session_id}'")
```

**Strategy 2: Cleanup old sessions automatically**
```python
from datetime import datetime, timedelta
import os

async def cleanup_old_sessions(days_old: int = 30):
    """Clean up sessions older than N days."""
    sessions = ClaudeBox.list_sessions()
    cutoff = datetime.now() - timedelta(days=days_old)

    for session in sessions:
        created = datetime.fromisoformat(session.created_at)
        if created < cutoff:
            print(f"Cleaning up old session: {session.session_id}")
            await ClaudeBox.cleanup_session(
                session.session_id,
                remove_workspace=True
            )
```

**Strategy 3: Cleanup with confirmation**
```python
async def cleanup_with_confirm(session_id: str):
    """Ask user before cleanup."""
    print(f"About to delete session '{session_id}' and all workspace files.")
    confirm = input("Are you sure? (yes/no): ")

    if confirm.lower() == "yes":
        await ClaudeBox.cleanup_session(session_id, remove_workspace=True)
        print("✅ Cleaned up")
    else:
        print("❌ Cancelled")
```

---

## Session Metadata

### Session Metadata File

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

### Reading Session Metadata

```python
import json
import os

def read_session_metadata(session_id: str):
    """Read session metadata from JSON file."""
    metadata_file = os.path.expanduser(
        f"~/.claudebox/sessions/{session_id}/.claudebox/session.json"
    )

    with open(metadata_file, 'r') as f:
        return json.load(f)

# Usage
metadata = read_session_metadata("my-project")
print(f"Created: {metadata['created_at']}")
print(f"Commands executed: {metadata['total_commands']}")
```

### Action History Log

**Location:** `~/.claudebox/sessions/{session_id}/.claudebox/history.jsonl`

**Format:** JSON Lines (one JSON object per line)

**Example:**
```jsonl
{"timestamp": "2025-01-01T10:00:00", "action": "session_created", "context": {"session_id": "my-project"}}
{"timestamp": "2025-01-01T10:01:00", "action": "code_execution", "context": {"prompt": "Initialize", "success": true}}
{"timestamp": "2025-01-01T10:02:00", "action": "file_created", "context": {"file": "app.py"}}
```

### Reading Action History

```python
import json

def read_action_history(session_id: str):
    """Read all actions from history.jsonl."""
    history_file = os.path.expanduser(
        f"~/.claudebox/sessions/{session_id}/.claudebox/history.jsonl"
    )

    actions = []
    with open(history_file, 'r') as f:
        for line in f:
            actions.append(json.loads(line))

    return actions

# Usage
actions = read_action_history("my-project")
print(f"Total actions: {len(actions)}")
for action in actions[-5:]:  # Last 5
    print(f"  {action['timestamp']}: {action['action']}")
```

---

## Advanced Session Patterns

### Pattern 1: Session Pool for Parallel Tasks

```python
async def parallel_sessions():
    """Run multiple sessions in parallel."""
    async def task_a():
        async with ClaudeBox(session_id="task-a") as box:
            return await box.code("Build API")

    async def task_b():
        async with ClaudeBox(session_id="task-b") as box:
            return await box.code("Build UI")

    results = await asyncio.gather(task_a(), task_b())
    return results
```

### Pattern 2: Session Chain (Sequential Dependencies)

```python
async def session_chain():
    """Chain sessions with dependencies."""
    # Session 1: Data preparation
    async with ClaudeBox(session_id="data-prep") as box:
        await box.code("Clean dataset")

    # Session 2: Analysis (depends on session 1)
    async with ClaudeBox(session_id="analysis") as box:
        # Copy data from session 1
        prep_workspace = "~/.claudebox/sessions/data-prep/workspace"
        await box.code(f"Copy data from {prep_workspace}")
        await box.code("Run analysis")

    # Session 3: Visualization (depends on session 2)
    async with ClaudeBox(session_id="visualization") as box:
        analysis_workspace = "~/.claudebox/sessions/analysis/workspace"
        await box.code(f"Load results from {analysis_workspace}")
        await box.code("Create visualizations")
```

### Pattern 3: Session with Checkpoints

```python
async def session_with_checkpoints(session_id: str):
    """Create checkpoints by copying workspace."""
    import shutil
    import os

    async with ClaudeBox(session_id=session_id) as box:
        # Checkpoint 1
        await box.code("Phase 1 work")
        checkpoint_1 = f"~/.claudebox/checkpoints/{session_id}-phase1"
        shutil.copytree(box.workspace_path, os.path.expanduser(checkpoint_1))

        # Checkpoint 2
        await box.code("Phase 2 work")
        checkpoint_2 = f"~/.claudebox/checkpoints/{session_id}-phase2"
        shutil.copytree(box.workspace_path, os.path.expanduser(checkpoint_2))
```

### Pattern 4: Session Templates

```python
async def create_from_template(session_id: str, template_session: str):
    """Create new session from template workspace."""
    import shutil
    import os

    # Copy template workspace to new session
    template_workspace = os.path.expanduser(
        f"~/.claudebox/sessions/{template_session}/workspace"
    )
    new_workspace = os.path.expanduser(
        f"~/.claudebox/sessions/{session_id}/workspace"
    )
    os.makedirs(os.path.dirname(new_workspace), exist_ok=True)
    shutil.copytree(template_workspace, new_workspace)

    # Now use the session
    async with ClaudeBox(session_id=session_id) as box:
        await box.code("Continue from template")
```

---

## Best Practices

### 1. Use Descriptive Session IDs

```python
# ✅ Good: Descriptive
async with ClaudeBox(session_id="user-auth-service") as box:
    ...

# ❌ Bad: Generic
async with ClaudeBox(session_id="test123") as box:
    ...
```

### 2. Clean Up When Done

```python
async def responsible_cleanup():
    session_id = "temporary-analysis"

    try:
        async with ClaudeBox(session_id=session_id) as box:
            result = await box.code("Analyze data")
    finally:
        # Always cleanup, even if error occurred
        await ClaudeBox.cleanup_session(session_id, remove_workspace=True)
```

### 3. Use Ephemeral for Temporary Work

```python
# ✅ For quick tasks, use ephemeral
async def quick_analysis():
    async with ClaudeBox() as box:  # No session_id
        return await box.code("Quick analysis")
    # Auto-cleanup
```

### 4. Document Session Purpose

```python
async def documented_session():
    """
    Session: ml-training-experiment
    Purpose: Train model on customer data
    Expected duration: 3 days
    Cleanup: After model evaluation complete
    """
    async with ClaudeBox(session_id="ml-training-experiment") as box:
        ...
```

### 5. Version Control Workspace

```python
async def versioned_session():
    async with ClaudeBox(session_id="versioned-project") as box:
        await box.code("git init")
        await box.code("git add .")
        await box.code("git commit -m 'Initial commit'")
        # Workspace is now version controlled
```

### 6. Regular Cleanup Schedule

```python
import asyncio
from datetime import datetime, timedelta

async def weekly_cleanup():
    """Run weekly to clean up old sessions."""
    sessions = ClaudeBox.list_sessions()
    cutoff = datetime.now() - timedelta(days=7)

    for session in sessions:
        if "temp-" in session.session_id:  # Cleanup temp sessions
            created = datetime.fromisoformat(session.created_at)
            if created < cutoff:
                await ClaudeBox.cleanup_session(
                    session.session_id,
                    remove_workspace=True
                )
                print(f"Cleaned up: {session.session_id}")

# Run weekly via cron or scheduler
asyncio.run(weekly_cleanup())
```

---

## Troubleshooting

### Issue: Session Already Exists

**Error:**
```
SessionAlreadyExistsError: Session 'my-project' already exists
```

**Solution:**
```python
# Use reconnect instead
async with ClaudeBox.reconnect("my-project") as box:
    ...
```

### Issue: Session Not Found

**Error:**
```
SessionNotFoundError: Session 'my-project' not found
```

**Solution:**
```python
# Create it first
async with ClaudeBox(session_id="my-project") as box:
    ...
```

### Issue: Workspace Disk Full

**Error:**
```
OSError: No space left on device
```

**Solution:**
```python
# Clean up old sessions
sessions = ClaudeBox.list_sessions()
for session in sessions:
    print(f"Clean up {session.session_id}? (yes/no)")
    if input() == "yes":
        await ClaudeBox.cleanup_session(session.session_id, remove_workspace=True)
```

### Issue: Corrupted Session

**Symptoms:** Cannot reconnect, errors loading metadata

**Solution:**
```bash
# Remove corrupted session manually
rm -rf ~/.claudebox/sessions/corrupted-session/

# Create fresh session
async with ClaudeBox(session_id="fresh-session") as box:
    ...
```

---

## Next Steps

- **[Skills Guide](skills.md)** - Add capabilities to sessions
- **[Templates Guide](templates.md)** - Specialized session environments
- **[Workspace Guide](workspace.md)** - Deep dive into workspace structure
- **[Examples](../../examples/01_basic_usage.py)** - 8 session examples

---

**Master sessions, unlock ClaudeBox's full potential!**
