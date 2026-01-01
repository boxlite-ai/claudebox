"""Real template system tests - actual BoxLite VMs with different templates."""

import os

import pytest

from claudebox import ClaudeBox, SandboxTemplate, get_template_description, list_templates

pytestmark = pytest.mark.real


@pytest.fixture
def ensure_oauth_token():
    """Ensure OAuth token is set."""
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        pytest.skip("CLAUDE_CODE_OAUTH_TOKEN not set")
    return token


@pytest.mark.asyncio
async def test_01_default_template(ensure_oauth_token, temp_workspace):
    """Test 1: Default template (no template specified)."""
    print("\n🔹 Test 1: Default template")

    async with ClaudeBox(
        oauth_token=ensure_oauth_token, workspace_dir=temp_workspace
    ) as box:
        # Default template should work
        assert box.id
        print(f"   ✅ Default template works: {box.id}")


@pytest.mark.asyncio
async def test_02_template_enum(ensure_oauth_token, temp_workspace):
    """Test 2: Template specified via SandboxTemplate enum."""
    print("\n🔹 Test 2: Template enum")

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="template-test-enum",
            template=SandboxTemplate.DEFAULT,
        ) as box:
            assert box.id
            print(f"   ✅ Template enum works: {SandboxTemplate.DEFAULT}")

    finally:
        await ClaudeBox.cleanup_session(
            "template-test-enum", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_03_template_string(ensure_oauth_token, temp_workspace):
    """Test 3: Template specified via string."""
    print("\n🔹 Test 3: Template string")

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="template-test-string",
            template="ghcr.io/boxlite-labs/claudebox-runtime:latest",
        ) as box:
            assert box.id
            print(f"   ✅ Template string works")

    finally:
        await ClaudeBox.cleanup_session(
            "template-test-string", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_04_explicit_image_overrides_template(ensure_oauth_token, temp_workspace):
    """Test 4: Explicit image parameter overrides template."""
    print("\n🔹 Test 4: Image overrides template")

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="template-test-override",
            template=SandboxTemplate.WEB_DEV,  # This should be ignored
            image="ghcr.io/boxlite-labs/claudebox-runtime:latest",  # This takes priority
        ) as box:
            assert box.id
            print(f"   ✅ Explicit image parameter takes priority")

    finally:
        await ClaudeBox.cleanup_session(
            "template-test-override", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_05_list_templates():
    """Test 5: List all available templates."""
    print("\n🔹 Test 5: List templates")

    templates = list_templates()

    assert "DEFAULT" in templates
    assert "WEB_DEV" in templates
    assert "DATA_SCIENCE" in templates
    assert "SECURITY" in templates

    print(f"   ✅ Found {len(templates)} templates:")
    for name, desc in templates.items():
        print(f"      - {name}: {desc}")


@pytest.mark.asyncio
async def test_06_get_template_description():
    """Test 6: Get template descriptions."""
    print("\n🔹 Test 6: Template descriptions")

    desc = get_template_description(SandboxTemplate.DATA_SCIENCE)
    assert "pandas" in desc or "Data science" in desc

    print(f"   ✅ DATA_SCIENCE: {desc}")

    desc = get_template_description(SandboxTemplate.WEB_DEV)
    assert "Web" in desc or "Node" in desc

    print(f"   ✅ WEB_DEV: {desc}")


@pytest.mark.asyncio
async def test_07_template_persistence(ensure_oauth_token, temp_workspace):
    """Test 7: Template choice persists across reconnection."""
    print("\n🔹 Test 7: Template persistence")

    import uuid

    session_id = f"template-persist-{uuid.uuid4().hex[:6]}"

    try:
        # Create session with template
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id=session_id,
            template=SandboxTemplate.DEFAULT,
        ) as box:
            print(f"   ✅ Created session with template")

        # Reconnect - should still work (reconnect creates new box with same workspace)
        box = await ClaudeBox.reconnect(session_id, workspace_dir=temp_workspace)
        async with box:
            assert box.id
            print(f"   ✅ Reconnection works after template session")

    finally:
        await ClaudeBox.cleanup_session(
            session_id, workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_08_custom_image_url(ensure_oauth_token, temp_workspace):
    """Test 8: Custom image URL."""
    print("\n🔹 Test 8: Custom image URL")

    try:
        # Use the default image as custom URL to ensure it works
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="template-custom-url",
            template="ghcr.io/boxlite-labs/claudebox-runtime:latest",
        ) as box:
            assert box.id
            print(f"   ✅ Custom image URL works")

    finally:
        await ClaudeBox.cleanup_session(
            "template-custom-url", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_09_template_enum_values():
    """Test 9: Template enum values."""
    print("\n🔹 Test 9: Template enum values")

    # All templates should have valid image URLs
    assert SandboxTemplate.DEFAULT.value.startswith("ghcr.io/")
    assert SandboxTemplate.WEB_DEV.value.startswith("ghcr.io/")
    assert SandboxTemplate.DATA_SCIENCE.value.startswith("ghcr.io/")

    print(f"   ✅ DEFAULT: {SandboxTemplate.DEFAULT.value}")
    print(f"   ✅ WEB_DEV: {SandboxTemplate.WEB_DEV.value}")
    print(f"   ✅ DATA_SCIENCE: {SandboxTemplate.DATA_SCIENCE.value}")
    print(f"   ✅ SECURITY: {SandboxTemplate.SECURITY.value}")


@pytest.mark.asyncio
async def test_10_template_str_conversion():
    """Test 10: Template string conversion."""
    print("\n🔹 Test 10: Template string conversion")

    template = SandboxTemplate.WEB_DEV
    template_str = str(template)

    assert template_str == template.value
    assert template_str.startswith("ghcr.io/")

    print(f"   ✅ str(SandboxTemplate.WEB_DEV) = {template_str}")
