"""Session metadata management for ClaudeBox."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from claudebox.exceptions import SessionNotFoundError
from claudebox.results import SessionMetadata
from claudebox.workspace import SessionWorkspace


class SessionManager:
    """Manages session metadata and BoxLite box lifecycle."""

    def __init__(self, workspace: SessionWorkspace):
        """
        Initialize session manager.

        Args:
            workspace: SessionWorkspace for this session
        """
        self.workspace = workspace
        self.session_file = Path(workspace.session_file)

    def create_session(self, box_id: str) -> SessionMetadata:
        """
        Create new session metadata.

        Args:
            box_id: BoxLite box ID

        Returns:
            SessionMetadata with initialized values
        """
        now = datetime.now(timezone.utc).isoformat()

        metadata = SessionMetadata(
            session_id=self.workspace.session_id,
            box_id=box_id,
            created_at=now,
            last_accessed=now,
            workspace_path=self.workspace.workspace_dir,
            total_turns=0,
            total_duration_ms=0,
        )

        self._save_metadata(metadata)
        return metadata

    def load_session(self) -> SessionMetadata:
        """
        Load existing session metadata.

        Returns:
            SessionMetadata from session.json

        Raises:
            SessionNotFoundError: If session.json doesn't exist or is invalid
        """
        if not self.session_file.exists():
            raise SessionNotFoundError(self.workspace.session_id)

        try:
            with open(self.session_file) as f:
                data = json.load(f)

            # Handle empty or incomplete session files
            if not data or "session_id" not in data:
                raise SessionNotFoundError(self.workspace.session_id)

            return SessionMetadata(
                session_id=data["session_id"],
                box_id=data["box_id"],
                created_at=data["created_at"],
                last_accessed=data["last_accessed"],
                workspace_path=data["workspace_path"],
                total_turns=data.get("total_turns", 0),
                total_duration_ms=data.get("total_duration_ms", 0),
            )

        except (json.JSONDecodeError, KeyError, OSError) as e:
            raise SessionNotFoundError(self.workspace.session_id) from e

    def update_session(self, metadata: SessionMetadata):
        """
        Update session metadata.

        Args:
            metadata: SessionMetadata to save
        """
        # Update last_accessed timestamp
        metadata.last_accessed = datetime.now(timezone.utc).isoformat()
        self._save_metadata(metadata)

    def increment_turn(
        self, metadata: SessionMetadata, duration_ms: int
    ) -> SessionMetadata:
        """
        Increment turn count and duration.

        Args:
            metadata: Current SessionMetadata
            duration_ms: Duration of this turn in milliseconds

        Returns:
            Updated SessionMetadata
        """
        metadata.total_turns += 1
        metadata.total_duration_ms += duration_ms
        self.update_session(metadata)
        return metadata

    def _save_metadata(self, metadata: SessionMetadata):
        """Save metadata to session.json."""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "session_id": metadata.session_id,
            "box_id": metadata.box_id,
            "created_at": metadata.created_at,
            "last_accessed": metadata.last_accessed,
            "workspace_path": metadata.workspace_path,
            "total_turns": metadata.total_turns,
            "total_duration_ms": metadata.total_duration_ms,
        }

        with open(self.session_file, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def get_box_name(session_id: str) -> str:
        """
        Get BoxLite box name for session.

        Args:
            session_id: Session identifier

        Returns:
            Box name in format: claudebox-{session_id}
        """
        return f"claudebox-{session_id}"

    def session_exists(self) -> bool:
        """Check if session metadata file exists."""
        return self.session_file.exists() and self.session_file.stat().st_size > 2  # More than just "{}"
