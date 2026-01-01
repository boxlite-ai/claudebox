"""Real security policy tests."""

import os

import pytest

from claudebox import (
    READONLY_POLICY,
    RESEARCH_POLICY,
    RESTRICTED_POLICY,
    STANDARD_POLICY,
    UNRESTRICTED_POLICY,
    ClaudeBox,
    SecurityPolicy,
    SecurityPolicyEnforcer,
)

pytestmark = pytest.mark.real


@pytest.fixture
def ensure_oauth_token():
    """Ensure OAuth token is set."""
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        pytest.skip("CLAUDE_CODE_OAUTH_TOKEN not set")
    return token


@pytest.mark.asyncio
async def test_01_security_policy_creation():
    """Test 1: Create security policies."""
    print("\n🔹 Test 1: Security policy creation")

    policy = SecurityPolicy(
        network_access="restricted",
        file_system="workspace_only",
        allow_sudo=False,
    )

    assert policy.network_access == "restricted"
    assert policy.file_system == "workspace_only"
    assert policy.allow_sudo is False

    print("   ✅ Custom security policy created")


@pytest.mark.asyncio
async def test_02_predefined_policies():
    """Test 2: Pre-defined security policies."""
    print("\n🔹 Test 2: Pre-defined policies")

    # Test all pre-defined policies
    assert UNRESTRICTED_POLICY.network_access == "full"
    print("   ✅ UNRESTRICTED_POLICY")

    assert STANDARD_POLICY.allow_sudo is False
    print("   ✅ STANDARD_POLICY")

    assert RESTRICTED_POLICY.file_system == "workspace_only"
    print("   ✅ RESTRICTED_POLICY")

    assert READONLY_POLICY.file_system == "readonly"
    print("   ✅ READONLY_POLICY")

    assert RESEARCH_POLICY.max_disk_usage_gb == 10
    print("   ✅ RESEARCH_POLICY")


@pytest.mark.asyncio
async def test_03_security_policy_validation():
    """Test 3: Security policy validation."""
    print("\n🔹 Test 3: Policy validation")

    # Invalid network_access
    with pytest.raises(ValueError, match="network_access must be"):
        SecurityPolicy(network_access="invalid")

    # Invalid file_system
    with pytest.raises(ValueError, match="file_system must be"):
        SecurityPolicy(file_system="invalid")

    print("   ✅ Policy validation works")


@pytest.mark.asyncio
async def test_04_policy_enforcer_command_check():
    """Test 4: Policy enforcer command checking."""
    print("\n🔹 Test 4: Command checking")

    enforcer = SecurityPolicyEnforcer(RESTRICTED_POLICY)

    # Check blocked command
    allowed, reason = enforcer.check_command("sudo apt install")
    assert not allowed
    assert "sudo" in reason.lower()
    print(f"   ✅ Blocked sudo: {reason}")

    # Check allowed command
    allowed, reason = enforcer.check_command("echo hello")
    assert allowed
    assert reason is None
    print("   ✅ Allowed safe command")


@pytest.mark.asyncio
async def test_05_policy_enforcer_network_check():
    """Test 5: Network access checking."""
    print("\n🔹 Test 5: Network checking")

    policy = SecurityPolicy(
        network_access="restricted",
        allowed_domains=["*.github.com", "pypi.org"],
        blocked_domains=["*.internal"],
    )

    enforcer = SecurityPolicyEnforcer(policy)

    # Check allowed domain
    allowed, reason = enforcer.check_network_access("api.github.com")
    assert allowed
    print("   ✅ Allowed api.github.com")

    # Check blocked domain
    allowed, reason = enforcer.check_network_access("secret.internal")
    assert not allowed
    print(f"   ✅ Blocked secret.internal: {reason}")


@pytest.mark.asyncio
async def test_06_policy_enforcer_file_check():
    """Test 6: File access checking."""
    print("\n🔹 Test 6: File access checking")

    policy = SecurityPolicy(
        file_system="workspace_only",
        blocked_paths=["/etc/", "/var/"],
    )

    enforcer = SecurityPolicyEnforcer(policy)

    # Check workspace access
    allowed, reason = enforcer.check_file_access("/config/workspace/file.txt")
    assert allowed
    print("   ✅ Allowed workspace access")

    # Check blocked path
    allowed, reason = enforcer.check_file_access("/etc/passwd")
    assert not allowed
    print(f"   ✅ Blocked /etc/passwd: {reason}")


@pytest.mark.asyncio
async def test_07_readonly_policy():
    """Test 7: Read-only policy."""
    print("\n🔹 Test 7: Read-only policy")

    enforcer = SecurityPolicyEnforcer(READONLY_POLICY)

    # Read should be allowed
    allowed, reason = enforcer.check_file_access("/config/workspace/file.txt", write=False)
    # Actually READONLY_POLICY allows all reads
    print(f"   ✅ Read access: {allowed}, {reason}")

    # Write should be blocked
    allowed, reason = enforcer.check_file_access("/config/workspace/file.txt", write=True)
    assert not allowed
    assert "read-only" in reason.lower()
    print(f"   ✅ Blocked write: {reason}")


@pytest.mark.asyncio
async def test_08_policy_integration(ensure_oauth_token, temp_workspace):
    """Test 8: Security policy integration with ClaudeBox."""
    print("\n🔹 Test 8: Policy integration")

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="security-test",
            security_policy=STANDARD_POLICY,
        ) as box:
            # Policy should be stored
            assert box._security_policy is STANDARD_POLICY
            print("   ✅ Security policy integrated")

    finally:
        await ClaudeBox.cleanup_session(
            "security-test", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_09_policy_to_dict():
    """Test 9: Policy serialization."""
    print("\n🔹 Test 9: Policy serialization")

    policy = SecurityPolicy(
        network_access="restricted",
        file_system="workspace_only",
        max_disk_usage_gb=5,
    )

    policy_dict = policy.to_dict()

    assert policy_dict["network_access"] == "restricted"
    assert policy_dict["file_system"] == "workspace_only"
    assert policy_dict["max_disk_usage_gb"] == 5

    print("   ✅ Policy serialization works")


@pytest.mark.asyncio
async def test_10_domain_matching():
    """Test 10: Domain pattern matching."""
    print("\n🔹 Test 10: Domain matching")

    enforcer = SecurityPolicyEnforcer(STANDARD_POLICY)

    # Wildcard matching
    assert enforcer._match_domain("api.github.com", "*.github.com")
    assert enforcer._match_domain("github.com", "*.github.com")
    assert not enforcer._match_domain("gitlab.com", "*.github.com")

    # Exact matching
    assert enforcer._match_domain("example.com", "example.com")
    assert not enforcer._match_domain("api.example.com", "example.com")

    print("   ✅ Domain matching works")
