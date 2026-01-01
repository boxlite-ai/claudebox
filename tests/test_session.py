"""Tests for SessionManager and SessionMetadata."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from claudebox.exceptions import SessionNotFoundError
from claudebox.results import SessionMetadata
from claudebox.session import SessionManager


def test_create_session_metadata(sample_workspace):
    """Test creating new session metadata."""
    manager = SessionManager(sample_workspace)

    metadata = manager.create_session("box_abc123")

    # Verify metadata structure
    assert isinstance(metadata, SessionMetadata)
    assert metadata.session_id == "test-session"
    assert metadata.box_id == "box_abc123"
    assert metadata.workspace_path == sample_workspace.workspace_dir
    assert metadata.total_turns == 0
    assert metadata.total_duration_ms == 0

    # Verify timestamps are ISO format
    assert "T" in metadata.created_at
    assert "T" in metadata.last_accessed

    # Verify timestamps are recent (within last minute)
    created_dt = datetime.fromisoformat(metadata.created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    time_diff = (now - created_dt).total_seconds()
    assert 0 <= time_diff < 60


def test_create_session_writes_file(sample_workspace):
    """Test that create_session writes session.json to disk."""
    manager = SessionManager(sample_workspace)

    metadata = manager.create_session("box_write_test")

    # Verify file exists
    session_file = Path(sample_workspace.session_file)
    assert session_file.exists()

    # Verify file contains correct data
    with open(session_file) as f:
        data = json.load(f)

    assert data["session_id"] == "test-session"
    assert data["box_id"] == "box_write_test"
    assert data["total_turns"] == 0
    assert data["total_duration_ms"] == 0
    assert "created_at" in data
    assert "last_accessed" in data


def test_load_session_success(sample_session_metadata, sample_workspace):
    """Test loading existing session metadata."""
    manager = SessionManager(sample_workspace)

    loaded = manager.load_session()

    # Should match the created metadata
    assert loaded.session_id == sample_session_metadata.session_id
    assert loaded.box_id == sample_session_metadata.box_id
    assert loaded.workspace_path == sample_session_metadata.workspace_path
    assert loaded.total_turns == sample_session_metadata.total_turns
    assert loaded.total_duration_ms == sample_session_metadata.total_duration_ms


def test_load_session_not_found_missing_file(sample_workspace):
    """Test load_session raises SessionNotFoundError when file missing."""
    manager = SessionManager(sample_workspace)

    # Delete session file
    session_file = Path(sample_workspace.session_file)
    session_file.unlink()

    with pytest.raises(SessionNotFoundError) as exc_info:
        manager.load_session()

    assert exc_info.value.session_id == "test-session"


def test_load_session_empty_file_raises_error(sample_workspace):
    """Test load_session raises error for empty session.json."""
    manager = SessionManager(sample_workspace)

    # Write empty JSON
    with open(sample_workspace.session_file, "w") as f:
        f.write("{}")

    with pytest.raises(SessionNotFoundError):
        manager.load_session()


def test_load_session_corrupted_json_raises_error(sample_workspace):
    """Test load_session handles corrupted JSON gracefully."""
    manager = SessionManager(sample_workspace)

    # Write invalid JSON
    with open(sample_workspace.session_file, "w") as f:
        f.write("{ invalid json content")

    with pytest.raises(SessionNotFoundError):
        manager.load_session()


def test_load_session_missing_required_fields(sample_workspace):
    """Test load_session raises error when required fields missing."""
    manager = SessionManager(sample_workspace)

    # Write JSON missing session_id
    with open(sample_workspace.session_file, "w") as f:
        json.dump(
            {
                "box_id": "box_123",
                "created_at": "2025-12-31T10:00:00Z",
                "last_accessed": "2025-12-31T10:00:00Z",
                "workspace_path": "/tmp/workspace",
            },
            f,
        )

    with pytest.raises(SessionNotFoundError):
        manager.load_session()


def test_update_session_updates_timestamp(sample_session_metadata, sample_workspace):
    """Test that update_session updates last_accessed timestamp."""
    manager = SessionManager(sample_workspace)

    # Get original timestamp
    original_timestamp = sample_session_metadata.last_accessed

    # Wait a tiny bit (not strictly necessary but makes test clearer)
    import time

    time.sleep(0.01)

    # Update session
    manager.update_session(sample_session_metadata)

    # Timestamp should be updated
    assert sample_session_metadata.last_accessed != original_timestamp

    # Load from disk to verify persistence
    loaded = manager.load_session()
    assert loaded.last_accessed == sample_session_metadata.last_accessed


def test_increment_turn(sample_session_metadata, sample_workspace):
    """Test incrementing turn count and duration."""
    manager = SessionManager(sample_workspace)

    # Initial state
    assert sample_session_metadata.total_turns == 0
    assert sample_session_metadata.total_duration_ms == 0

    # Increment once
    updated = manager.increment_turn(sample_session_metadata, duration_ms=1500)

    assert updated.total_turns == 1
    assert updated.total_duration_ms == 1500

    # Increment again
    updated = manager.increment_turn(updated, duration_ms=2300)

    assert updated.total_turns == 2
    assert updated.total_duration_ms == 3800

    # Verify persisted to disk
    loaded = manager.load_session()
    assert loaded.total_turns == 2
    assert loaded.total_duration_ms == 3800


def test_increment_turn_updates_last_accessed(sample_session_metadata, sample_workspace):
    """Test that increment_turn also updates last_accessed."""
    manager = SessionManager(sample_workspace)

    original_timestamp = sample_session_metadata.last_accessed

    import time

    time.sleep(0.01)

    # Increment turn
    updated = manager.increment_turn(sample_session_metadata, duration_ms=1000)

    # Timestamp should be updated
    assert updated.last_accessed != original_timestamp


def test_get_box_name():
    """Test box name generation from session ID."""
    box_name = SessionManager.get_box_name("my-dev-env")

    assert box_name == "claudebox-my-dev-env"


def test_get_box_name_with_special_characters():
    """Test box name generation with special characters."""
    box_name = SessionManager.get_box_name("project_123-test")

    # Should preserve special characters
    assert box_name == "claudebox-project_123-test"


def test_session_exists_true(sample_session_metadata, sample_workspace):
    """Test session_exists returns True for valid session."""
    manager = SessionManager(sample_workspace)

    assert manager.session_exists() is True


def test_session_exists_false_no_file(sample_workspace):
    """Test session_exists returns False when file doesn't exist."""
    manager = SessionManager(sample_workspace)

    # Delete session file
    Path(sample_workspace.session_file).unlink()

    assert manager.session_exists() is False


def test_session_exists_false_empty_file(sample_workspace):
    """Test session_exists returns False for empty/placeholder file."""
    manager = SessionManager(sample_workspace)

    # File already has {} placeholder from workspace creation
    assert manager.session_exists() is False


def test_session_metadata_dataclass():
    """Test SessionMetadata dataclass structure."""
    metadata = SessionMetadata(
        session_id="test-123",
        box_id="box_abc",
        created_at="2025-12-31T10:00:00Z",
        last_accessed="2025-12-31T11:00:00Z",
        workspace_path="/home/user/.claudebox/sessions/test-123",
        total_turns=5,
        total_duration_ms=15000,
    )

    assert metadata.session_id == "test-123"
    assert metadata.box_id == "box_abc"
    assert metadata.total_turns == 5
    assert metadata.total_duration_ms == 15000


def test_multiple_sessions_independent(temp_workspace):
    """Test that multiple SessionManagers don't interfere."""
    from claudebox.workspace import WorkspaceManager

    workspace_mgr = WorkspaceManager(temp_workspace)

    # Create two sessions
    workspace1 = workspace_mgr.create_session_workspace("session-1")
    workspace2 = workspace_mgr.create_session_workspace("session-2")

    manager1 = SessionManager(workspace1)
    manager2 = SessionManager(workspace2)

    # Create metadata for both
    metadata1 = manager1.create_session("box_1")
    metadata2 = manager2.create_session("box_2")

    # Increment different amounts
    manager1.increment_turn(metadata1, duration_ms=1000)
    manager2.increment_turn(metadata2, duration_ms=2000)
    manager2.increment_turn(metadata2, duration_ms=2000)

    # Load and verify independence
    loaded1 = manager1.load_session()
    loaded2 = manager2.load_session()

    assert loaded1.session_id == "session-1"
    assert loaded1.total_turns == 1
    assert loaded1.total_duration_ms == 1000

    assert loaded2.session_id == "session-2"
    assert loaded2.total_turns == 2
    assert loaded2.total_duration_ms == 4000
