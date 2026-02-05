"""
Security policy examples.

This demonstrates:
- Pre-defined security policies
- Custom security policies
- Policy enforcement
- Network and filesystem restrictions
"""

import asyncio
import logging

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


async def example_unrestricted_policy():
    """Example 1: Unrestricted policy (default)."""
    print("\n=== Example 1: Unrestricted Policy ===")

    async with ClaudeBox(
        session_id="unrestricted", security_policy=UNRESTRICTED_POLICY
    ) as box:
        print(f"Policy: UNRESTRICTED")
        print(f"  Network: {UNRESTRICTED_POLICY.network_access}")
        print(f"  Filesystem: {UNRESTRICTED_POLICY.file_system}")
        print(f"  Allow sudo: {UNRESTRICTED_POLICY.allow_sudo}")

        result = await box.code("List files in /tmp")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("unrestricted", remove_workspace=True)


async def example_standard_policy():
    """Example 2: Standard policy (recommended)."""
    print("\n=== Example 2: Standard Policy ===")

    async with ClaudeBox(
        session_id="standard", security_policy=STANDARD_POLICY
    ) as box:
        print(f"Policy: STANDARD")
        print(f"  Network: {STANDARD_POLICY.network_access}")
        print(f"  Filesystem: {STANDARD_POLICY.file_system}")
        print(f"  Blocked commands: {STANDARD_POLICY.blocked_commands[:3]}...")

        result = await box.code("Create a file in the workspace")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("standard", remove_workspace=True)


async def example_restricted_policy():
    """Example 3: Restricted policy (high security)."""
    print("\n=== Example 3: Restricted Policy ===")

    async with ClaudeBox(
        session_id="restricted", security_policy=RESTRICTED_POLICY
    ) as box:
        print(f"Policy: RESTRICTED")
        print(f"  Network: {RESTRICTED_POLICY.network_access}")
        print(f"  Filesystem: {RESTRICTED_POLICY.file_system}")
        print(f"  Blocked domains: {RESTRICTED_POLICY.blocked_domains}")

        result = await box.code("Create files in workspace only")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("restricted", remove_workspace=True)


async def example_readonly_policy():
    """Example 4: Read-only policy."""
    print("\n=== Example 4: Read-Only Policy ===")

    print(f"Policy: READONLY")
    print(f"  Network: {READONLY_POLICY.network_access}")
    print(f"  Filesystem: {READONLY_POLICY.file_system}")
    print(f"  All writes blocked: True")

    # Read-only mode blocks all modifications
    # Useful for analysis/inspection tasks


async def example_research_policy():
    """Example 5: Research policy (balanced)."""
    print("\n=== Example 5: Research Policy ===")

    async with ClaudeBox(
        session_id="research", security_policy=RESEARCH_POLICY
    ) as box:
        print(f"Policy: RESEARCH")
        print(f"  Network: {RESEARCH_POLICY.network_access}")
        print(f"  Max disk: {RESEARCH_POLICY.max_disk_usage_gb} GB")
        print(f"  Max memory: {RESEARCH_POLICY.max_memory_mb} MB")
        print(f"  Allowed domains: {RESEARCH_POLICY.allowed_domains[:2]}...")

        result = await box.code("Download a dataset from GitHub")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("research", remove_workspace=True)


async def example_custom_policy():
    """Example 6: Custom security policy."""
    print("\n=== Example 6: Custom Security Policy ===")

    custom_policy = SecurityPolicy(
        network_access="restricted",
        file_system="workspace_only",
        allowed_domains=["*.github.com", "*.npmjs.com"],
        blocked_commands=["rm -rf", "sudo", "curl"],
        max_disk_usage_gb=5,
        max_memory_mb=2048,
        allow_sudo=False,
    )

    async with ClaudeBox(
        session_id="custom-policy", security_policy=custom_policy
    ) as box:
        print(f"Custom policy configured:")
        print(f"  Network: {custom_policy.network_access}")
        print(f"  Allowed domains: {custom_policy.allowed_domains}")
        print(f"  Max disk: {custom_policy.max_disk_usage_gb} GB")

        result = await box.code("Install packages from npm")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("custom-policy", remove_workspace=True)


async def example_policy_enforcement_commands():
    """Example 7: Command policy enforcement."""
    print("\n=== Example 7: Command Enforcement ===")

    policy = SecurityPolicy(
        blocked_commands=["rm -rf", "sudo", "dd"],
    )

    enforcer = SecurityPolicyEnforcer(policy)

    # Test various commands
    commands = [
        "echo hello",
        "sudo apt install",
        "rm -rf /tmp",
        "ls -la",
        "dd if=/dev/zero",
    ]

    print("Command enforcement results:")
    for cmd in commands:
        allowed, reason = enforcer.check_command(cmd)
        status = "✓ ALLOWED" if allowed else "✗ BLOCKED"
        print(f"  {status}: {cmd}")
        if reason:
            print(f"    Reason: {reason}")


async def example_policy_enforcement_network():
    """Example 8: Network policy enforcement."""
    print("\n=== Example 8: Network Enforcement ===")

    policy = SecurityPolicy(
        network_access="restricted",
        allowed_domains=["*.github.com", "*.pypi.org"],
        blocked_domains=["*.internal", "localhost"],
    )

    enforcer = SecurityPolicyEnforcer(policy)

    # Test various hosts
    hosts = [
        "api.github.com",
        "pypi.org",
        "secret.internal",
        "localhost",
        "example.com",
    ]

    print("Network access enforcement:")
    for host in hosts:
        allowed, reason = enforcer.check_network_access(host)
        status = "✓ ALLOWED" if allowed else "✗ BLOCKED"
        print(f"  {status}: {host}")
        if reason:
            print(f"    Reason: {reason}")


async def example_policy_enforcement_filesystem():
    """Example 9: Filesystem policy enforcement."""
    print("\n=== Example 9: Filesystem Enforcement ===")

    policy = SecurityPolicy(
        file_system="workspace_only",
        blocked_paths=["/etc/", "/var/", "/sys/"],
    )

    enforcer = SecurityPolicyEnforcer(policy)

    # Test various paths
    paths = [
        ("/config/workspace/file.txt", False),  # read
        ("/config/workspace/data.txt", True),   # write
        ("/etc/passwd", False),                 # read
        ("/tmp/test.txt", True),                # write
    ]

    print("Filesystem access enforcement:")
    for path, is_write in paths:
        allowed, reason = enforcer.check_file_access(path, write=is_write)
        status = "✓ ALLOWED" if allowed else "✗ BLOCKED"
        operation = "WRITE" if is_write else "READ"
        print(f"  {status}: {operation} {path}")
        if reason:
            print(f"    Reason: {reason}")


async def example_network_isolation():
    """Example 10: Network isolation policy."""
    print("\n=== Example 10: Network Isolation ===")

    no_network_policy = SecurityPolicy(
        network_access="none",
        file_system="workspace_only",
    )

    async with ClaudeBox(
        session_id="no-network", security_policy=no_network_policy
    ) as box:
        print(f"Network isolation policy:")
        print(f"  Network: {no_network_policy.network_access}")
        print(f"  All network access blocked")

        result = await box.code("Work with local files only")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("no-network", remove_workspace=True)


async def example_resource_limits():
    """Example 11: Resource limit policy."""
    print("\n=== Example 11: Resource Limits ===")

    limited_policy = SecurityPolicy(
        max_disk_usage_gb=2,
        max_memory_mb=1024,
        max_cpu_percent=50,
        max_execution_time_s=300,
    )

    print(f"Resource limits:")
    print(f"  Max disk: {limited_policy.max_disk_usage_gb} GB")
    print(f"  Max memory: {limited_policy.max_memory_mb} MB")
    print(f"  Max CPU: {limited_policy.max_cpu_percent}%")
    print(f"  Max time: {limited_policy.max_execution_time_s}s")


async def example_command_whitelist():
    """Example 12: Command whitelist policy."""
    print("\n=== Example 12: Command Whitelist ===")

    whitelist_policy = SecurityPolicy(
        allowed_commands=["python", "pip", "git", "npm"],
    )

    enforcer = SecurityPolicyEnforcer(whitelist_policy)

    commands = ["python script.py", "git clone", "rm file.txt", "sudo apt"]

    print("Whitelist enforcement (only allowed commands):")
    for cmd in commands:
        allowed, reason = enforcer.check_command(cmd)
        status = "✓ ALLOWED" if allowed else "✗ BLOCKED"
        print(f"  {status}: {cmd}")


async def example_policy_serialization():
    """Example 13: Policy serialization."""
    print("\n=== Example 13: Policy Serialization ===")

    policy = SecurityPolicy(
        network_access="restricted",
        file_system="workspace_only",
        max_disk_usage_gb=5,
    )

    # Convert to dictionary
    policy_dict = policy.to_dict()

    print("Policy as dictionary:")
    for key, value in list(policy_dict.items())[:5]:
        print(f"  {key}: {value}")


async def example_domain_wildcards():
    """Example 14: Domain wildcard matching."""
    print("\n=== Example 14: Domain Wildcards ===")

    policy = SecurityPolicy(
        network_access="restricted",
        allowed_domains=["*.github.com", "*.npmjs.com"],
    )

    enforcer = SecurityPolicyEnforcer(policy)

    domains = [
        "api.github.com",       # Matches *.github.com
        "github.com",           # Matches *.github.com
        "registry.npmjs.com",   # Matches *.npmjs.com
        "example.com",          # No match
    ]

    print("Wildcard domain matching:")
    for domain in domains:
        matches = enforcer._match_domain(domain, "*.github.com")
        if matches:
            print(f"  ✓ {domain} matches *.github.com")


async def example_layered_security():
    """Example 15: Layered security approach."""
    print("\n=== Example 15: Layered Security ===")

    # Combine multiple security layers
    secure_policy = SecurityPolicy(
        # Layer 1: Network restriction
        network_access="restricted",
        allowed_domains=["*.github.com", "*.pypi.org"],

        # Layer 2: Filesystem isolation
        file_system="workspace_only",

        # Layer 3: Command blocking
        blocked_commands=["sudo", "rm -rf", "dd", "mkfs"],

        # Layer 4: Resource limits
        max_disk_usage_gb=10,
        max_memory_mb=4096,

        # Layer 5: Privilege restriction
        allow_sudo=False,
        allow_root=False,
    )

    async with ClaudeBox(
        session_id="layered", security_policy=secure_policy
    ) as box:
        print(f"Layered security policy:")
        print(f"  ✓ Network restricted")
        print(f"  ✓ Filesystem isolated")
        print(f"  ✓ Commands blocked")
        print(f"  ✓ Resources limited")
        print(f"  ✓ Privileges restricted")

        result = await box.code("Safe operations within policy")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("layered", remove_workspace=True)


async def main():
    """Run all examples."""
    await example_unrestricted_policy()
    await example_standard_policy()
    await example_restricted_policy()
    await example_readonly_policy()
    await example_research_policy()
    await example_custom_policy()
    await example_policy_enforcement_commands()
    await example_policy_enforcement_network()
    await example_policy_enforcement_filesystem()
    await example_network_isolation()
    await example_resource_limits()
    await example_command_whitelist()
    await example_policy_serialization()
    await example_domain_wildcards()
    await example_layered_security()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
    asyncio.run(main())
