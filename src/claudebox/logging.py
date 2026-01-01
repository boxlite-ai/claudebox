"""Structured logging for ClaudeBox sessions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from claudebox.results import ActionLog

if TYPE_CHECKING:
    pass


class ActionLogger:
    """Structured JSON Lines logger for session actions."""

    def __init__(self, history_file: str, log_level: str = "info"):
        """
        Initialize action logger.

        Args:
            history_file: Path to history.jsonl file
            log_level: Logging level (debug, info, warn, error)
        """
        self.history_file = Path(history_file)
        self.log_level = log_level
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensure history file exists."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self.history_file.touch()

    def log_tool_call(
        self,
        tool: str,
        input_data: dict,
        output_data: dict,
        duration_ms: int | None = None,
        context: dict | None = None,
        session_id: str | None = None,
    ):
        """
        Log a tool call.

        Args:
            tool: Tool name (bash, read_file, write_file, etc.)
            input_data: Tool input parameters
            output_data: Tool output/result
            duration_ms: Execution time in milliseconds
            context: Additional context (working_dir, files_modified, etc.)
            session_id: Session identifier
        """
        log_entry = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "tool_call",
            "tool": tool,
            "input": input_data,
            "output": output_data,
            "duration_ms": duration_ms,
            "context": context or {},
        }
        self._write_log(log_entry)

    def log_error(
        self,
        error: str,
        context: dict | None = None,
        session_id: str | None = None,
    ):
        """
        Log an error.

        Args:
            error: Error message
            context: Additional context
            session_id: Session identifier
        """
        log_entry = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "error",
            "tool": None,
            "input": {},
            "output": {"error": error},
            "duration_ms": None,
            "context": context or {},
        }
        self._write_log(log_entry)

    def log_info(
        self,
        message: str,
        context: dict | None = None,
        session_id: str | None = None,
    ):
        """
        Log an informational message.

        Args:
            message: Info message
            context: Additional context
            session_id: Session identifier
        """
        log_entry = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "info",
            "tool": None,
            "input": {},
            "output": {"message": message},
            "duration_ms": None,
            "context": context or {},
        }
        self._write_log(log_entry)

    def _write_log(self, log_entry: dict):
        """Write log entry to JSON Lines file."""
        with open(self.history_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_logs(
        self,
        limit: int | None = None,
        event_type: str | None = None,
        session_id: str | None = None,
    ) -> list[ActionLog]:
        """
        Retrieve logs with optional filtering.

        Args:
            limit: Maximum number of logs to return (most recent first)
            event_type: Filter by event type (tool_call, error, info)
            session_id: Filter by session ID

        Returns:
            List of ActionLog instances
        """
        if not self.history_file.exists():
            return []

        logs = []
        with open(self.history_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)

                    # Apply filters
                    if event_type and entry.get("event_type") != event_type:
                        continue
                    if session_id and entry.get("session_id") != session_id:
                        continue

                    logs.append(
                        ActionLog(
                            timestamp=entry["timestamp"],
                            event_type=entry["event_type"],
                            tool=entry.get("tool"),
                            input=entry.get("input", {}),
                            output=entry.get("output", {}),
                            duration_ms=entry.get("duration_ms"),
                            context=entry.get("context", {}),
                        )
                    )
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue

        # Return most recent first
        logs.reverse()

        if limit:
            return logs[:limit]
        return logs

    def parse_claude_output(self, json_output: str, session_id: str) -> list[ActionLog]:
        """
        Parse Claude Code CLI JSON output and extract tool calls.

        Args:
            json_output: JSON output from claude --output-format json
            session_id: Session identifier

        Returns:
            List of ActionLog entries for tool calls
        """
        try:
            data = json.loads(json_output)
        except json.JSONDecodeError:
            return []

        logs = []

        # Extract tool calls from Claude output
        # Format depends on Claude Code CLI output structure
        if "tool_calls" in data:
            for tool_call in data["tool_calls"]:
                log_entry = ActionLog(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    event_type="tool_call",
                    tool=tool_call.get("tool"),
                    input=tool_call.get("input", {}),
                    output=tool_call.get("output", {}),
                    duration_ms=tool_call.get("duration_ms"),
                    context={"session_id": session_id},
                )
                logs.append(log_entry)
                self._write_log(
                    {
                        "session_id": session_id,
                        "timestamp": log_entry.timestamp,
                        "event_type": log_entry.event_type,
                        "tool": log_entry.tool,
                        "input": log_entry.input,
                        "output": log_entry.output,
                        "duration_ms": log_entry.duration_ms,
                        "context": log_entry.context,
                    }
                )

        return logs

    def clear_logs(self):
        """Clear all logs from history file."""
        if self.history_file.exists():
            self.history_file.unlink()
        self._ensure_file_exists()

    def get_stats(self) -> dict:
        """
        Get statistics about logged actions.

        Returns:
            Dictionary with stats: total_events, events_by_type, total_duration_ms
        """
        logs = self.get_logs()

        events_by_type: dict[str, int] = {}
        tools_used: set[str] = set()
        total_duration_ms = 0

        for log in logs:
            # Count by event type
            event_type = log.event_type
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1

            # Sum duration
            if log.duration_ms:
                total_duration_ms += log.duration_ms

            # Track tools
            if log.tool:
                tools_used.add(log.tool)

        return {
            "total_events": len(logs),
            "events_by_type": events_by_type,
            "total_duration_ms": total_duration_ms,
            "tools_used": list(tools_used),
        }
