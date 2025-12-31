"""
Agent tools available for Claude Agent SDK execution.
"""

from typing import Final


class AgentTool:
    """
    Available tools for Claude Agent SDK.

    Usage:
        >>> from claude_box import ClaudeBox, AgentTool
        >>>
        >>> async with ClaudeBox() as claude:
        ...     result = await claude.agent(
        ...         task="Create a script",
        ...         tools=[AgentTool.BASH, AgentTool.WRITE_FILE],
        ...     )

        >>> # Or use all tools
        >>> result = await claude.agent(task="...", tools=AgentTool.ALL)
    """

    # File operations
    READ_FILE: Final[str] = "read_file"
    """Read the contents of a file."""

    WRITE_FILE: Final[str] = "write_file"
    """Write content to a file."""

    LIST_DIR: Final[str] = "list_dir"
    """List directory contents."""

    SEARCH_FILES: Final[str] = "search_files"
    """Search for files using glob patterns."""

    # Shell and code execution
    BASH: Final[str] = "bash"
    """Execute bash shell commands."""

    PYTHON: Final[str] = "python"
    """Execute Python code."""

    # Search
    GREP: Final[str] = "grep"
    """Search for text patterns in files."""

    # Network
    WEB_FETCH: Final[str] = "web_fetch"
    """Fetch content from URLs via HTTP GET."""

    # Computer control
    COMPUTER: Final[str] = "computer"
    """Control the desktop: screenshot, mouse, keyboard, scroll."""

    # Tool collections
    ALL: Final[list[str]] = [
        "bash",
        "read_file",
        "write_file",
        "list_dir",
        "web_fetch",
        "python",
        "search_files",
        "grep",
        "computer",
    ]
    """All available tools."""

    COMPUTER_USE: Final[list[str]] = [
        "computer",
        "bash",
        "read_file",
        "write_file",
    ]
    """Tools for computer use scenarios."""

    DEFAULT: Final[list[str]] = [
        "bash",
        "read_file",
        "write_file",
        "list_dir",
    ]
    """Default tool set: bash, read_file, write_file, list_dir."""

    FILE_TOOLS: Final[list[str]] = [
        "read_file",
        "write_file",
        "list_dir",
        "search_files",
    ]
    """File operation tools only."""

    SAFE: Final[list[str]] = [
        "read_file",
        "list_dir",
        "search_files",
        "grep",
    ]
    """Read-only safe tools (no write, no execution)."""
