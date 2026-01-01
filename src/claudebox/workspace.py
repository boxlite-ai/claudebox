"""Workspace management for ClaudeBox sessions."""

from __future__ import annotations

import os
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

from claudebox.exceptions import SessionAlreadyExistsError, SessionNotFoundError, WorkspaceError


@dataclass
class SessionWorkspace:
    """Represents a session's workspace paths."""

    session_id: str
    base_dir: str  # Base session directory: ~/.claudebox/sessions/{id}/
    workspace_dir: str  # Working directory: ~/.claudebox/sessions/{id}/workspace/
    metadata_dir: str  # Metadata directory: ~/.claudebox/sessions/{id}/.claudebox/
    history_file: str  # Action log: ~/.claudebox/sessions/{id}/.claudebox/history.jsonl
    session_file: str  # Session metadata: ~/.claudebox/sessions/{id}/.claudebox/session.json
    artifacts_dir: str  # Artifacts: ~/.claudebox/sessions/{id}/.claudebox/artifacts/
    skills_dir: str  # Session skills: ~/.claudebox/sessions/{id}/skills/


@dataclass
class SessionInfo:
    """Information about a session."""

    session_id: str
    status: str  # "active", "stopped", "unknown"
    created_at: str
    workspace_path: str
    box_id: str | None = None


class WorkspaceManager:
    """Manages ~/.claudebox/ structure and session directories."""

    def __init__(self, base_dir: str | None = None):
        """
        Initialize workspace manager.

        Args:
            base_dir: Base directory for all ClaudeBox data (default: ~/.claudebox)
        """
        if base_dir is None:
            base_dir = os.path.expanduser("~/.claudebox")
        self.base_dir = Path(base_dir)
        self.sessions_dir = self.base_dir / "sessions"
        self.global_skills_dir = self.base_dir / "skills"
        self.templates_dir = self.base_dir / "templates"
        self.config_dir = self.base_dir / "config"

        # Ensure base directories exist
        self._ensure_base_structure()

    def _ensure_base_structure(self):
        """Ensure ~/.claudebox/ base structure exists."""
        try:
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
            self.global_skills_dir.mkdir(parents=True, exist_ok=True)
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise WorkspaceError(f"Failed to create base directory structure: {e}")

    def _generate_session_id(self, user_session_id: str) -> str:
        """
        Generate full session ID with random suffix if needed.

        Args:
            user_session_id: User-provided session ID

        Returns:
            Full session ID (user_id if unique, or user_id-{suffix} if collision)
        """
        # Check if session_id already exists
        session_path = self.sessions_dir / user_session_id
        if not session_path.exists():
            return user_session_id

        # Add random suffix to avoid collision
        suffix = str(uuid.uuid4())[:8]
        return f"{user_session_id}-{suffix}"

    def create_session_workspace(
        self, session_id: str, force: bool = False
    ) -> SessionWorkspace:
        """
        Create directory structure for new session.

        Args:
            session_id: User-provided session identifier
            force: If True, overwrite existing session

        Returns:
            SessionWorkspace with all paths

        Raises:
            SessionAlreadyExistsError: If session exists and force=False
            WorkspaceError: If directory creation fails
        """
        # Generate unique session ID if needed
        full_session_id = session_id if force else self._generate_session_id(session_id)

        session_dir = self.sessions_dir / full_session_id

        if session_dir.exists() and not force:
            raise SessionAlreadyExistsError(full_session_id)

        try:
            # Create session directory structure
            workspace_dir = session_dir / "workspace"
            metadata_dir = session_dir / ".claudebox"
            artifacts_dir = metadata_dir / "artifacts"
            skills_dir = session_dir / "skills"

            # Create all directories
            workspace_dir.mkdir(parents=True, exist_ok=True)
            metadata_dir.mkdir(parents=True, exist_ok=True)
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            skills_dir.mkdir(parents=True, exist_ok=True)

            # File paths
            history_file = metadata_dir / "history.jsonl"
            session_file = metadata_dir / "session.json"

            # Initialize empty files
            history_file.touch(exist_ok=True)
            if not session_file.exists():
                session_file.write_text("{}")

            return SessionWorkspace(
                session_id=full_session_id,
                base_dir=str(session_dir),
                workspace_dir=str(workspace_dir),
                metadata_dir=str(metadata_dir),
                history_file=str(history_file),
                session_file=str(session_file),
                artifacts_dir=str(artifacts_dir),
                skills_dir=str(skills_dir),
            )

        except OSError as e:
            raise WorkspaceError(f"Failed to create session workspace: {e}")

    def get_session_workspace(self, session_id: str) -> SessionWorkspace:
        """
        Get existing session workspace.

        Args:
            session_id: Session identifier

        Returns:
            SessionWorkspace with all paths

        Raises:
            SessionNotFoundError: If session doesn't exist
        """
        session_dir = self.sessions_dir / session_id

        if not session_dir.exists():
            raise SessionNotFoundError(session_id)

        workspace_dir = session_dir / "workspace"
        metadata_dir = session_dir / ".claudebox"
        artifacts_dir = metadata_dir / "artifacts"
        skills_dir = session_dir / "skills"
        history_file = metadata_dir / "history.jsonl"
        session_file = metadata_dir / "session.json"

        return SessionWorkspace(
            session_id=session_id,
            base_dir=str(session_dir),
            workspace_dir=str(workspace_dir),
            metadata_dir=str(metadata_dir),
            history_file=str(history_file),
            session_file=str(session_file),
            artifacts_dir=str(artifacts_dir),
            skills_dir=str(skills_dir),
        )

    def list_sessions(self) -> list[SessionInfo]:
        """
        List all sessions (from filesystem).

        Returns:
            List of SessionInfo for all sessions
        """
        sessions: list[SessionInfo] = []

        if not self.sessions_dir.exists():
            return sessions

        for session_dir in self.sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue

            session_id = session_dir.name
            workspace_path = str(session_dir / "workspace")
            session_file = session_dir / ".claudebox" / "session.json"

            # Try to read session metadata
            created_at = "unknown"
            box_id = None
            status = "unknown"

            if session_file.exists():
                try:
                    import json

                    with open(session_file) as f:
                        data = json.load(f)
                        created_at = data.get("created_at", "unknown")
                        box_id = data.get("box_id")
                        # Status is determined by BoxLite runtime, default to unknown
                        status = "stopped"  # Default assumption
                except (json.JSONDecodeError, OSError):
                    pass

            sessions.append(
                SessionInfo(
                    session_id=session_id,
                    status=status,
                    created_at=created_at,
                    workspace_path=workspace_path,
                    box_id=box_id,
                )
            )

        return sessions

    def cleanup_session(self, session_id: str, remove_workspace: bool = False):
        """
        Remove session directory.

        Args:
            session_id: Session to remove
            remove_workspace: If True, delete entire session directory

        Raises:
            SessionNotFoundError: If session doesn't exist
            WorkspaceError: If removal fails
        """
        session_dir = self.sessions_dir / session_id

        if not session_dir.exists():
            raise SessionNotFoundError(session_id)

        try:
            if remove_workspace:
                # Remove entire session directory
                shutil.rmtree(session_dir)
            else:
                # Only remove metadata, keep workspace
                metadata_dir = session_dir / ".claudebox"
                if metadata_dir.exists():
                    shutil.rmtree(metadata_dir)

                # Mark session as cleaned
                cleanup_marker = session_dir / ".cleaned"
                cleanup_marker.touch()

        except OSError as e:
            raise WorkspaceError(f"Failed to cleanup session: {e}")

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        return (self.sessions_dir / session_id).exists()
