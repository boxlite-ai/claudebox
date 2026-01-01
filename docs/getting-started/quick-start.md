# Quick Start

Get started with ClaudeBox in 5 minutes. This hands-on tutorial covers the basics of running Claude Code in isolated micro-VMs.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Installed ClaudeBox ([Installation Guide](installation.md))
- ✅ Set up authentication (OAuth token or API key)
- ✅ Docker running and BoxLite installed

---

## Your First Command

Let's start with the simplest possible example - a "Hello World" script:

**Create a file `hello.py`:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    async with ClaudeBox() as box:
        result = await box.code("Create a hello.py script that prints 'Hello from ClaudeBox!'")
        print(result.response)

asyncio.run(main())
```

**Run it:**
```bash
python3 hello.py
```

**What happened?**
1. ClaudeBox created an isolated micro-VM
2. Claude Code CLI executed your prompt
3. Created a Python script inside the VM
4. The VM was automatically cleaned up after exit

This is an **ephemeral session** - the workspace is deleted when the session ends.

---

## Persistent Sessions

In real workflows, you want your work to persist across sessions. Let's create a persistent project:

**Create `persistent_demo.py`:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    # Create a persistent session with ID "my-project"
    async with ClaudeBox(session_id="my-project") as box:
        result = await box.code(
            "Create a Node.js project with package.json and a simple Express server in server.js"
        )
        print(f"Session ID: {box.session_id}")
        print(f"Workspace: {box.workspace_path}")
        print(f"\nClaude's response:\n{result.response}")

asyncio.run(main())
```

**Run it:**
```bash
python3 persistent_demo.py
```

**Expected output:**
```
Session ID: my-project
Workspace: /Users/yourname/.claudebox/sessions/my-project/workspace

Claude's response:
I've created a Node.js project with Express:
- package.json with dependencies
- server.js with basic Express server on port 3000
- Created node_modules after running npm install
```

### Viewing Workspace Files

Your workspace persists on the host machine at `~/.claudebox/sessions/my-project/`:

```bash
# List workspace files
ls -la ~/.claudebox/sessions/my-project/workspace/

# View created files
cat ~/.claudebox/sessions/my-project/workspace/package.json
cat ~/.claudebox/sessions/my-project/workspace/server.js

# Check session metadata
cat ~/.claudebox/sessions/my-project/.claudebox/session.json

# View action history
cat ~/.claudebox/sessions/my-project/.claudebox/history.jsonl
```

**Directory structure:**
```
~/.claudebox/sessions/my-project/
├── workspace/              # Your project files (mounted in VM)
│   ├── package.json
│   ├── server.js
│   └── node_modules/
└── .claudebox/            # Metadata (mounted in VM)
    ├── session.json       # Session metadata
    └── history.jsonl      # Action log
```

---

## Reconnecting to Sessions

The power of persistent sessions: you can reconnect later and continue where you left off.

**Create `reconnect_demo.py`:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    # Reconnect to existing session
    async with ClaudeBox.reconnect("my-project") as box:
        result = await box.code(
            "Add a GET /status endpoint to server.js that returns {status: 'ok'}"
        )
        print(f"Reconnected to: {box.session_id}")
        print(f"\nClaude's response:\n{result.response}")

asyncio.run(main())
```

**Run it:**
```bash
python3 reconnect_demo.py
```

Claude Code picks up where it left off - your previous files are all there! Check the updated `server.js`:

```bash
cat ~/.claudebox/sessions/my-project/workspace/server.js
```

---

## Listing All Sessions

See all your sessions (both active and stopped):

**Create `list_sessions.py`:**
```python
from claudebox import ClaudeBox

# List all sessions
sessions = ClaudeBox.list_sessions()

print(f"Found {len(sessions)} session(s):\n")
for session in sessions:
    print(f"  ID: {session.session_id}")
    print(f"  Status: {session.status}")
    print(f"  Created: {session.created_at}")
    print(f"  Workspace: {session.workspace_path}")
    print()
```

**Run it:**
```bash
python3 list_sessions.py
```

**Expected output:**
```
Found 1 session(s):

  ID: my-project
  Status: stopped
  Created: 2025-01-01 10:30:00
  Workspace: /Users/yourname/.claudebox/sessions/my-project/workspace
```

---

## Cleaning Up Sessions

When you're done with a session, clean it up:

### Option 1: Remove Box, Keep Workspace

Removes the VM but preserves all files and logs:

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    await ClaudeBox.cleanup_session("my-project", remove_workspace=False)
    print("Session removed, workspace preserved")

asyncio.run(main())
```

You can still browse files in `~/.claudebox/sessions/my-project/workspace/`

### Option 2: Remove Everything

Completely removes the session including all workspace files:

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    await ClaudeBox.cleanup_session("my-project", remove_workspace=True)
    print("Session and workspace completely removed")

asyncio.run(main())
```

**Warning**: This deletes all project files. Make sure to back up anything important!

---

## Complete Example: Multi-Session Workflow

Here's a realistic workflow showing session lifecycle:

**Create `workflow_demo.py`:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    # Day 1: Initialize project
    print("=== Day 1: Initialize Project ===")
    async with ClaudeBox(session_id="web-app") as box:
        result = await box.code("Create a React app with TypeScript using Vite")
        print(f"✅ Created React app in {box.workspace_path}")

    # Day 2: Add features
    print("\n=== Day 2: Add Features ===")
    async with ClaudeBox.reconnect("web-app") as box:
        result = await box.code("Add a Header component with navigation")
        print("✅ Added Header component")

    # Day 3: Testing
    print("\n=== Day 3: Testing ===")
    async with ClaudeBox.reconnect("web-app") as box:
        result = await box.code("Write unit tests for Header component using Vitest")
        print("✅ Added unit tests")

    # List session info
    print("\n=== Session Summary ===")
    sessions = ClaudeBox.list_sessions()
    for session in sessions:
        if session.session_id == "web-app":
            print(f"Project: {session.session_id}")
            print(f"Created: {session.created_at}")
            print(f"Workspace: {session.workspace_path}")

    # Cleanup when done
    print("\n=== Cleanup ===")
    await ClaudeBox.cleanup_session("web-app", remove_workspace=True)
    print("✅ Project cleaned up")

asyncio.run(main())
```

**Run it:**
```bash
python3 workflow_demo.py
```

This demonstrates:
- Creating a persistent session
- Multiple reconnections over "days"
- Listing session info
- Final cleanup

---

## Key Concepts

### Ephemeral vs Persistent Sessions

| Feature | Ephemeral | Persistent |
|---------|-----------|-----------|
| **Creation** | `ClaudeBox()` | `ClaudeBox(session_id="name")` |
| **Workspace** | Temporary | `~/.claudebox/sessions/name/` |
| **Cleanup** | Automatic on exit | Manual with `cleanup_session()` |
| **Reconnection** | ❌ Not possible | ✅ Via `reconnect()` |
| **Use Case** | Quick tasks | Multi-day projects |

### Session Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Create Session                                         │
│  ──────────────                                         │
│  ClaudeBox(session_id="proj")  →  Session Created      │
│                                   Workspace at          │
│                                   ~/.claudebox/         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Work on Project (Day 1)                               │
│  ────────────────────────                              │
│  box.code("Initialize project")  →  Files created     │
│                                      in workspace      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Reconnect (Day 2, 3, ...)                            │
│  ──────────────────────────                            │
│  ClaudeBox.reconnect("proj")  →  Continue work        │
│                                  with same files       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Cleanup                                               │
│  ────────                                              │
│  cleanup_session(remove_workspace=True)                │
│  →  Session & workspace deleted                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Workspace Persistence

Files persist on your **host machine** at `~/.claudebox/sessions/{session_id}/workspace/`:

- ✅ Survives VM shutdown
- ✅ Accessible from host filesystem
- ✅ Can be backed up, version controlled with git
- ✅ Shared across ClaudeBox reconnections

---

## Common Patterns

### Pattern 1: Quick One-Off Task

```python
async with ClaudeBox() as box:
    result = await box.code("Analyze data.csv and create summary.txt")
    # Workspace auto-deleted on exit
```

**When to use:** Simple tasks, no need to save work

### Pattern 2: Long-Running Project

```python
# Session 1: Setup
async with ClaudeBox(session_id="data-analysis") as box:
    await box.code("Load dataset and clean data")

# Session 2: Analysis
async with ClaudeBox.reconnect("data-analysis") as box:
    await box.code("Run statistical analysis")

# Session 3: Visualization
async with ClaudeBox.reconnect("data-analysis") as box:
    await box.code("Create matplotlib visualizations")

# Cleanup
await ClaudeBox.cleanup_session("data-analysis", remove_workspace=True)
```

**When to use:** Multi-step projects over days/weeks

### Pattern 3: Parallel Sessions

```python
# Work on multiple projects simultaneously
async def project_a():
    async with ClaudeBox(session_id="proj-a") as box:
        await box.code("Build API server")

async def project_b():
    async with ClaudeBox(session_id="proj-b") as box:
        await box.code("Build frontend")

# Run in parallel
await asyncio.gather(project_a(), project_b())
```

**When to use:** Independent workstreams

---

## Troubleshooting

### Issue: Session already exists

**Error:**
```
SessionAlreadyExistsError: Session 'my-project' already exists
```

**Solution:** Use `reconnect()` instead of creating new session:
```python
async with ClaudeBox.reconnect("my-project") as box:
    ...
```

### Issue: Session not found

**Error:**
```
SessionNotFoundError: Session 'my-project' not found
```

**Solution:** Create the session first:
```python
async with ClaudeBox(session_id="my-project") as box:
    ...
```

### Issue: Workspace files missing

**Cause:** Using ephemeral session (no `session_id`)

**Solution:** Add `session_id` parameter for persistence:
```python
# Wrong: ephemeral
async with ClaudeBox() as box:
    ...

# Correct: persistent
async with ClaudeBox(session_id="my-project") as box:
    ...
```

---

## What You've Learned

✅ Creating ephemeral sessions for quick tasks
✅ Creating persistent sessions for long-running projects
✅ Reconnecting to existing sessions
✅ Viewing workspace files on host
✅ Listing all sessions
✅ Cleaning up sessions
✅ Common workflow patterns

---

## Next Steps

Now that you understand the basics, explore more features:

- **[Authentication Guide](authentication.md)** - Detailed auth setup and security
- **[Your First Session](first-session.md)** - Interactive step-by-step tutorial
- **[Session Management Guide](../guides/sessions.md)** - Advanced session patterns
- **[Skills System](../guides/skills.md)** - Extend capabilities with skills
- **[Examples](../../examples/)** - 71 comprehensive examples

### Recommended Learning Path

1. ✅ **Quick Start** (you are here)
2. [Your First Session](first-session.md) - Hands-on tutorial
3. [Skills Guide](../guides/skills.md) - Add databases, APIs, cloud
4. [Templates Guide](../guides/templates.md) - Specialized environments
5. [Examples](../../examples/) - Real-world usage patterns

---

**Ready to dive deeper?** Continue to [Your First Session](first-session.md) →
