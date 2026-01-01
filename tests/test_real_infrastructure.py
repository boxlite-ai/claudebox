"""Real infrastructure tests - no Claude Code execution, just VM/volume/session testing."""

import os
from pathlib import Path

import pytest

from claudebox import ClaudeBox


pytestmark = pytest.mark.real


@pytest.fixture
def ensure_oauth_token():
    """Ensure OAuth token is set."""
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        pytest.skip("CLAUDE_CODE_OAUTH_TOKEN not set")
    return token


@pytest.mark.asyncio
async def test_01_box_creation(ensure_oauth_token, temp_workspace):
    """Test 1: BoxLite VM creation works."""
    print("\n🔹 Test 1: Box creation")

    async with ClaudeBox(
        oauth_token=ensure_oauth_token,
        workspace_dir=temp_workspace
    ) as box:
        print(f"   ✅ Box ID: {box.id}")
        print(f"   ✅ Session: {box.session_id}")
        print(f"   ✅ Workspace: {box.workspace_path}")

        assert box.id
        assert box.session_id
        assert box.workspace_path
        assert Path(box.workspace_path).exists()


@pytest.mark.asyncio
async def test_02_volume_mounting(ensure_oauth_token, temp_workspace):
    """Test 2: Host-to-VM volume mounting works."""
    print("\n🔹 Test 2: Volume mounting")

    session_id = "test-volume"

    try:
        async with ClaudeBox(
            session_id=session_id,
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
        ) as box:
            workspace_path = Path(box.workspace_path)
            metadata_path = Path(box.workspace_path).parent / ".claudebox"

            # Create files on host
            test_file = workspace_path / "from_host.txt"
            test_file.write_text("Hello from host")

            metadata_file = metadata_path / "test.txt"
            metadata_file.write_text("Metadata file")

            print(f"   ✅ Workspace dir exists: {workspace_path.exists()}")
            print(f"   ✅ Metadata dir exists: {metadata_path.exists()}")
            print(f"   ✅ File created: {test_file.exists()}")

            assert test_file.exists()
            assert metadata_file.exists()

    finally:
        await ClaudeBox.cleanup_session(
            session_id,
            workspace_dir=temp_workspace,
            remove_workspace=True
        )


@pytest.mark.asyncio
async def test_03_persistent_session(ensure_oauth_token, temp_workspace):
    """Test 3: Persistent session workspace survives."""
    print("\n🔹 Test 3: Persistent session")

    import uuid
    session_id = f"test-persist-{uuid.uuid4().hex[:6]}"

    try:
        # Create session
        async with ClaudeBox(
            session_id=session_id,
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
        ) as box:
            assert box.is_persistent is True

            workspace_path = Path(box.workspace_path)
            marker = workspace_path / "marker.txt"
            marker.write_text("session 1")

            print(f"   ✅ Session ID: {box.session_id}")
            print(f"   ✅ Is persistent: {box.is_persistent}")

        # Verify workspace persists
        assert workspace_path.exists()
        assert marker.exists()
        print(f"   ✅ Workspace persisted after exit")

        # Reconnect
        box = await ClaudeBox.reconnect(
            session_id,
            workspace_dir=temp_workspace
        )
        async with box:
            assert box.session_id == session_id
            assert marker.exists()
            assert marker.read_text() == "session 1"

            print(f"   ✅ Reconnection works")

    finally:
        await ClaudeBox.cleanup_session(
            session_id,
            workspace_dir=temp_workspace,
            remove_workspace=True
        )


@pytest.mark.asyncio
async def test_04_ephemeral_session(ensure_oauth_token, temp_workspace):
    """Test 4: Ephemeral session auto-cleanup."""
    print("\n🔹 Test 4: Ephemeral session")

    workspace_path = None

    async with ClaudeBox(
        oauth_token=ensure_oauth_token,
        workspace_dir=temp_workspace
    ) as box:
        assert box.is_persistent is False
        assert box.session_id.startswith("ephemeral-")

        workspace_path = Path(box.workspace_path)
        print(f"   ✅ Session ID: {box.session_id}")
        print(f"   ✅ Is ephemeral: {not box.is_persistent}")

    # Workspace should be cleaned up
    assert not workspace_path.exists()
    print(f"   ✅ Workspace auto-cleaned")


@pytest.mark.asyncio
async def test_05_list_sessions(ensure_oauth_token, temp_workspace):
    """Test 5: List sessions API."""
    print("\n🔹 Test 5: List sessions")

    session_ids = ["list-test-1", "list-test-2", "list-test-3"]

    try:
        # Create sessions
        for sid in session_ids:
            async with ClaudeBox(
                session_id=sid,
                oauth_token=ensure_oauth_token,
                workspace_dir=temp_workspace,
            ):
                pass

        # List sessions
        sessions = ClaudeBox.list_sessions(workspace_dir=temp_workspace)
        found_ids = {s.session_id for s in sessions}

        print(f"   Found {len(sessions)} sessions")

        for sid in session_ids:
            assert sid in found_ids
            print(f"   ✅ Found: {sid}")

    finally:
        for sid in session_ids:
            try:
                await ClaudeBox.cleanup_session(
                    sid,
                    workspace_dir=temp_workspace,
                    remove_workspace=True
                )
            except Exception:
                pass


@pytest.mark.asyncio
async def test_06_cleanup_session(ensure_oauth_token, temp_workspace):
    """Test 6: Session cleanup API."""
    print("\n🔹 Test 6: Cleanup session")

    session_id = "cleanup-test"

    # Create session
    async with ClaudeBox(
        session_id=session_id,
        oauth_token=ensure_oauth_token,
        workspace_dir=temp_workspace,
    ) as box:
        workspace_path = Path(box.workspace_path)

    assert workspace_path.exists()

    # Cleanup
    await ClaudeBox.cleanup_session(
        session_id,
        workspace_dir=temp_workspace,
        remove_workspace=True
    )

    assert not workspace_path.exists()
    print(f"   ✅ Session cleaned up")


@pytest.mark.asyncio
async def test_07_session_reconnect(ensure_oauth_token, temp_workspace):
    """Test 7: Reconnect to existing session."""
    print("\n🔹 Test 7: Session reconnect")

    import uuid
    session_id = f"reconnect-{uuid.uuid4().hex[:6]}"

    try:
        # Create session
        async with ClaudeBox(
            session_id=session_id,
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
        ) as box:
            workspace_path = Path(box.workspace_path)
            (workspace_path / "file1.txt").write_text("first")

        # Reconnect
        box = await ClaudeBox.reconnect(session_id, workspace_dir=temp_workspace)
        async with box:
            assert box.session_id == session_id
            assert (workspace_path / "file1.txt").read_text() == "first"

            # Add another file
            (workspace_path / "file2.txt").write_text("second")

        # Both files should persist
        assert (workspace_path / "file1.txt").exists()
        assert (workspace_path / "file2.txt").exists()

        print(f"   ✅ Reconnection preserves workspace")

    finally:
        await ClaudeBox.cleanup_session(
            session_id,
            workspace_dir=temp_workspace,
            remove_workspace=True
        )
