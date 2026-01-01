"""Integration tests for ClaudeBox with mocked BoxLite runtime."""

from pathlib import Path

import pytest

from claudebox import ClaudeBox
from claudebox.exceptions import SessionNotFoundError


@pytest.mark.asyncio
async def test_ephemeral_session_lifecycle(mock_boxlite, temp_workspace):
    """Test ephemeral session creates and auto-cleans workspace."""
    # Create ephemeral session (no session_id)
    async with ClaudeBox(workspace_dir=temp_workspace, runtime=mock_boxlite) as box:
        assert box.session_id.startswith("ephemeral-")
        assert box.is_persistent is False

        workspace_path = box.workspace_path
        assert Path(workspace_path).exists()

        # Execute a command
        result = await box.code("echo 'hello'")
        assert result.exit_code == 0

    # After exit, workspace should be cleaned up
    assert not Path(workspace_path).exists()


@pytest.mark.asyncio
async def test_ephemeral_workspace_cleaned_up(mock_boxlite, temp_workspace):
    """Test that ephemeral workspace is fully removed on exit."""
    workspace_path = None

    async with ClaudeBox(workspace_dir=temp_workspace, runtime=mock_boxlite) as box:
        workspace_path = box.workspace_path

        # Create some files in workspace
        test_file = Path(workspace_path) / "test.txt"
        test_file.write_text("ephemeral data")
        assert test_file.exists()

    # Entire session directory should be gone
    assert not Path(workspace_path).exists()
    session_dir = Path(workspace_path).parent
    assert not session_dir.exists()


@pytest.mark.asyncio
async def test_persistent_session_creation(mock_boxlite, temp_workspace):
    """Test creating a persistent session with session_id."""
    async with ClaudeBox(
        session_id="my-persistent-session",
        workspace_dir=temp_workspace,
        runtime=mock_boxlite,
    ) as box:
        assert box.session_id == "my-persistent-session"
        assert box.is_persistent is True

        workspace_path = box.workspace_path
        assert Path(workspace_path).exists()

        # Execute a command
        result = await box.code("echo 'persistent'")
        assert result.exit_code == 0

    # After exit, workspace should still exist
    assert Path(workspace_path).exists()


@pytest.mark.asyncio
async def test_persistent_workspace_survives_exit(mock_boxlite, temp_workspace):
    """Test that persistent workspace and files survive box exit."""
    # Create persistent session
    async with ClaudeBox(
        session_id="survives-exit",
        workspace_dir=temp_workspace,
        runtime=mock_boxlite,
    ) as box:
        workspace_path = box.workspace_path

        # Create a file
        test_file = Path(workspace_path) / "important.txt"
        test_file.write_text("important data")

    # Workspace and file should still exist
    assert Path(workspace_path).exists()
    assert test_file.exists()
    assert test_file.read_text() == "important data"


@pytest.mark.asyncio
async def test_reconnect_to_session(mock_boxlite, temp_workspace):
    """Test reconnecting to an existing persistent session."""
    # Create initial session
    async with ClaudeBox(
        session_id="reconnect-test",
        workspace_dir=temp_workspace,
        runtime=mock_boxlite,
    ) as box:
        workspace_path = box.workspace_path

        # Create a file
        test_file = Path(workspace_path) / "data.txt"
        test_file.write_text("first session")

    # Reconnect to same session
    box = await ClaudeBox.reconnect(
        "reconnect-test", workspace_dir=temp_workspace, runtime=mock_boxlite
    )
    async with box:
        assert box.session_id == "reconnect-test"
        assert box.is_persistent is True

        # File from previous session should exist
        test_file = Path(box.workspace_path) / "data.txt"
        assert test_file.exists()
        assert test_file.read_text() == "first session"

        # Add another file
        test_file2 = Path(box.workspace_path) / "data2.txt"
        test_file2.write_text("second session")

    # Both files should persist
    assert test_file.exists()
    assert test_file2.exists()


@pytest.mark.asyncio
async def test_reconnect_to_nonexistent_session_raises_error(
    mock_boxlite, temp_workspace
):
    """Test that reconnecting to non-existent session raises error."""
    with pytest.raises(SessionNotFoundError) as exc_info:
        box = await ClaudeBox.reconnect(
            "does-not-exist", workspace_dir=temp_workspace, runtime=mock_boxlite
        )
        async with box:
            pass

    assert exc_info.value.session_id == "does-not-exist"


def test_list_sessions_empty(mock_boxlite, temp_workspace):
    """Test list_sessions returns empty list when no sessions exist."""
    sessions = ClaudeBox.list_sessions(
        workspace_dir=temp_workspace, runtime=mock_boxlite
    )

    assert sessions == []


@pytest.mark.asyncio
async def test_list_sessions_api(mock_boxlite, temp_workspace):
    """Test ClaudeBox.list_sessions() returns all sessions."""
    # Create multiple sessions
    async with ClaudeBox(
        session_id="session-1", workspace_dir=temp_workspace, runtime=mock_boxlite
    ):
        pass

    async with ClaudeBox(
        session_id="session-2", workspace_dir=temp_workspace, runtime=mock_boxlite
    ):
        pass

    async with ClaudeBox(
        session_id="session-3", workspace_dir=temp_workspace, runtime=mock_boxlite
    ):
        pass

    # List sessions
    sessions = ClaudeBox.list_sessions(
        workspace_dir=temp_workspace, runtime=mock_boxlite
    )

    assert len(sessions) == 3

    session_ids = {s.session_id for s in sessions}
    assert session_ids == {"session-1", "session-2", "session-3"}

    # All should have workspace paths
    assert all(s.workspace_path for s in sessions)


@pytest.mark.asyncio
async def test_cleanup_session_api(mock_boxlite, temp_workspace):
    """Test ClaudeBox.cleanup_session() removes session."""
    # Create session
    async with ClaudeBox(
        session_id="cleanup-test", workspace_dir=temp_workspace, runtime=mock_boxlite
    ) as box:
        workspace_path = box.workspace_path

    # Verify exists
    assert Path(workspace_path).exists()

    # Cleanup
    await ClaudeBox.cleanup_session(
        "cleanup-test",
        workspace_dir=temp_workspace,
        runtime=mock_boxlite,
        remove_workspace=True,
    )

    # Should be gone
    assert not Path(workspace_path).exists()

    # Should not be listed
    sessions = ClaudeBox.list_sessions(
        workspace_dir=temp_workspace, runtime=mock_boxlite
    )
    assert not any(s.session_id == "cleanup-test" for s in sessions)


@pytest.mark.asyncio
async def test_cleanup_session_keep_workspace(mock_boxlite, temp_workspace):
    """Test cleanup_session with remove_workspace=False keeps files."""
    # Create session
    async with ClaudeBox(
        session_id="keep-workspace", workspace_dir=temp_workspace, runtime=mock_boxlite
    ) as box:
        workspace_path = box.workspace_path
        test_file = Path(workspace_path) / "keep.txt"
        test_file.write_text("keep this")

    # Cleanup without removing workspace
    await ClaudeBox.cleanup_session(
        "keep-workspace",
        workspace_dir=temp_workspace,
        runtime=mock_boxlite,
        remove_workspace=False,
    )

    # Workspace files should still exist
    assert Path(workspace_path).exists()
    assert test_file.exists()


@pytest.mark.asyncio
async def test_cleanup_nonexistent_session_raises_error(mock_boxlite, temp_workspace):
    """Test that cleanup_session raises error for non-existent session."""
    with pytest.raises(SessionNotFoundError):
        await ClaudeBox.cleanup_session(
            "nonexistent", workspace_dir=temp_workspace, runtime=mock_boxlite
        )


@pytest.mark.asyncio
async def test_backward_compatibility_no_session_id(mock_boxlite, temp_workspace):
    """Test that old API (no session_id) still works."""
    # This is the original usage pattern
    async with ClaudeBox(workspace_dir=temp_workspace, runtime=mock_boxlite) as box:
        # Should create ephemeral session
        assert box.session_id.startswith("ephemeral-")
        assert box.is_persistent is False

        # Should execute commands
        result = await box.code("echo 'backward compatible'")
        assert result.exit_code == 0

        workspace_path = box.workspace_path

    # Should auto-cleanup
    assert not Path(workspace_path).exists()


@pytest.mark.asyncio
async def test_session_metadata_persistence(mock_boxlite, temp_workspace):
    """Test that session metadata persists across reconnections."""
    # Create session
    async with ClaudeBox(
        session_id="metadata-test", workspace_dir=temp_workspace, runtime=mock_boxlite
    ) as box:
        # Execute some commands (would increment turns in real usage)
        await box.code("echo 'command 1'")

    # Reconnect and check metadata still exists
    box = await ClaudeBox.reconnect(
        "metadata-test", workspace_dir=temp_workspace, runtime=mock_boxlite
    )
    async with box:
        # Session metadata should be loaded
        # (actual metadata tracking would happen in code() method)
        assert box.session_id == "metadata-test"


@pytest.mark.asyncio
async def test_multiple_sessions_independent(mock_boxlite, temp_workspace):
    """Test that multiple sessions don't interfere with each other."""
    # Create two sessions simultaneously
    async with ClaudeBox(
        session_id="session-a", workspace_dir=temp_workspace, runtime=mock_boxlite
    ) as box_a:
        async with ClaudeBox(
            session_id="session-b", workspace_dir=temp_workspace, runtime=mock_boxlite
        ) as box_b:
            # Different workspaces
            assert box_a.workspace_path != box_b.workspace_path

            # Create files in each
            file_a = Path(box_a.workspace_path) / "file_a.txt"
            file_b = Path(box_b.workspace_path) / "file_b.txt"

            file_a.write_text("session a data")
            file_b.write_text("session b data")

            # Verify independence
            assert file_a.exists()
            assert file_b.exists()
            assert not (Path(box_a.workspace_path) / "file_b.txt").exists()
            assert not (Path(box_b.workspace_path) / "file_a.txt").exists()


@pytest.mark.asyncio
async def test_auto_remove_behavior(mock_boxlite, temp_workspace):
    """Test that auto_remove is set correctly based on persistence."""
    # Ephemeral: auto_remove should be True
    async with ClaudeBox(workspace_dir=temp_workspace, runtime=mock_boxlite) as box:
        assert box._auto_remove is True

    # Persistent: auto_remove should be False
    async with ClaudeBox(
        session_id="persistent", workspace_dir=temp_workspace, runtime=mock_boxlite
    ) as box:
        assert box._auto_remove is False

    # Explicit override: auto_remove should respect parameter
    async with ClaudeBox(
        session_id="override",
        workspace_dir=temp_workspace,
        runtime=mock_boxlite,
        auto_remove=True,
    ) as box:
        assert box._auto_remove is True


@pytest.mark.asyncio
async def test_box_properties(mock_boxlite, temp_workspace):
    """Test ClaudeBox properties are accessible."""
    async with ClaudeBox(
        session_id="props-test", workspace_dir=temp_workspace, runtime=mock_boxlite
    ) as box:
        # Test all properties
        assert box.id  # BoxLite box ID
        assert box.session_id == "props-test"
        assert box.workspace_path
        assert box.is_persistent is True

        # Verify types
        assert isinstance(box.id, str)
        assert isinstance(box.session_id, str)
        assert isinstance(box.workspace_path, str)
        assert isinstance(box.is_persistent, bool)
