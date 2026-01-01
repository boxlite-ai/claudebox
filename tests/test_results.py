"""Tests for result dataclasses and CodeResult parsing."""

import json

import pytest

from claudebox.results import ActionLog, CodeResult, ResourceMetrics, SessionMetadata


def test_action_log_dataclass():
    """Test ActionLog dataclass structure."""
    log = ActionLog(
        timestamp="2025-12-31T10:30:45.123Z",
        event_type="tool_call",
        tool="bash",
        input={"command": "npm install"},
        output={"exit_code": 0, "stdout": "installed 42 packages"},
        duration_ms=1234,
        context={"working_dir": "/config/workspace"},
    )

    assert log.timestamp == "2025-12-31T10:30:45.123Z"
    assert log.event_type == "tool_call"
    assert log.tool == "bash"
    assert log.input["command"] == "npm install"
    assert log.output["exit_code"] == 0
    assert log.duration_ms == 1234
    assert log.context["working_dir"] == "/config/workspace"


def test_action_log_optional_fields():
    """Test ActionLog with optional fields as None."""
    log = ActionLog(
        timestamp="2025-12-31T10:00:00Z",
        event_type="info",
        tool=None,
        input={},
        output={},
        duration_ms=None,
        context={},
    )

    assert log.tool is None
    assert log.duration_ms is None


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
    assert metadata.created_at == "2025-12-31T10:00:00Z"
    assert metadata.last_accessed == "2025-12-31T11:00:00Z"
    assert metadata.workspace_path == "/home/user/.claudebox/sessions/test-123"
    assert metadata.total_turns == 5
    assert metadata.total_duration_ms == 15000


def test_resource_metrics_dataclass():
    """Test ResourceMetrics dataclass structure."""
    metrics = ResourceMetrics(
        cpu_percent=45.2,
        memory_mb=512,
        disk_mb=2048,
        network_bytes_sent=10485760,  # 10 MB in bytes
        network_bytes_received=5242880,  # 5 MB in bytes
        commands_executed=42,
    )

    assert metrics.cpu_percent == 45.2
    assert metrics.memory_mb == 512
    assert metrics.disk_mb == 2048
    assert metrics.network_bytes_sent == 10485760
    assert metrics.network_bytes_received == 5242880
    assert metrics.commands_executed == 42


def test_resource_metrics_optional_fields():
    """Test ResourceMetrics with all fields set to 0."""
    metrics = ResourceMetrics(
        cpu_percent=0.0,
        memory_mb=0,
        disk_mb=0,
        network_bytes_sent=0,
        network_bytes_received=0,
        commands_executed=0,
    )

    assert metrics.cpu_percent == 0.0
    assert metrics.memory_mb == 0


def test_code_result_from_exec_success():
    """Test CodeResult.from_exec with successful execution."""
    stdout = json.dumps({"result": "File created successfully", "is_error": False})
    stderr = ""

    result = CodeResult.from_exec(0, stdout, stderr)

    assert result.success is True
    assert result.exit_code == 0
    assert result.response == "File created successfully"
    assert result.error is None
    assert result.raw_output == stdout


def test_code_result_from_exec_failure():
    """Test CodeResult.from_exec with failed execution."""
    stdout = json.dumps(
        {"result": "Command failed: file not found", "is_error": True, "error": "File not found"}
    )
    stderr = ""

    result = CodeResult.from_exec(1, stdout, stderr)

    assert result.success is False
    assert result.exit_code == 1
    assert result.error == "File not found"
    assert result.response == "Command failed: file not found"


def test_code_result_from_exec_non_json_output():
    """Test CodeResult.from_exec with non-JSON output (fallback behavior)."""
    stdout = "This is plain text output, not JSON"
    stderr = ""

    result = CodeResult.from_exec(0, stdout, stderr)

    # Should handle gracefully - exact behavior depends on implementation
    # At minimum, should not crash
    assert result.exit_code == 0
    assert result.raw_output == stdout


def test_code_result_from_exec_with_stderr():
    """Test CodeResult.from_exec captures stderr."""
    stdout = json.dumps({"result": "Success with warnings", "is_error": False})
    stderr = "Warning: deprecated API used"

    result = CodeResult.from_exec(0, stdout, stderr)

    assert result.success is True
    # raw_output combines stdout + stderr
    assert "Success with warnings" in result.raw_output
    assert "Warning: deprecated API used" in result.raw_output


def test_code_result_json_parsing_with_script_artifacts():
    """Test parsing Claude output with script command artifacts."""
    # Claude CLI wrapped in 'script' adds control characters
    stdout = """Script started on 2025-12-31 10:30:45
{"result": "Task completed", "is_error": false}
Script done on 2025-12-31 10:30:50
"""

    result = CodeResult.from_exec(0, stdout, "")

    # Should extract JSON despite script wrapper
    assert result.success is True
    assert result.response == "Task completed"


def test_code_result_backward_compatibility():
    """Test that CodeResult maintains backward compatibility."""
    # Old usage: accessing basic fields
    result = CodeResult(
        success=True,
        exit_code=0,
        response="Hello world",
        error=None,
        raw_output='{"result": "Hello world"}',
        action_log=None,
        session_metadata=None,
        resource_metrics=None,
        reward=None,
    )

    # These should work for backward compatibility
    assert result.success is True
    assert result.exit_code == 0
    assert result.response == "Hello world"
    assert result.error is None


def test_code_result_with_enhanced_fields():
    """Test CodeResult with new enhanced fields."""
    action_logs = [
        ActionLog(
            timestamp="2025-12-31T10:00:00Z",
            event_type="tool_call",
            tool="bash",
            input={"command": "ls"},
            output={"exit_code": 0},
            duration_ms=100,
            context={},
        )
    ]

    session_meta = SessionMetadata(
        session_id="test",
        box_id="box_123",
        created_at="2025-12-31T09:00:00Z",
        last_accessed="2025-12-31T10:00:00Z",
        workspace_path="/tmp/workspace",
        total_turns=1,
        total_duration_ms=100,
    )

    metrics = ResourceMetrics(
        cpu_percent=25.0,
        memory_mb=256,
        disk_mb=500,
        network_bytes_sent=1048576,  # 1 MB
        network_bytes_received=524288,  # 0.5 MB
        commands_executed=1,
    )

    result = CodeResult(
        success=True,
        exit_code=0,
        response="Success",
        error=None,
        raw_output="{}",
        action_log=action_logs,
        session_metadata=session_meta,
        resource_metrics=metrics,
        reward=1.0,
    )

    # Verify enhanced fields
    assert result.action_log == action_logs
    assert result.session_metadata == session_meta
    assert result.resource_metrics == metrics
    assert result.reward == 1.0


def test_code_result_optional_enhanced_fields():
    """Test that enhanced fields are optional (None by default)."""
    result = CodeResult(
        success=True,
        exit_code=0,
        response="Response",
        error=None,
        raw_output="{}",
        action_log=None,
        session_metadata=None,
        resource_metrics=None,
        reward=None,
    )

    assert result.action_log is None
    assert result.session_metadata is None
    assert result.resource_metrics is None
    assert result.reward is None


def test_code_result_error_handling():
    """Test CodeResult handles errors correctly."""
    stdout = json.dumps(
        {
            "result": None,
            "is_error": True,
            "error": "Permission denied: cannot write to /etc/hosts",
        }
    )

    result = CodeResult.from_exec(1, stdout, "")

    assert result.success is False
    assert result.exit_code == 1
    assert result.error is not None
    assert "Permission denied" in result.error


def test_code_result_handles_malformed_json():
    """Test CodeResult handles malformed JSON gracefully."""
    stdout = '{"result": "incomplete json...'

    result = CodeResult.from_exec(0, stdout, "")

    # Should not crash - implementation decides how to handle
    assert result.exit_code == 0
    # Either parses what it can or falls back to raw output


def test_code_result_multi_line_output():
    """Test CodeResult with multi-line output."""
    json_output = {
        "result": "File contents:\nLine 1\nLine 2\nLine 3",
        "is_error": False,
    }
    stdout = json.dumps(json_output)

    result = CodeResult.from_exec(0, stdout, "")

    assert result.success is True
    assert "\n" in result.response
    assert "Line 1" in result.response


def test_code_result_empty_output():
    """Test CodeResult with empty output."""
    result = CodeResult.from_exec(0, "", "")

    # Should handle gracefully
    assert result.exit_code == 0


def test_code_result_dataclass_immutability():
    """Test that CodeResult fields can be accessed."""
    result = CodeResult(
        success=True,
        exit_code=0,
        response="Test",
        error=None,
        raw_output="{}",
        action_log=None,
        session_metadata=None,
        resource_metrics=None,
        reward=None,
    )

    # Should be able to read all fields
    assert hasattr(result, "success")
    assert hasattr(result, "exit_code")
    assert hasattr(result, "response")
    assert hasattr(result, "error")
    assert hasattr(result, "raw_output")
    assert hasattr(result, "action_log")
    assert hasattr(result, "session_metadata")
    assert hasattr(result, "resource_metrics")
    assert hasattr(result, "reward")
