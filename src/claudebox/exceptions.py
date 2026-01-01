"""Custom exceptions for ClaudeBox."""

from __future__ import annotations


class ClaudeBoxError(Exception):
    """Base exception for all ClaudeBox errors."""

    pass


class SessionNotFoundError(ClaudeBoxError):
    """Raised when attempting to access a session that doesn't exist."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session '{session_id}' not found")


class SessionAlreadyExistsError(ClaudeBoxError):
    """Raised when attempting to create a session that already exists."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session '{session_id}' already exists")


class WorkspaceError(ClaudeBoxError):
    """Raised when a workspace operation fails."""

    pass


class SkillError(ClaudeBoxError):
    """Raised when a skill operation fails."""

    pass


class SkillNotFoundError(SkillError):
    """Raised when attempting to access a skill that doesn't exist."""

    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        super().__init__(f"Skill '{skill_name}' not found")


class SkillInstallationError(SkillError):
    """Raised when skill installation fails."""

    def __init__(self, skill_name: str, reason: str):
        self.skill_name = skill_name
        self.reason = reason
        super().__init__(f"Failed to install skill '{skill_name}': {reason}")


class TemplateError(ClaudeBoxError):
    """Raised when a template operation fails."""

    pass


class LoggingError(ClaudeBoxError):
    """Raised when logging operations fail."""

    pass
