"""Tests for WorkspaceManager and SessionWorkspace."""

from pathlib import Path

import pytest

from claudebox.exceptions import SessionNotFoundError
from claudebox.workspace import SessionInfo, SessionWorkspace, WorkspaceManager


def test_workspace_manager_init_creates_base_structure(temp_workspace):
    """Test that WorkspaceManager creates base directory structure."""
    manager = WorkspaceManager(temp_workspace)

    assert manager.base_dir == Path(temp_workspace)
    assert manager.sessions_dir == Path(temp_workspace) / "sessions"
    assert manager.sessions_dir.exists()


def test_workspace_manager_init_expands_tilde():
    """Test that WorkspaceManager expands ~ to home directory."""
    manager = WorkspaceManager()

    # Should expand to actual home directory
    assert str(manager.base_dir).startswith("/")
    assert "~" not in str(manager.base_dir)


def test_create_session_workspace_creates_all_directories(temp_workspace):
    """Test that create_session_workspace creates all required directories."""
    manager = WorkspaceManager(temp_workspace)
    workspace = manager.create_session_workspace("my-session")

    # Verify workspace structure
    assert isinstance(workspace, SessionWorkspace)
    assert workspace.session_id == "my-session"

    # Verify all directories exist
    assert Path(workspace.workspace_dir).exists()
    assert Path(workspace.metadata_dir).exists()
    assert Path(workspace.artifacts_dir).exists()
    assert Path(workspace.skills_dir).exists()

    # Verify files initialized
    assert Path(workspace.history_file).exists()
    assert Path(workspace.session_file).exists()

    # Verify history.jsonl is empty initially
    with open(workspace.history_file) as f:
        content = f.read()
        assert content == ""

    # Verify session.json has placeholder
    with open(workspace.session_file) as f:
        content = f.read()
        assert content == "{}"


def test_create_session_workspace_collision_adds_suffix(temp_workspace):
    """Test that colliding session IDs get unique suffix."""
    manager = WorkspaceManager(temp_workspace)

    # Create first session
    workspace1 = manager.create_session_workspace("duplicate")
    session_id_1 = workspace1.session_id

    # Create second session with same name
    workspace2 = manager.create_session_workspace("duplicate")
    session_id_2 = workspace2.session_id

    # Should have different IDs (suffix added to second)
    assert session_id_1 == "duplicate"
    assert session_id_2 != session_id_1
    assert session_id_2.startswith("duplicate-")

    # Both directories should exist
    assert Path(workspace1.workspace_dir).exists()
    assert Path(workspace2.workspace_dir).exists()


def test_create_session_workspace_force_overwrites(temp_workspace):
    """Test that force=True allows reusing existing session ID."""
    manager = WorkspaceManager(temp_workspace)

    # Create initial session
    workspace1 = manager.create_session_workspace("forced")

    # Write some content
    test_file = Path(workspace1.workspace_dir) / "test.txt"
    test_file.write_text("original content")

    # Force recreate (allows reusing same session_id)
    workspace2 = manager.create_session_workspace("forced", force=True)

    # Should have same session_id
    assert workspace2.session_id == "forced"

    # Original file should still exist (force doesn't delete files)
    assert test_file.exists()
    assert test_file.read_text() == "original content"


def test_get_session_workspace_success(temp_workspace):
    """Test retrieving an existing workspace."""
    manager = WorkspaceManager(temp_workspace)

    # Create session
    created = manager.create_session_workspace("retrieve-me")

    # Retrieve it
    retrieved = manager.get_session_workspace("retrieve-me")

    # Should match
    assert retrieved.session_id == created.session_id
    assert retrieved.workspace_dir == created.workspace_dir
    assert Path(retrieved.workspace_dir).exists()


def test_get_session_workspace_not_found_raises_error(temp_workspace):
    """Test that get_session_workspace raises SessionNotFoundError."""
    manager = WorkspaceManager(temp_workspace)

    with pytest.raises(SessionNotFoundError) as exc_info:
        manager.get_session_workspace("nonexistent")

    assert "nonexistent" in str(exc_info.value)
    assert exc_info.value.session_id == "nonexistent"


def test_list_sessions_empty(temp_workspace):
    """Test listing sessions when none exist."""
    manager = WorkspaceManager(temp_workspace)

    sessions = manager.list_sessions()

    assert sessions == []


def test_list_sessions_returns_all(temp_workspace):
    """Test listing multiple sessions."""
    manager = WorkspaceManager(temp_workspace)

    # Create multiple sessions
    manager.create_session_workspace("session-1")
    manager.create_session_workspace("session-2")
    manager.create_session_workspace("session-3")

    # List them
    sessions = manager.list_sessions()

    assert len(sessions) == 3

    # Should be SessionInfo objects
    assert all(isinstance(s, SessionInfo) for s in sessions)

    # Extract session IDs
    session_ids = {s.session_id for s in sessions}
    assert session_ids == {"session-1", "session-2", "session-3"}

    # All should have "stopped" status (session.json exists but no runtime info)
    # Note: status is "stopped" when session.json exists, "unknown" when it doesn't
    assert all(s.status == "stopped" for s in sessions)

    # All should have workspace paths
    assert all(s.workspace_path for s in sessions)


def test_session_exists_true(temp_workspace):
    """Test session_exists returns True for existing session."""
    manager = WorkspaceManager(temp_workspace)

    manager.create_session_workspace("exists")

    assert manager.session_exists("exists") is True


def test_session_exists_false(temp_workspace):
    """Test session_exists returns False for non-existent session."""
    manager = WorkspaceManager(temp_workspace)

    assert manager.session_exists("not-there") is False


def test_cleanup_session_keep_workspace(temp_workspace):
    """Test cleanup_session with remove_workspace=False (metadata only)."""
    manager = WorkspaceManager(temp_workspace)

    # Create session
    workspace = manager.create_session_workspace("cleanup-test")

    # Write some workspace files
    test_file = Path(workspace.workspace_dir) / "important.txt"
    test_file.write_text("important data")

    # Cleanup without removing workspace
    manager.cleanup_session("cleanup-test", remove_workspace=False)

    # Workspace directory should still exist
    assert Path(workspace.workspace_dir).exists()
    assert test_file.exists()
    assert test_file.read_text() == "important data"

    # Session directory still exists (just metadata removed)
    # So it will still be listed, but metadata_dir is gone
    metadata_dir = Path(workspace.metadata_dir)
    assert not metadata_dir.exists()

    # Cleaned marker should exist
    session_dir = Path(workspace.workspace_dir).parent
    assert (session_dir / ".cleaned").exists()


def test_cleanup_session_remove_all(temp_workspace):
    """Test cleanup_session with remove_workspace=True (full removal)."""
    manager = WorkspaceManager(temp_workspace)

    # Create session
    workspace = manager.create_session_workspace("delete-me")

    # Write some workspace files
    test_file = Path(workspace.workspace_dir) / "data.txt"
    test_file.write_text("will be deleted")

    workspace_dir = Path(workspace.workspace_dir).parent  # Get session root

    # Cleanup with full removal
    manager.cleanup_session("delete-me", remove_workspace=True)

    # Entire session directory should be gone
    assert not workspace_dir.exists()
    assert not test_file.exists()


def test_cleanup_session_not_found_raises_error(temp_workspace):
    """Test that cleanup_session raises error for non-existent session."""
    manager = WorkspaceManager(temp_workspace)

    with pytest.raises(SessionNotFoundError):
        manager.cleanup_session("never-existed")


def test_custom_base_directory(temp_workspace):
    """Test WorkspaceManager with custom base directory."""
    custom_dir = Path(temp_workspace) / "custom_claudebox"

    manager = WorkspaceManager(str(custom_dir))

    assert manager.base_dir == custom_dir
    assert manager.sessions_dir == custom_dir / "sessions"

    # Create session in custom location
    workspace = manager.create_session_workspace("custom-session")

    assert str(custom_dir) in workspace.workspace_dir
    assert Path(workspace.workspace_dir).exists()


def test_session_workspace_paths(temp_workspace):
    """Test that SessionWorkspace has correct path structure."""
    manager = WorkspaceManager(temp_workspace)
    workspace = manager.create_session_workspace("path-test")

    # Verify path relationships
    base = Path(workspace.workspace_dir).parent

    assert workspace.workspace_dir == str(base / "workspace")
    assert workspace.metadata_dir == str(base / ".claudebox")
    assert workspace.artifacts_dir == str(base / ".claudebox" / "artifacts")
    assert workspace.skills_dir == str(base / "skills")
    assert workspace.history_file == str(base / ".claudebox" / "history.jsonl")
    assert workspace.session_file == str(base / ".claudebox" / "session.json")


def test_session_info_dataclass():
    """Test SessionInfo dataclass structure."""
    info = SessionInfo(
        session_id="test-123",
        status="running",
        created_at="2025-12-31T10:00:00Z",
        workspace_path="/home/user/.claudebox/sessions/test-123",
    )

    assert info.session_id == "test-123"
    assert info.status == "running"
    assert info.created_at == "2025-12-31T10:00:00Z"
    assert info.workspace_path == "/home/user/.claudebox/sessions/test-123"
