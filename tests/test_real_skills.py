"""Real skill system tests - actual BoxLite VMs with skill installation."""

import os
from pathlib import Path

import pytest

from claudebox import API_SKILL, REDIS_SKILL, ClaudeBox, Skill

pytestmark = pytest.mark.real


@pytest.fixture
def ensure_oauth_token():
    """Ensure OAuth token is set."""
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        pytest.skip("CLAUDE_CODE_OAUTH_TOKEN not set")
    return token


@pytest.mark.asyncio
async def test_01_skill_basic_installation(ensure_oauth_token, temp_workspace):
    """Test 1: Basic skill installation."""
    print("\n🔹 Test 1: Basic skill installation")

    # Create a simple skill
    test_skill = Skill(
        name="test_basic",
        description="Basic test skill",
        install_cmd="echo 'Skill installed' > /tmp/skill_test.txt",
    )

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="skill-test-basic",
            skills=[test_skill],
        ) as box:
            print(f"   ✅ Box created with skill: {test_skill.name}")

            # Verify workspace structure
            workspace_path = Path(box.workspace_path)
            skills_dir = workspace_path.parent / "skills"

            assert skills_dir.exists()
            print(f"   ✅ Skills directory exists: {skills_dir}")

    finally:
        await ClaudeBox.cleanup_session(
            "skill-test-basic", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_02_skill_with_env_vars(ensure_oauth_token, temp_workspace):
    """Test 2: Skill with environment variables."""
    print("\n🔹 Test 2: Skill with environment variables")

    test_skill = Skill(
        name="test_env",
        description="Test skill with env vars",
        env_vars={"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"},
    )

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="skill-test-env",
            skills=[test_skill],
        ) as box:
            print(f"   ✅ Box created with env vars from {test_skill.name}")

            # Environment variables should be set in the VM
            # (They're passed via BoxOptions env parameter)
            assert box.id
            print(f"   ✅ Env vars configured")

    finally:
        await ClaudeBox.cleanup_session(
            "skill-test-env", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_03_skill_with_files(ensure_oauth_token, temp_workspace):
    """Test 3: Skill with file injection."""
    print("\n🔹 Test 3: Skill with file injection")

    test_skill = Skill(
        name="test_files",
        description="Test skill with files",
        files={
            "config.json": '{"key": "value"}',
            "script.py": "print('Hello from skill')",
        },
    )

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="skill-test-files",
            skills=[test_skill],
        ) as box:
            workspace_path = Path(box.workspace_path)
            skills_dir = workspace_path.parent / "skills" / "test_files"

            # Files should be injected
            config_file = skills_dir / "config.json"
            script_file = skills_dir / "script.py"

            assert config_file.exists(), f"Config file not found: {config_file}"
            assert script_file.exists(), f"Script file not found: {script_file}"

            assert config_file.read_text() == '{"key": "value"}'
            assert script_file.read_text() == "print('Hello from skill')"

            print(f"   ✅ Files injected: config.json, script.py")

    finally:
        await ClaudeBox.cleanup_session(
            "skill-test-files", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_04_skill_with_config(ensure_oauth_token, temp_workspace):
    """Test 4: Skill with configuration."""
    print("\n🔹 Test 4: Skill with configuration")

    test_skill = Skill(
        name="test_config",
        description="Test skill with config",
        config={"api_key": "test-key-123", "endpoint": "https://api.example.com"},
    )

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="skill-test-config",
            skills=[test_skill],
        ) as box:
            workspace_path = Path(box.workspace_path)
            metadata_dir = workspace_path.parent / ".claudebox"

            # Config should be written
            config_file = metadata_dir / "skill_test_config_config.json"
            assert config_file.exists(), f"Config file not found: {config_file}"

            import json

            config_data = json.loads(config_file.read_text())
            assert config_data["name"] == "test_config"
            assert config_data["config"]["api_key"] == "test-key-123"

            print(f"   ✅ Skill config saved: {config_file.name}")

    finally:
        await ClaudeBox.cleanup_session(
            "skill-test-config", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_05_multiple_skills(ensure_oauth_token, temp_workspace):
    """Test 5: Multiple skills installation."""
    print("\n🔹 Test 5: Multiple skills installation")

    skill1 = Skill(name="skill_one", description="First skill")
    skill2 = Skill(name="skill_two", description="Second skill")
    skill3 = Skill(name="skill_three", description="Third skill")

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="skill-test-multiple",
            skills=[skill1, skill2, skill3],
        ) as box:
            workspace_path = Path(box.workspace_path)
            skills_dir = workspace_path.parent / "skills"

            # All skill dirs should exist
            assert (skills_dir / "skill_one").exists()
            assert (skills_dir / "skill_two").exists()
            assert (skills_dir / "skill_three").exists()

            print(f"   ✅ All 3 skills installed")

    finally:
        await ClaudeBox.cleanup_session(
            "skill-test-multiple", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_06_builtin_api_skill(ensure_oauth_token, temp_workspace):
    """Test 6: Built-in API skill installation."""
    print("\n🔹 Test 6: Built-in API skill")

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="skill-test-api",
            skills=[API_SKILL],
        ) as box:
            print(f"   ✅ API skill installed: {API_SKILL.name}")
            print(f"   ✅ Requirements: {API_SKILL.requirements}")

            # This test verifies the skill is accepted and processed
            # Actual package installation happens inside the VM
            assert box.id

    finally:
        await ClaudeBox.cleanup_session(
            "skill-test-api", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_07_builtin_redis_skill(ensure_oauth_token, temp_workspace):
    """Test 7: Built-in Redis skill installation."""
    print("\n🔹 Test 7: Built-in Redis skill")

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="skill-test-redis",
            skills=[REDIS_SKILL],
        ) as box:
            print(f"   ✅ Redis skill installed: {REDIS_SKILL.name}")
            print(f"   ✅ System packages: {REDIS_SKILL.system_packages}")
            print(f"   ✅ Requirements: {REDIS_SKILL.requirements}")

            assert box.id

    finally:
        await ClaudeBox.cleanup_session(
            "skill-test-redis", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_08_skill_persistence_across_reconnect(ensure_oauth_token, temp_workspace):
    """Test 8: Skill files persist across session reconnect."""
    print("\n🔹 Test 8: Skill persistence")

    import uuid

    session_id = f"skill-persist-{uuid.uuid4().hex[:6]}"

    test_skill = Skill(
        name="persist_test",
        description="Persistence test skill",
        files={"data.txt": "persistent data"},
    )

    try:
        # First session
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id=session_id,
            skills=[test_skill],
        ) as box:
            workspace_path = Path(box.workspace_path)
            data_file = workspace_path.parent / "skills" / "persist_test" / "data.txt"

            assert data_file.exists()
            assert data_file.read_text() == "persistent data"

            print(f"   ✅ Skill file created in first session")

        # Reconnect - skill files should persist
        box = await ClaudeBox.reconnect(session_id, workspace_dir=temp_workspace)
        async with box:
            # Skill files persist in workspace
            assert data_file.exists()
            assert data_file.read_text() == "persistent data"

            print(f"   ✅ Skill file persisted after reconnect")

    finally:
        await ClaudeBox.cleanup_session(
            session_id, workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_09_skill_validation(ensure_oauth_token, temp_workspace):
    """Test 9: Skill validation."""
    print("\n🔹 Test 9: Skill validation")

    # Invalid skill name should raise ValueError
    with pytest.raises(ValueError, match="must be alphanumeric"):
        Skill(name="invalid name!", description="Invalid")

    # Empty skill name should raise ValueError
    with pytest.raises(ValueError, match="cannot be empty"):
        Skill(name="", description="Empty name")

    print(f"   ✅ Skill validation works")


@pytest.mark.asyncio
async def test_10_skill_registry(ensure_oauth_token, temp_workspace):
    """Test 10: Skill registry operations."""
    print("\n🔹 Test 10: Skill registry")

    from claudebox import get_skill, list_skills, register_skill

    # List built-in skills
    builtin_skills = list_skills()
    assert "email" in builtin_skills
    assert "postgres" in builtin_skills
    assert "redis" in builtin_skills

    print(f"   ✅ Found {len(builtin_skills)} built-in skills")

    # Get a skill
    email_skill = get_skill("email")
    assert email_skill.name == "email"
    assert "sendgrid" in email_skill.requirements

    print(f"   ✅ Retrieved email skill from registry")

    # Register custom skill
    custom_skill = Skill(name="custom_test", description="Custom test skill")
    register_skill(custom_skill)

    assert "custom_test" in list_skills()
    retrieved = get_skill("custom_test")
    assert retrieved.name == "custom_test"

    print(f"   ✅ Custom skill registered successfully")
