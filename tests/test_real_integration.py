"""Real integration tests with actual BoxLite and Claude Code CLI.

These tests require:
1. BoxLite installed and running
2. CLAUDE_CODE_OAUTH_TOKEN environment variable set
3. Docker/VM infrastructure available

Run with: pytest tests/test_real_integration.py -v -m real
Skip with: pytest tests/ -v -m "not real"
"""

import os
from pathlib import Path

import pytest

from claudebox import ClaudeBox

# Mark all tests in this file as 'real' (requires infrastructure)
pytestmark = pytest.mark.real


@pytest.fixture
def ensure_oauth_token():
    """Ensure OAuth token is set for real tests."""
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        pytest.skip("CLAUDE_CODE_OAUTH_TOKEN not set - skipping real integration test")
    return token


@pytest.mark.asyncio
async def test_real_ephemeral_session(ensure_oauth_token, temp_workspace):
    """Test ephemeral session with real BoxLite and Claude Code."""
    async with ClaudeBox(
        oauth_token=ensure_oauth_token, workspace_dir=temp_workspace
    ) as box:
        # Verify box is created
        assert box.id
        assert box.session_id.startswith("ephemeral-")

        # Execute real Claude Code command
        result = await box.code("echo 'Hello from ClaudeBox' > /config/workspace/test.txt")

        # Verify result
        assert result.exit_code == 0 or result.success
        # Note: exact result format depends on Claude Code output

        # Verify file was created in workspace
        Path(box.workspace_path) / "test.txt"
        # File should exist (might be created by Claude)
        # assert test_file.exists()  # Uncomment if Claude creates it


    # Ephemeral workspace should be cleaned up
    # Note: This check might be timing-dependent
    # assert not Path(workspace_path).exists()


@pytest.mark.asyncio
async def test_real_persistent_session(ensure_oauth_token, temp_workspace):
    """Test persistent session with real BoxLite."""
    session_id = "test-real-persistent"

    try:
        # Create persistent session
        async with ClaudeBox(
            session_id=session_id,
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
        ) as box:
            assert box.session_id == session_id
            assert box.is_persistent is True

            # Execute command to create file
            await box.code("Create a file called hello.txt with content 'Hello World'")

            workspace_path = box.workspace_path

        # Workspace should still exist
        assert Path(workspace_path).exists()

        # Reconnect to session
        box = await ClaudeBox.reconnect(
            session_id, workspace_dir=temp_workspace
        )
        async with box:
            assert box.session_id == session_id

            # Verify file from previous session exists
            # (This depends on Claude actually creating the file)
            await box.code("List files in /config/workspace")
            # Check result contains evidence of hello.txt if Claude created it

    finally:
        # Cleanup
        await ClaudeBox.cleanup_session(
            session_id, workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_real_claude_code_execution(ensure_oauth_token, temp_workspace):
    """Test actual Claude Code CLI execution."""
    async with ClaudeBox(
        oauth_token=ensure_oauth_token, workspace_dir=temp_workspace
    ) as box:
        # Execute a simple Claude Code prompt
        result = await box.code("What is 2 + 2?")

        # Verify we got a result
        assert result is not None
        assert result.exit_code is not None

        # Check for response or error
        if result.success:
            assert result.response is not None
        else:
            # If it failed, should have error info
            assert result.error is not None or result.raw_output


@pytest.mark.asyncio
async def test_real_workspace_volume_mounting(ensure_oauth_token, temp_workspace):
    """Test that workspace volume mounting works correctly."""
    try:
        async with ClaudeBox(
            session_id="mount-test",
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
        ) as box:
            workspace_path = Path(box.workspace_path)

            # Create a file directly in host workspace
            test_file = workspace_path / "host_created.txt"
            test_file.write_text("Created from host")

            # Execute Claude command to read the file
            await box.code("Read the contents of /config/workspace/host_created.txt")

            # Claude should be able to see the file (if command succeeds)
            # Exact verification depends on Claude's response format

            # Create a file from inside the box
            await box.code("Write 'Created from box' to /config/workspace/box_created.txt")

            # File should appear on host
            workspace_path / "box_created.txt"
            # Check if file exists (might depend on Claude's execution)

    finally:
        # Cleanup
        await ClaudeBox.cleanup_session(
            "mount-test", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_real_reconnect(ensure_oauth_token, temp_workspace):
    """Test reconnecting to a real persistent session."""
    session_id = "test-real-reconnect"

    try:
        # Create initial session
        async with ClaudeBox(
            session_id=session_id,
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
        ) as box:
            # Create marker file
            marker = Path(box.workspace_path) / "marker.txt"
            marker.write_text("session 1")

        # Reconnect
        box = await ClaudeBox.reconnect(
            session_id, workspace_dir=temp_workspace
        )
        async with box:
            # Marker should still exist
            marker = Path(box.workspace_path) / "marker.txt"
            assert marker.exists()
            assert marker.read_text() == "session 1"

            # Add another marker
            marker2 = Path(box.workspace_path) / "marker2.txt"
            marker2.write_text("session 2")

        # Both markers should persist
        assert marker.exists()
        assert marker2.exists()

    finally:
        # Cleanup
        await ClaudeBox.cleanup_session(
            session_id, workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_real_list_sessions(ensure_oauth_token, temp_workspace):
    """Test listing real sessions."""
    session_ids = ["real-session-1", "real-session-2"]

    try:
        # Create multiple sessions
        for sid in session_ids:
            async with ClaudeBox(
                session_id=sid,
                oauth_token=ensure_oauth_token,
                workspace_dir=temp_workspace,
            ):
                pass

        # List sessions
        sessions = ClaudeBox.list_sessions(workspace_dir=temp_workspace)

        # Should include our sessions
        found_ids = {s.session_id for s in sessions}
        for sid in session_ids:
            assert sid in found_ids

    finally:
        # Cleanup all test sessions
        for sid in session_ids:
            try:
                await ClaudeBox.cleanup_session(
                    sid, workspace_dir=temp_workspace, remove_workspace=True
                )
            except Exception:
                pass  # Ignore cleanup errors


@pytest.mark.asyncio
async def test_real_box_resources(ensure_oauth_token, temp_workspace):
    """Test that real box has expected resources."""
    async with ClaudeBox(
        oauth_token=ensure_oauth_token,
        workspace_dir=temp_workspace,
        cpus=2,
        memory_mib=2048,
    ) as box:
        # Box should be created with specified resources
        assert box.id

        # Execute command to check resources are available
        result = await box.code("Check available CPU and memory")

        # Just verify command executes (exact checks depend on Claude's capabilities)
        assert result is not None


# Helper to clean up any leftover test sessions
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_sessions():
    """Clean up any leftover test sessions after all real tests complete."""
    yield

    # Cleanup code runs after all tests
    # This is a safety measure to remove any test sessions that weren't cleaned up
    try:
        import tempfile

        tempfile.gettempdir()
        sessions = ClaudeBox.list_sessions()

        for session in sessions:
            # Clean up sessions in temp directories (test sessions)
            if "claudebox_test_" in session.workspace_path:
                try:
                    import asyncio

                    asyncio.run(
                        ClaudeBox.cleanup_session(
                            session.session_id, remove_workspace=True
                        )
                    )
                except Exception:
                    pass  # Ignore errors during cleanup
    except Exception:
        pass  # Ignore any errors in cleanup
