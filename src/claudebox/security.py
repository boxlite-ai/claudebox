"""Security policies for ClaudeBox."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SecurityPolicy:
    """
    Security policy for ClaudeBox sandboxes.

    Controls network access, filesystem access, and resource limits.
    """

    # Network access
    network_access: str = "full"  # "full", "restricted", "none"
    allowed_domains: list[str] = field(default_factory=list)
    blocked_domains: list[str] = field(default_factory=list)

    # Filesystem access
    file_system: str = "full"  # "full", "workspace_only", "readonly"
    allowed_paths: list[str] = field(default_factory=list)
    blocked_paths: list[str] = field(default_factory=list)

    # Resource limits
    max_disk_usage_gb: int | None = None
    max_memory_mb: int | None = None
    max_cpu_percent: int | None = None
    max_execution_time_s: int | None = None

    # Command restrictions
    blocked_commands: list[str] = field(default_factory=list)
    allowed_commands: list[str] = field(default_factory=list)

    # Privilege restrictions
    allow_sudo: bool = False
    allow_root: bool = False

    def __post_init__(self):
        """Validate security policy."""
        valid_network = ["full", "restricted", "none"]
        if self.network_access not in valid_network:
            raise ValueError(f"network_access must be one of {valid_network}")

        valid_filesystem = ["full", "workspace_only", "readonly"]
        if self.file_system not in valid_filesystem:
            raise ValueError(f"file_system must be one of {valid_filesystem}")

    def to_dict(self) -> dict:
        """Convert policy to dictionary."""
        return {
            "network_access": self.network_access,
            "allowed_domains": self.allowed_domains,
            "blocked_domains": self.blocked_domains,
            "file_system": self.file_system,
            "allowed_paths": self.allowed_paths,
            "blocked_paths": self.blocked_paths,
            "max_disk_usage_gb": self.max_disk_usage_gb,
            "max_memory_mb": self.max_memory_mb,
            "max_cpu_percent": self.max_cpu_percent,
            "max_execution_time_s": self.max_execution_time_s,
            "blocked_commands": self.blocked_commands,
            "allowed_commands": self.allowed_commands,
            "allow_sudo": self.allow_sudo,
            "allow_root": self.allow_root,
        }


# Pre-defined security policies

UNRESTRICTED_POLICY = SecurityPolicy(
    network_access="full",
    file_system="full",
    allow_sudo=True,
    allow_root=False,
)

STANDARD_POLICY = SecurityPolicy(
    network_access="full",
    file_system="full",
    allow_sudo=False,
    allow_root=False,
    blocked_commands=["rm -rf /", "dd if=/dev/zero", "mkfs", "fdisk"],
)

RESTRICTED_POLICY = SecurityPolicy(
    network_access="restricted",
    file_system="workspace_only",
    allow_sudo=False,
    allow_root=False,
    blocked_commands=[
        "rm -rf",
        "dd",
        "mkfs",
        "fdisk",
        "sudo",
        "su",
        "chmod 777",
    ],
    blocked_domains=["*.internal", "localhost", "127.0.0.1"],
)

READONLY_POLICY = SecurityPolicy(
    network_access="none",
    file_system="readonly",
    allow_sudo=False,
    allow_root=False,
    blocked_commands=["*"],  # Block all commands that modify state
)

RESEARCH_POLICY = SecurityPolicy(
    network_access="restricted",
    file_system="workspace_only",
    allow_sudo=False,
    allow_root=False,
    max_disk_usage_gb=10,
    max_memory_mb=8192,
    blocked_commands=["sudo", "su"],
    allowed_domains=[
        "*.github.com",
        "*.pypi.org",
        "*.npmjs.com",
        "*.arxiv.org",
    ],
)


class SecurityPolicyEnforcer:
    """Enforce security policies on ClaudeBox actions."""

    def __init__(self, policy: SecurityPolicy):
        """
        Initialize policy enforcer.

        Args:
            policy: Security policy to enforce
        """
        self.policy = policy

    def check_command(self, command: str) -> tuple[bool, str | None]:
        """
        Check if a command is allowed by the policy.

        Args:
            command: Command to check

        Returns:
            (allowed, reason) tuple - reason is None if allowed
        """
        # Check sudo/su restrictions
        if not self.policy.allow_sudo and ("sudo " in command or "su " in command):
            return False, "sudo/su not allowed by security policy"

        # Check blocked commands
        for blocked in self.policy.blocked_commands:
            if blocked in command:
                return False, f"Command contains blocked pattern: {blocked}"

        # If allowed_commands is set, only allow those
        if self.policy.allowed_commands:
            allowed = False
            for pattern in self.policy.allowed_commands:
                if pattern in command:
                    allowed = True
                    break
            if not allowed:
                return False, "Command not in allowed list"

        return True, None

    def check_network_access(self, host: str) -> tuple[bool, str | None]:
        """
        Check if network access to a host is allowed.

        Args:
            host: Hostname or IP to check

        Returns:
            (allowed, reason) tuple
        """
        if self.policy.network_access == "none":
            return False, "Network access disabled by policy"

        # Check blocked domains
        for blocked in self.policy.blocked_domains:
            if self._match_domain(host, blocked):
                return False, f"Domain blocked: {blocked}"

        # If restricted and allowed_domains set, check whitelist
        if self.policy.network_access == "restricted" and self.policy.allowed_domains:
            allowed = False
            for pattern in self.policy.allowed_domains:
                if self._match_domain(host, pattern):
                    allowed = True
                    break
            if not allowed:
                return False, "Domain not in allowed list"

        return True, None

    def check_file_access(self, path: str, write: bool = False) -> tuple[bool, str | None]:
        """
        Check if file access is allowed.

        Args:
            path: File path to check
            write: Whether this is a write operation

        Returns:
            (allowed, reason) tuple
        """
        if self.policy.file_system == "readonly" and write:
            return False, "Filesystem is read-only"

        # Check blocked paths
        for blocked in self.policy.blocked_paths:
            if path.startswith(blocked):
                return False, f"Path blocked: {blocked}"

        # If workspace_only, check if in workspace
        if self.policy.file_system == "workspace_only":
            if not path.startswith("/config/workspace"):
                return False, "Only workspace access allowed"

        # Check allowed paths if set
        if self.policy.allowed_paths:
            allowed = False
            for pattern in self.policy.allowed_paths:
                if path.startswith(pattern):
                    allowed = True
                    break
            if not allowed:
                return False, "Path not in allowed list"

        return True, None

    @staticmethod
    def _match_domain(host: str, pattern: str) -> bool:
        """Match domain against pattern (supports wildcards)."""
        if pattern.startswith("*."):
            suffix = pattern[2:]
            return host.endswith(suffix) or host == suffix
        return host == pattern
