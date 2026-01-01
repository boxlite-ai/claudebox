"""Result types for ClaudeBox."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

# Strip ANSI escape codes
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\][^\x07]*\x07|\x1b\[\?[0-9]+[hl]")


@dataclass
class ActionLog:
    """Single action/tool call in a session."""

    timestamp: str  # ISO 8601 format
    event_type: str  # "tool_call", "error", "info"
    tool: str | None  # Tool name (bash, read_file, etc.)
    input: dict  # Tool input parameters
    output: dict  # Tool output/result
    duration_ms: int | None  # Execution time
    context: dict  # Working directory, files modified, etc.


@dataclass
class SessionMetadata:
    """Metadata about a session."""

    session_id: str
    box_id: str
    created_at: str
    last_accessed: str
    workspace_path: str
    total_turns: int
    total_duration_ms: int


@dataclass
class ResourceMetrics:
    """Resource usage metrics from BoxLite."""

    cpu_percent: float
    memory_mb: int
    disk_mb: int
    commands_executed: int
    network_bytes_sent: int
    network_bytes_received: int


@dataclass
class CodeResult:
    """Result from Claude Code CLI execution."""

    success: bool
    response: str
    exit_code: int
    raw_output: str = ""
    error: str | None = None

    # Enhanced observability (Phase 1)
    action_log: list[ActionLog] = field(default_factory=list)
    session_metadata: SessionMetadata | None = None
    resource_metrics: ResourceMetrics | None = None

    # RL support (Phase 3)
    reward: float | None = None

    @classmethod
    def from_exec(
        cls,
        exit_code: int,
        stdout: str,
        stderr: str,
        session_metadata: SessionMetadata | None = None,
        resource_metrics: ResourceMetrics | None = None,
        action_log: list[ActionLog] | None = None,
        reward: float | None = None,
    ) -> CodeResult:
        """Create CodeResult from execution output."""
        output = ANSI_ESCAPE.sub("", stdout + stderr).strip()
        success = exit_code == 0
        response = output
        error = None

        try:
            if "{" in output:
                json_str = output[output.index("{") : output.rindex("}") + 1]
                data = json.loads(json_str)
                response = data.get("result", data.get("response", output))
                if data.get("is_error"):
                    error = data.get("error", "Unknown error")
                    success = False
        except (json.JSONDecodeError, ValueError):
            if not success:
                error = output

        return cls(
            success=success,
            response=response,
            exit_code=exit_code,
            raw_output=output,
            error=error,
            action_log=action_log or [],
            session_metadata=session_metadata,
            resource_metrics=resource_metrics,
            reward=reward,
        )
