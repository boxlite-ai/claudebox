"""Tests for AgentTool definitions."""

from claude_box import AgentTool


def test_agent_tool_constants():
    """Test that tool constants are defined."""
    assert AgentTool.BASH == "bash"
    assert AgentTool.READ_FILE == "read_file"
    assert AgentTool.WRITE_FILE == "write_file"
    assert AgentTool.LIST_DIR == "list_dir"
    assert AgentTool.WEB_FETCH == "web_fetch"
    assert AgentTool.PYTHON == "python"
    assert AgentTool.SEARCH_FILES == "search_files"
    assert AgentTool.GREP == "grep"


def test_agent_tool_collections():
    """Test tool collections."""
    assert len(AgentTool.ALL) == 8
    assert len(AgentTool.DEFAULT) == 4
    assert len(AgentTool.SAFE) == 4
    assert len(AgentTool.FILE_TOOLS) == 4

    # Default should not include dangerous tools
    assert AgentTool.WEB_FETCH not in AgentTool.DEFAULT

    # Safe should be read-only
    assert AgentTool.WRITE_FILE not in AgentTool.SAFE
    assert AgentTool.BASH not in AgentTool.SAFE
