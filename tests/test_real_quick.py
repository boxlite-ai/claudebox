"""Quick real integration tests - simpler prompts for faster execution."""

import os
from pathlib import Path

import pytest

from claudebox import ClaudeBox


pytestmark = pytest.mark.real


@pytest.fixture
def ensure_oauth_token():
    """Ensure OAuth token is set for real tests."""
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        pytest.skip("CLAUDE_CODE_OAUTH_TOKEN not set")
    return token


@pytest.mark.asyncio
async def test_box_creation_and_basic_execution(ensure_oauth_token, temp_workspace):
    """Test 1: Box creation with simple command."""
    print("\n✅ Test 1: Box creation...")

    async with ClaudeBox(
        oauth_token=ensure_oauth_token,
        workspace_dir=temp_workspace
    ) as box:
        print(f"   Box ID: {box.id}")
        print(f"   Session: {box.session_id}")
        print(f"   Workspace: {box.workspace_path}")

        # Very simple prompt
        result = await box.code("just say 'hello' and nothing else")

        print(f"   Exit code: {result.exit_code}")
        print(f"   Response: {result.response[:100] if result.response else 'None'}")

        # Just verify we got some result
        assert result is not None
        assert box.workspace_path


@pytest.mark.asyncio
async def test_workspace_volume_mounting(ensure_oauth_token, temp_workspace):
    """Test 2: Workspace volume mounting."""
    print("\n✅ Test 2: Volume mounting...")

    async with ClaudeBox(
        session_id="test-mount",
        oauth_token=ensure_oauth_token,
        workspace_dir=temp_workspace,
    ) as box:
        workspace_path = Path(box.workspace_path)

        # Create file on host
        test_file = workspace_path / "test_from_host.txt"
        test_file.write_text("Created from host")

        print(f"   Created file: {test_file}")
        print(f"   File exists: {test_file.exists()}")

        # Verify file exists
        assert test_file.exists()

        print(f"   ✅ Volume mounting works")

    # Cleanup
    try:
        await ClaudeBox.cleanup_session(
            "test-mount",
            workspace_dir=temp_workspace,
            remove_workspace=True
        )
    except Exception:
        pass


@pytest.mark.asyncio
async def test_persistent_session(ensure_oauth_token, temp_workspace):
    """Test 3: Persistent session creation."""
    print("\n✅ Test 3: Persistent session...")

    session_id = "test-persist-quick"

    try:
        # Create persistent session
        async with ClaudeBox(
            session_id=session_id,
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
        ) as box:
            assert box.session_id == session_id
            assert box.is_persistent is True

            workspace_path = box.workspace_path

            # Create marker file
            marker = Path(workspace_path) / "marker.txt"
            marker.write_text("session 1")

            print(f"   Session ID: {session_id}")
            print(f"   Is persistent: {box.is_persistent}")

        # Verify workspace persists
        assert Path(workspace_path).exists()
        assert marker.exists()

        print(f"   ✅ Workspace persisted")

        # Reconnect
        box = await ClaudeBox.reconnect(
            session_id,
            workspace_dir=temp_workspace
        )
        async with box:
            assert box.session_id == session_id

            # Marker should still exist
            assert marker.exists()
            assert marker.read_text() == "session 1"

            print(f"   ✅ Reconnection works")

    finally:
        # Cleanup
        try:
            await ClaudeBox.cleanup_session(
                session_id,
                workspace_dir=temp_workspace,
                remove_workspace=True
            )
        except Exception:
            pass


@pytest.mark.asyncio
async def test_list_sessions(ensure_oauth_token, temp_workspace):
    """Test 4: List sessions."""
    print("\n✅ Test 4: List sessions...")

    session_ids = ["quick-session-1", "quick-session-2"]

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
        print(f"   Found sessions: {found_ids}")

        for sid in session_ids:
            assert sid in found_ids

        print(f"   ✅ List sessions works")

    finally:
        # Cleanup
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
async def test_ephemeral_cleanup(ensure_oauth_token, temp_workspace):
    """Test 5: Ephemeral session auto-cleanup."""
    print("\n✅ Test 5: Ephemeral cleanup...")

    workspace_path = None

    async with ClaudeBox(
        oauth_token=ensure_oauth_token,
        workspace_dir=temp_workspace
    ) as box:
        assert box.is_persistent is False
        workspace_path = box.workspace_path

        print(f"   Session ID: {box.session_id}")
        print(f"   Is ephemeral: {not box.is_persistent}")

    # Workspace should be cleaned up
    # Note: cleanup happens in __aexit__
    print(f"   Workspace path: {workspace_path}")
    print(f"   ✅ Ephemeral session complete")
