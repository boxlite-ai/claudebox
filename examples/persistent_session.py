"""
Example: Persistent Sessions with ClaudeBox

This example demonstrates how to use persistent sessions for multi-turn development workflows.
Sessions persist across program runs, maintaining workspace state.
"""

import asyncio
import logging

from claudebox import ClaudeBox


async def main():
    print("=== ClaudeBox Persistent Session Example ===\n")

    # Example 1: Create a persistent session
    print("1. Creating persistent session 'my-dev-env'...")
    async with ClaudeBox(session_id="my-dev-env") as box:
        print(f"   Session ID: {box.session_id}")
        print(f"   Workspace: {box.workspace_path}")
        print(f"   Is persistent: {box.is_persistent}\n")

        result = await box.code("Create a Python hello.py file in /config/workspace")
        print(f"   Result: {result.response[:100]}...\n")

    print("   Session closed but workspace persists!\n")

    # Example 2: Reconnect to the same session
    print("2. Reconnecting to session 'my-dev-env'...")
    async with ClaudeBox.reconnect("my-dev-env") as box:
        print(f"   Reconnected to: {box.session_id}\n")

        result = await box.code("List files in /config/workspace")
        print(f"   Files: {result.response[:100]}...\n")

    # Example 3: List all sessions
    print("3. Listing all sessions...")
    sessions = ClaudeBox.list_sessions()
    for session in sessions:
        print(f"   - {session.session_id}: {session.status} (created: {session.created_at})")
    print()

    # Example 4: Cleanup when done
    print("4. Cleaning up session...")
    await ClaudeBox.cleanup_session("my-dev-env", remove_workspace=True)
    print("   Session and workspace removed!\n")

    # Example 5: Ephemeral session (default behavior)
    print("5. Creating ephemeral session (auto-cleanup)...")
    async with ClaudeBox() as box:
        print(f"   Session ID: {box.session_id}")
        print(f"   Is persistent: {box.is_persistent}")
        result = await box.code("echo 'This workspace will be deleted on exit'")
        print(f"   Result: {result.response[:80]}...\n")
    print("   Ephemeral session auto-cleaned!\n")

    print("=== Example Complete ===")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
    asyncio.run(main())
