# Your First Session

An interactive, step-by-step tutorial to master ClaudeBox sessions.

---

## What You'll Build

In this tutorial, you'll:

1. Create a persistent session
2. Build a simple Python web API
3. Add features across multiple runs
4. Explore the workspace structure
5. View session logs and metadata
6. Reconnect to continue work
7. Clean up when finished

**Time required:** 15-20 minutes

**Prerequisites:**
- ✅ ClaudeBox installed ([Installation Guide](installation.md))
- ✅ Authentication configured ([Authentication Guide](authentication.md))
- ✅ Basic Python knowledge

---

## Step 1: Create Your First Persistent Session

Let's build a simple Flask API over multiple sessions.

**Create `tutorial_session.py`:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    print("=== Creating Persistent Session ===\n")

    # Create persistent session with ID "flask-tutorial"
    async with ClaudeBox(session_id="flask-tutorial") as box:
        print(f"Session ID: {box.session_id}")
        print(f"Workspace: {box.workspace_path}")
        print(f"Persistent: {box.is_persistent}\n")

        # Task 1: Initialize Flask project
        print("Task: Initialize Flask project...")
        result = await box.code(
            "Create a Flask project with:\n"
            "1. app.py with a basic Flask app\n"
            "2. requirements.txt with Flask\n"
            "3. A GET / endpoint that returns {'message': 'Hello from ClaudeBox!'}\n"
            "4. Run pip install -r requirements.txt"
        )

        print(f"Success: {result.success}")
        print(f"Response:\n{result.response}\n")

        if result.success:
            print("✅ Flask project initialized!")
        else:
            print(f"❌ Error: {result.error}")

asyncio.run(main())
```

**Run it:**
```bash
python3 tutorial_session.py
```

**Expected output:**
```
=== Creating Persistent Session ===

Session ID: flask-tutorial
Workspace: /Users/yourname/.claudebox/sessions/flask-tutorial/workspace
Persistent: True

Task: Initialize Flask project...
Success: True
Response:
I've created a Flask project with:
- app.py with GET / endpoint
- requirements.txt with Flask dependency
- Installed dependencies with pip

✅ Flask project initialized!
```

---

## Step 2: Explore the Workspace

Your session workspace persists on the host filesystem. Let's explore it!

```bash
# Navigate to workspace
cd ~/.claudebox/sessions/flask-tutorial/

# List directory structure
tree
# Or use ls if tree not installed
ls -la
```

**Expected structure:**
```
flask-tutorial/
├── workspace/              # Your project files (mounted in VM)
│   ├── app.py
│   ├── requirements.txt
│   └── venv/              # Python virtual environment
└── .claudebox/            # Session metadata (mounted in VM)
    ├── session.json       # Session metadata
    └── history.jsonl      # Action log
```

### View Created Files

**Check `app.py`:**
```bash
cat ~/.claudebox/sessions/flask-tutorial/workspace/app.py
```

**Expected content:**
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'message': 'Hello from ClaudeBox!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**Check `requirements.txt`:**
```bash
cat ~/.claudebox/sessions/flask-tutorial/workspace/requirements.txt
```

**Expected content:**
```
Flask==3.0.0
```

---

## Step 3: View Session Metadata

ClaudeBox maintains metadata about your session in `.claudebox/`.

### Session Info

**View `session.json`:**
```bash
cat ~/.claudebox/sessions/flask-tutorial/.claudebox/session.json | python3 -m json.tool
```

**Expected content:**
```json
{
  "session_id": "flask-tutorial",
  "box_id": "box-abc123",
  "created_at": "2025-01-01T10:00:00.000000",
  "updated_at": "2025-01-01T10:05:00.000000",
  "total_commands": 5,
  "total_files_created": 2,
  "workspace_path": "/Users/yourname/.claudebox/sessions/flask-tutorial/workspace"
}
```

### Action History

**View `history.jsonl`** (JSON Lines format - one JSON object per line):
```bash
cat ~/.claudebox/sessions/flask-tutorial/.claudebox/history.jsonl | python3 -m json.tool
```

**Expected content:**
```json
{
  "timestamp": "2025-01-01T10:00:00.000000",
  "action": "session_created",
  "context": {
    "session_id": "flask-tutorial",
    "box_id": "box-abc123"
  }
}
{
  "timestamp": "2025-01-01T10:01:00.000000",
  "action": "code_execution",
  "context": {
    "prompt": "Create a Flask project...",
    "success": true,
    "files_created": ["app.py", "requirements.txt"]
  }
}
```

**Note**: Each line is a separate JSON object. This format is ideal for streaming logs and incremental processing.

---

## Step 4: Reconnect and Add Features

The power of persistent sessions: reconnect later and continue where you left off!

**Create `tutorial_add_features.py`:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    print("=== Reconnecting to Session ===\n")

    # Reconnect to existing session
    async with ClaudeBox.reconnect("flask-tutorial") as box:
        print(f"Reconnected to: {box.session_id}")
        print(f"Workspace: {box.workspace_path}\n")

        # Task 2: Add user endpoint
        print("Task: Add user endpoint...")
        result = await box.code(
            "Add a GET /users endpoint to app.py that returns:\n"
            "{'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}"
        )

        if result.success:
            print("✅ User endpoint added!")
        else:
            print(f"❌ Error: {result.error}")

        print()

        # Task 3: Add health check
        print("Task: Add health check endpoint...")
        result = await box.code(
            "Add a GET /health endpoint that returns:\n"
            "{'status': 'healthy', 'version': '1.0.0'}"
        )

        if result.success:
            print("✅ Health check added!")
        else:
            print(f"❌ Error: {result.error}")

asyncio.run(main())
```

**Run it:**
```bash
python3 tutorial_add_features.py
```

**Expected output:**
```
=== Reconnecting to Session ===

Reconnected to: flask-tutorial
Workspace: /Users/yourname/.claudebox/sessions/flask-tutorial/workspace

Task: Add user endpoint...
✅ User endpoint added!

Task: Add health check endpoint...
✅ Health check added!
```

### Verify Changes

**Check updated `app.py`:**
```bash
cat ~/.claudebox/sessions/flask-tutorial/workspace/app.py
```

**Expected content (now with 3 endpoints):**
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'message': 'Hello from ClaudeBox!'})

@app.route('/users')
def users():
    return jsonify({
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## Step 5: List All Sessions

See all your ClaudeBox sessions (active and stopped):

**Create `tutorial_list_sessions.py`:**
```python
from claudebox import ClaudeBox

print("=== All ClaudeBox Sessions ===\n")

sessions = ClaudeBox.list_sessions()

if not sessions:
    print("No sessions found.")
else:
    print(f"Found {len(sessions)} session(s):\n")
    for session in sessions:
        print(f"  Session: {session.session_id}")
        print(f"  Status: {session.status}")
        print(f"  Created: {session.created_at}")
        print(f"  Workspace: {session.workspace_path}")
        print()
```

**Run it:**
```bash
python3 tutorial_list_sessions.py
```

**Expected output:**
```
=== All ClaudeBox Sessions ===

Found 1 session(s):

  Session: flask-tutorial
  Status: stopped
  Created: 2025-01-01 10:00:00
  Workspace: /Users/yourname/.claudebox/sessions/flask-tutorial/workspace
```

---

## Step 6: Test Your API

Let's test the Flask API we built!

**Create `tutorial_test_api.py`:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    print("=== Testing Flask API ===\n")

    async with ClaudeBox.reconnect("flask-tutorial") as box:
        # Start Flask server in background and test endpoints
        result = await box.code(
            "Start the Flask app in the background, then use curl to test all three endpoints:\n"
            "1. GET / \n"
            "2. GET /users\n"
            "3. GET /health\n"
            "Show the responses."
        )

        print("Test Results:")
        print(result.response)

asyncio.run(main())
```

**Run it:**
```bash
python3 tutorial_test_api.py
```

**Expected output:**
```
=== Testing Flask API ===

Test Results:
Started Flask server on port 5000

GET / response:
{"message": "Hello from ClaudeBox!"}

GET /users response:
{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

GET /health response:
{"status": "healthy", "version": "1.0.0"}

All endpoints working correctly!
```

---

## Step 7: Add Tests

Let's add unit tests to make our project production-ready:

**Create `tutorial_add_tests.py`:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    print("=== Adding Unit Tests ===\n")

    async with ClaudeBox.reconnect("flask-tutorial") as box:
        # Add pytest tests
        result = await box.code(
            "Create test_app.py with pytest tests for all three endpoints:\n"
            "1. Test GET / returns correct message\n"
            "2. Test GET /users returns two users\n"
            "3. Test GET /health returns status and version\n"
            "Add pytest to requirements.txt and install it.\n"
            "Run the tests with pytest."
        )

        if result.success:
            print("✅ Tests created and executed!")
            print(f"\nTest output:\n{result.response}")
        else:
            print(f"❌ Error: {result.error}")

asyncio.run(main())
```

**Run it:**
```bash
python3 tutorial_add_tests.py
```

**Verify tests created:**
```bash
cat ~/.claudebox/sessions/flask-tutorial/workspace/test_app.py
```

---

## Step 8: Session Lifecycle Summary

Let's review what we've learned about session lifecycle:

**Create `tutorial_session_info.py`:**
```python
import asyncio
import json
from claudebox import ClaudeBox

async def main():
    print("=== Session Lifecycle Summary ===\n")

    # Load session metadata
    session_file = "/Users/yourname/.claudebox/sessions/flask-tutorial/.claudebox/session.json"

    try:
        with open(session_file.replace("/Users/yourname", "~/.").replace("~", "/Users/yourname"), 'r') as f:
            metadata = json.load(f)

        print("Session Information:")
        print(f"  ID: {metadata['session_id']}")
        print(f"  Created: {metadata['created_at']}")
        print(f"  Updated: {metadata['updated_at']}")
        print(f"  Total Commands: {metadata.get('total_commands', 'N/A')}")
        print(f"  Files Created: {metadata.get('total_files_created', 'N/A')}")
        print(f"  Workspace: {metadata['workspace_path']}")
        print()

        print("Session History:")
        # Count actions from history.jsonl
        history_file = session_file.replace("session.json", "history.jsonl")
        with open(history_file, 'r') as f:
            actions = [json.loads(line) for line in f]

        print(f"  Total Actions: {len(actions)}")
        print("\n  Recent Actions:")
        for action in actions[-5:]:  # Show last 5 actions
            print(f"    - {action['action']} at {action['timestamp']}")

    except FileNotFoundError:
        print("Session metadata not found. Run previous tutorial steps first.")

asyncio.run(main())
```

---

## Step 9: Understanding Workspace Persistence

Key concept: **Everything in `workspace/` survives across sessions!**

**Diagram:**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Host Machine                                          │
│  ─────────────                                         │
│                                                         │
│  ~/.claudebox/sessions/flask-tutorial/                │
│  │                                                      │
│  ├── workspace/          ← Your project files         │
│  │   ├── app.py         ← Persists!                   │
│  │   ├── test_app.py    ← Persists!                   │
│  │   └── requirements.txt ← Persists!                 │
│  │                                                      │
│  └── .claudebox/         ← Metadata                    │
│      ├── session.json    ← Session info                │
│      └── history.jsonl   ← Action log                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
                        ↕
                 Volume Mount
                        ↕
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Micro-VM (BoxLite)                                    │
│  ──────────────────                                    │
│                                                         │
│  /config/workspace/      ← Mounted from host          │
│  │                                                      │
│  ├── app.py              ← Same files                  │
│  ├── test_app.py                                       │
│  └── requirements.txt                                  │
│                                                         │
│  /config/.claudebox/     ← Mounted from host          │
│  │                                                      │
│  ├── session.json                                      │
│  └── history.jsonl                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Key points:**
- ✅ Files in `workspace/` are **on your host machine**
- ✅ They're **mounted** into the micro-VM
- ✅ Changes persist when VM stops
- ✅ You can edit files from host or VM
- ✅ Can version control with git
- ✅ Can back up, move between machines

---

## Step 10: Clean Up Session

When you're finished with a session, clean it up:

### Option A: Keep Workspace (Remove VM Only)

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    print("Cleaning up session (keeping workspace)...")
    await ClaudeBox.cleanup_session("flask-tutorial", remove_workspace=False)
    print("✅ Session removed, workspace preserved at ~/.claudebox/sessions/flask-tutorial/")

asyncio.run(main())
```

**Use when:** You want to keep files for reference but stop the VM.

### Option B: Remove Everything

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    print("Cleaning up session and workspace...")
    await ClaudeBox.cleanup_session("flask-tutorial", remove_workspace=True)
    print("✅ Session and workspace completely removed")

asyncio.run(main())
```

**Use when:** You're completely done and don't need the files.

**Warning:** This **permanently deletes** all workspace files!

### Manual Cleanup

Alternatively, manually remove workspace:

```bash
# Remove entire session
rm -rf ~/.claudebox/sessions/flask-tutorial/

# Or just remove workspace, keep metadata
rm -rf ~/.claudebox/sessions/flask-tutorial/workspace/
```

---

## Complete Tutorial Script

Here's a single script that runs through the entire tutorial:

**Create `complete_tutorial.py`:**
```python
import asyncio
from claudebox import ClaudeBox

async def main():
    print("=" * 60)
    print("ClaudeBox First Session Tutorial")
    print("=" * 60)
    print()

    # Step 1: Create session
    print("STEP 1: Creating persistent session...")
    async with ClaudeBox(session_id="flask-tutorial") as box:
        print(f"✅ Session created: {box.session_id}")
        print(f"   Workspace: {box.workspace_path}\n")

        # Initialize Flask project
        print("STEP 2: Initializing Flask project...")
        result = await box.code(
            "Create a Flask app with GET / endpoint returning {'message': 'Hello!'}"
        )
        print(f"✅ Flask project initialized\n")

    # Step 3: Reconnect and add features
    print("STEP 3: Reconnecting and adding features...")
    async with ClaudeBox.reconnect("flask-tutorial") as box:
        print(f"✅ Reconnected to: {box.session_id}\n")

        # Add endpoints
        await box.code("Add GET /users endpoint")
        print("✅ Added /users endpoint")

        await box.code("Add GET /health endpoint")
        print("✅ Added /health endpoint\n")

    # Step 4: List sessions
    print("STEP 4: Listing sessions...")
    sessions = ClaudeBox.list_sessions()
    print(f"✅ Found {len(sessions)} session(s)\n")

    # Step 5: Session info
    print("STEP 5: Session summary...")
    for session in sessions:
        if session.session_id == "flask-tutorial":
            print(f"   ID: {session.session_id}")
            print(f"   Created: {session.created_at}")
            print(f"   Workspace: {session.workspace_path}")
    print()

    # Step 6: Cleanup prompt
    print("STEP 6: Cleanup")
    print("To clean up this session later, run:")
    print("  await ClaudeBox.cleanup_session('flask-tutorial', remove_workspace=True)")
    print()
    print("=" * 60)
    print("Tutorial Complete!")
    print("=" * 60)

asyncio.run(main())
```

**Run the complete tutorial:**
```bash
python3 complete_tutorial.py
```

---

## What You've Learned

✅ **Session Creation** - Creating persistent sessions with `session_id`
✅ **Workspace Persistence** - Files survive across VM restarts
✅ **Workspace Structure** - Understanding `workspace/` and `.claudebox/`
✅ **Session Metadata** - Reading `session.json` and `history.jsonl`
✅ **Reconnection** - Using `reconnect()` to continue work
✅ **Session Listing** - Finding all active sessions
✅ **Cleanup** - Removing sessions and workspaces
✅ **Volume Mounting** - How host files are mounted in VM
✅ **Multi-Step Workflows** - Building projects over multiple sessions

---

## Common Patterns Demonstrated

### Pattern 1: Initialize → Iterate → Test

```python
# Day 1: Initialize
async with ClaudeBox(session_id="project") as box:
    await box.code("Initialize project structure")

# Day 2: Add features
async with ClaudeBox.reconnect("project") as box:
    await box.code("Add feature A")
    await box.code("Add feature B")

# Day 3: Test
async with ClaudeBox.reconnect("project") as box:
    await box.code("Write and run tests")
```

### Pattern 2: Exploratory Development

```python
# Create session for experimentation
async with ClaudeBox(session_id="experiment") as box:
    await box.code("Try approach A")
    # Doesn't work? Session persists, try again

async with ClaudeBox.reconnect("experiment") as box:
    await box.code("Try approach B")
    # Workspace has all previous attempts
```

### Pattern 3: Collaborative Development

```python
# Developer A: Setup
async with ClaudeBox(session_id="team-project") as box:
    await box.code("Initialize project")

# Share workspace: ~/.claudebox/sessions/team-project/

# Developer B: Continue (on same machine or shared filesystem)
async with ClaudeBox.reconnect("team-project") as box:
    await box.code("Add feature")
```

---

## Troubleshooting Tutorial

### Issue: Session already exists

**Error when running tutorial:**
```
SessionAlreadyExistsError: Session 'flask-tutorial' already exists
```

**Solution:** Clean up first:
```bash
python3 -c "import asyncio; from claudebox import ClaudeBox; asyncio.run(ClaudeBox.cleanup_session('flask-tutorial', remove_workspace=True))"
```

### Issue: Cannot reconnect

**Error:**
```
SessionNotFoundError: Session 'flask-tutorial' not found
```

**Solution:** Run Step 1 first to create the session.

### Issue: Files not visible in workspace

**Cause:** Session was ephemeral (no `session_id`)

**Solution:** Always use `session_id` for persistence:
```python
# Wrong: ephemeral
async with ClaudeBox() as box:
    ...

# Correct: persistent
async with ClaudeBox(session_id="my-session") as box:
    ...
```

---

## Next Steps

Congratulations! You've completed the first session tutorial. Continue learning:

- **[Session Management Guide](../guides/sessions.md)** - Advanced session patterns
- **[Skills System](../guides/skills.md)** - Add databases, APIs, cloud capabilities
- **[Sandbox Templates](../guides/templates.md)** - Specialized environments
- **[Security Policies](../guides/security.md)** - Fine-grained control
- **[Examples](../../examples/)** - 71 comprehensive examples

### Recommended Next Tutorial

**Try the Skills System next:**
- Add a PostgreSQL database to your Flask app
- Integrate with external APIs
- Deploy to cloud platforms

See [Skills Guide](../guides/skills.md) to learn more!

---

**Tutorial complete!** Continue to [Skills Guide](../guides/skills.md) →
