"""
Basic ClaudeBox usage examples.

This demonstrates the fundamental features of ClaudeBox:
- Simple ephemeral sessions
- Persistent sessions
- Session reconnection
- Listing and cleanup
"""

import asyncio
import logging

from claudebox import ClaudeBox


async def example_ephemeral_session():
    """Example 1: Ephemeral session (auto-cleanup)."""
    print("\n=== Example 1: Ephemeral Session ===")

    async with ClaudeBox() as box:
        print(f"Box ID: {box.id}")
        print(f"Session ID: {box.session_id}")
        print(f"Is persistent: {box.is_persistent}")
        print(f"Workspace: {box.workspace_path}")

        # Execute a simple command
        result = await box.code("Create a hello.txt file with 'Hello ClaudeBox!'")

        print(f"\nResult:")
        print(f"  Success: {result.success}")
        print(f"  Response: {result.response}")

    # Workspace is automatically cleaned up after exit
    print("\n✓ Ephemeral session completed (workspace auto-cleaned)")


async def example_persistent_session():
    """Example 2: Persistent session (workspace survives)."""
    print("\n=== Example 2: Persistent Session ===")

    session_id = "my-project"

    # First session
    async with ClaudeBox(session_id=session_id) as box:
        print(f"Session ID: {box.session_id}")
        print(f"Is persistent: {box.is_persistent}")
        print(f"Workspace: {box.workspace_path}")

        result = await box.code("Create a file called data.txt with some data")
        print(f"Created data file: {result.success}")

    # Workspace persists after exit
    print("\n✓ Persistent session created (workspace preserved)")


async def example_reconnect_session():
    """Example 3: Reconnect to existing session."""
    print("\n=== Example 3: Reconnect to Session ===")

    session_id = "my-project"

    # Reconnect to the session created in Example 2
    box = await ClaudeBox.reconnect(session_id)
    async with box:
        print(f"Reconnected to: {box.session_id}")
        print(f"Workspace: {box.workspace_path}")

        result = await box.code("List all files in the workspace")
        print(f"\nFiles in workspace:")
        print(result.response)

    print("\n✓ Session reconnection successful")


async def example_list_sessions():
    """Example 4: List all sessions."""
    print("\n=== Example 4: List Sessions ===")

    sessions = ClaudeBox.list_sessions()

    print(f"Found {len(sessions)} session(s):")
    for session in sessions:
        print(f"\n  Session ID: {session.session_id}")
        print(f"  Created at: {session.created_at}")
        print(f"  Workspace: {session.workspace_path}")
        print(f"  Status: {session.status}")


async def example_cleanup_session():
    """Example 5: Cleanup a session."""
    print("\n=== Example 5: Cleanup Session ===")

    session_id = "my-project"

    # Remove session and its workspace
    await ClaudeBox.cleanup_session(session_id, remove_workspace=True)

    print(f"✓ Session '{session_id}' cleaned up")


async def example_custom_configuration():
    """Example 6: Custom configuration."""
    print("\n=== Example 6: Custom Configuration ===")

    async with ClaudeBox(
        session_id="custom-config",
        cpus=2,
        memory_mib=2048,
        disk_size_gb=5,
        enable_logging=True,
    ) as box:
        print(f"Box created with custom resources:")
        print(f"  CPUs: 2")
        print(f"  Memory: 2048 MiB")
        print(f"  Disk: 5 GB")

        result = await box.code("Check system resources")
        print(f"\nResult: {result.success}")

    # Cleanup
    await ClaudeBox.cleanup_session("custom-config", remove_workspace=True)


async def example_max_turns():
    """Example 7: Limit max turns."""
    print("\n=== Example 7: Max Turns ===")

    async with ClaudeBox() as box:
        # Limit to 5 turns maximum
        result = await box.code(
            "Create 3 files: a.txt, b.txt, c.txt", max_turns=5
        )

        print(f"Success: {result.success}")
        print(f"Response: {result.response[:100]}...")


async def example_workspace_access():
    """Example 8: Access workspace from host."""
    print("\n=== Example 8: Workspace Access ===")

    from pathlib import Path

    async with ClaudeBox(session_id="workspace-access") as box:
        workspace = Path(box.workspace_path)

        # Create a file from the host
        host_file = workspace / "host_created.txt"
        host_file.write_text("Created from host!")

        # Claude can see it in the VM
        result = await box.code("Read the contents of host_created.txt")

        print(f"Claude read from host file:")
        print(f"  {result.response}")

    # Cleanup
    await ClaudeBox.cleanup_session("workspace-access", remove_workspace=True)


async def main():
    """Run all examples."""
    await example_ephemeral_session()
    await example_persistent_session()
    await example_reconnect_session()
    await example_list_sessions()
    await example_cleanup_session()
    await example_custom_configuration()
    await example_max_turns()
    await example_workspace_access()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(name)s %(levelname)s %(message)s")
    asyncio.run(main())
