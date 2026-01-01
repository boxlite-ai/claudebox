"""Shared pytest fixtures for ClaudeBox tests."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest


@pytest.fixture
def temp_workspace():
    """
    Temporary workspace directory for testing.

    Creates a temporary directory with claudebox_test_ prefix,
    yields the path, then cleans up after test completes.
    """
    temp_dir = tempfile.mkdtemp(prefix="claudebox_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_boxlite_runtime():
    """
    Mocked BoxLite runtime for testing without VM infrastructure.

    Returns a Mock object with create(), get(), list_info(), and remove() methods.
    """
    runtime = Mock()
    runtime.create = Mock()
    runtime.get = Mock()
    runtime.list_info = Mock(return_value=[])
    runtime.remove = Mock()
    return runtime


@pytest.fixture
def mock_box():
    """
    Mocked Box instance for testing without actual VM.

    Returns a Mock box with id, name, async context managers, and exec() method.
    """
    box = Mock()
    box.id = "box_12345abc"
    box.name = "claudebox-test-session"

    # Mock async context managers
    async def async_enter(*args, **kwargs):
        return box

    async def async_exit(*args, **kwargs):
        return None

    box.__aenter__ = AsyncMock(side_effect=async_enter)
    box.__aexit__ = AsyncMock(side_effect=async_exit)

    # Mock exec method
    async def mock_exec(cmd, args=None, env=None):
        execution = Mock()

        # Mock stdout/stderr streams
        async def stdout_stream():
            yield b'{"result": "success", "is_error": false}\n'

        async def stderr_stream():
            return
            yield  # Empty generator

        execution.stdout = Mock(return_value=stdout_stream())
        execution.stderr = Mock(return_value=stderr_stream())

        # Mock wait result
        wait_result = Mock()
        wait_result.exit_code = 0
        execution.wait = AsyncMock(return_value=wait_result)

        return execution

    box.exec = AsyncMock(side_effect=mock_exec)

    return box


@pytest.fixture
def mock_boxlite(monkeypatch, mock_box, mock_boxlite_runtime):
    """
    Mock the entire boxlite module to avoid importing actual BoxLite.

    This fixture patches the boxlite imports in claudebox.box module.
    """
    # Configure runtime to return our mock box
    mock_boxlite_runtime.create.return_value = mock_box

    # Create mock BoxOptions class
    class MockBoxOptions:
        def __init__(self, **kwargs):
            self.image = kwargs.get("image")
            self.cpus = kwargs.get("cpus")
            self.memory_mib = kwargs.get("memory_mib")
            self.disk_size_gb = kwargs.get("disk_size_gb")
            self.env = kwargs.get("env", [])
            self.volumes = kwargs.get("volumes", [])
            self.ports = kwargs.get("ports", [])
            self.auto_remove = kwargs.get("auto_remove", True)

    # Create mock Boxlite class
    class MockBoxlite:
        @staticmethod
        def default():
            return mock_boxlite_runtime

    # Create a mock boxlite module
    import sys
    from unittest.mock import Mock

    mock_boxlite_module = Mock()
    mock_boxlite_module.Boxlite = MockBoxlite
    mock_boxlite_module.BoxOptions = MockBoxOptions

    # Patch the boxlite module in sys.modules
    monkeypatch.setitem(sys.modules, "boxlite", mock_boxlite_module)

    return mock_boxlite_runtime


@pytest.fixture
def sample_workspace(temp_workspace):
    """
    Pre-created sample workspace for testing.

    Creates a workspace with session_id='test-session' in the temp directory.
    Returns the SessionWorkspace object.
    """
    from claudebox.workspace import WorkspaceManager

    manager = WorkspaceManager(temp_workspace)
    workspace = manager.create_session_workspace("test-session")

    return workspace


@pytest.fixture
def sample_session_metadata(sample_workspace):
    """
    Pre-created session metadata for testing.

    Creates session.json with initial metadata in the sample workspace.
    Returns the SessionMetadata object.
    """
    from claudebox.session import SessionManager

    manager = SessionManager(sample_workspace)
    metadata = manager.create_session("box_sample_123")

    return metadata
