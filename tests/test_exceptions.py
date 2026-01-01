"""Tests for ClaudeBox custom exceptions."""

import pytest

from claudebox.exceptions import (
    ClaudeBoxError,
    LoggingError,
    SessionAlreadyExistsError,
    SessionNotFoundError,
    SkillError,
    SkillInstallationError,
    SkillNotFoundError,
    TemplateError,
    WorkspaceError,
)


def test_claudebox_error_base():
    """Test base ClaudeBoxError exception."""
    error = ClaudeBoxError("Something went wrong")

    assert str(error) == "Something went wrong"
    assert isinstance(error, Exception)


def test_session_not_found_error_message():
    """Test SessionNotFoundError has correct message format."""
    error = SessionNotFoundError("my-session")

    assert "my-session" in str(error)
    assert "not found" in str(error).lower()
    assert error.session_id == "my-session"


def test_session_not_found_error_inheritance():
    """Test SessionNotFoundError inherits from ClaudeBoxError."""
    error = SessionNotFoundError("test")

    assert isinstance(error, SessionNotFoundError)
    assert isinstance(error, ClaudeBoxError)
    assert isinstance(error, Exception)


def test_session_already_exists_error_message():
    """Test SessionAlreadyExistsError has correct message format."""
    error = SessionAlreadyExistsError("duplicate-session")

    assert "duplicate-session" in str(error)
    assert "already exists" in str(error).lower()
    assert error.session_id == "duplicate-session"


def test_session_already_exists_error_inheritance():
    """Test SessionAlreadyExistsError inherits from ClaudeBoxError."""
    error = SessionAlreadyExistsError("test")

    assert isinstance(error, SessionAlreadyExistsError)
    assert isinstance(error, ClaudeBoxError)


def test_workspace_error():
    """Test WorkspaceError base exception."""
    error = WorkspaceError("Workspace problem")

    assert str(error) == "Workspace problem"
    assert isinstance(error, ClaudeBoxError)


def test_skill_error():
    """Test SkillError base exception."""
    error = SkillError("Skill problem")

    assert str(error) == "Skill problem"
    assert isinstance(error, ClaudeBoxError)


def test_skill_not_found_error():
    """Test SkillNotFoundError with skill name."""
    error = SkillNotFoundError("email-sender")

    assert "email-sender" in str(error)
    assert "not found" in str(error).lower()
    assert error.skill_name == "email-sender"
    assert isinstance(error, SkillError)
    assert isinstance(error, ClaudeBoxError)


def test_skill_installation_error():
    """Test SkillInstallationError with skill name and reason."""
    error = SkillInstallationError("database", "pip install failed")

    assert "database" in str(error)
    assert "pip install failed" in str(error)
    assert error.skill_name == "database"
    assert isinstance(error, SkillError)


def test_template_error():
    """Test TemplateError exception."""
    error = TemplateError("Invalid template configuration")

    assert str(error) == "Invalid template configuration"
    assert isinstance(error, ClaudeBoxError)


def test_logging_error():
    """Test LoggingError exception."""
    error = LoggingError("Failed to write log file")

    assert str(error) == "Failed to write log file"
    assert isinstance(error, ClaudeBoxError)


def test_all_exceptions_inherit_from_base():
    """Test that all ClaudeBox exceptions inherit from ClaudeBoxError."""
    exceptions = [
        SessionNotFoundError("test"),
        SessionAlreadyExistsError("test"),
        WorkspaceError("test"),
        SkillError("test"),
        SkillNotFoundError("test"),
        SkillInstallationError("test", "reason"),
        TemplateError("test"),
        LoggingError("test"),
    ]

    for exc in exceptions:
        assert isinstance(exc, ClaudeBoxError)
        assert isinstance(exc, Exception)


def test_exception_can_be_raised_and_caught():
    """Test that exceptions can be raised and caught normally."""
    with pytest.raises(SessionNotFoundError) as exc_info:
        raise SessionNotFoundError("missing")

    assert exc_info.value.session_id == "missing"


def test_exception_can_be_caught_as_base_class():
    """Test that specific exceptions can be caught as ClaudeBoxError."""
    with pytest.raises(ClaudeBoxError):
        raise SessionNotFoundError("test")

    with pytest.raises(ClaudeBoxError):
        raise SkillNotFoundError("test")


def test_exception_attributes_preserved():
    """Test that exception attributes are preserved through raise/catch."""

    def raise_session_error():
        raise SessionNotFoundError("my-session-id")

    with pytest.raises(SessionNotFoundError) as exc_info:
        raise_session_error()

    # Attribute should be accessible
    assert exc_info.value.session_id == "my-session-id"


def test_skill_installation_error_with_details():
    """Test SkillInstallationError captures detailed error information."""
    detailed_error = """
    Command failed: pip install invalid-package
    Exit code: 1
    Output: ERROR: Could not find a version that satisfies the requirement
    """

    error = SkillInstallationError("invalid-package", detailed_error)

    assert "invalid-package" in str(error)
    assert "pip install" in str(error)
    assert error.skill_name == "invalid-package"


def test_exception_repr():
    """Test exception repr for debugging."""
    error = SessionNotFoundError("debug-session")

    # repr should be informative
    repr_str = repr(error)
    assert "SessionNotFoundError" in repr_str
    assert "debug-session" in repr_str
