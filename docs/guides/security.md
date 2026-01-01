# Security Policies Guide

Control network access, filesystem permissions, and resource limits with fine-grained security policies.

---

## Overview

**Security policies** provide defense-in-depth protection for ClaudeBox sessions by controlling:

- **Network Access** - Full, restricted, or no network
- **Filesystem Access** - Full, workspace-only, or read-only
- **Command Restrictions** - Block dangerous commands
- **Resource Limits** - Cap disk, memory, CPU usage
- **Privilege Control** - Disable sudo/root access

Think of security policies as guardrails that prevent Claude Code from performing dangerous operations.

---

## Pre-defined Security Policies

ClaudeBox provides **5 pre-defined policies**:

| Policy | Network | Filesystem | Sudo | Use Case |
|--------|---------|------------|------|----------|
| `UNRESTRICTED_POLICY` | Full | Full | ✅ | Development, full control |
| `STANDARD_POLICY` | Full | Full | ❌ | General use, basic safety |
| `RESTRICTED_POLICY` | Restricted | Workspace only | ❌ | Sensitive data, limited access |
| `READONLY_POLICY` | None | Read-only | ❌ | Analysis only, no modifications |
| `RESEARCH_POLICY` | Restricted | Workspace only | ❌ | Research, curated domains |

---

## Policy Reference

### 1. UNRESTRICTED_POLICY

**Purpose:** Full access with minimal restrictions (development)

**Configuration:**
```python
UNRESTRICTED_POLICY = SecurityPolicy(
    network_access="full",       # Internet access
    file_system="full",          # All filesystem access
    allow_sudo=True,             # Sudo allowed
    allow_root=False,            # Root still blocked
)
```

**When to use:**
- Local development
- Trusted code only
- Need full system control

**Example:**
```python
from claudebox import ClaudeBox, UNRESTRICTED_POLICY

async def development():
    async with ClaudeBox(security_policy=UNRESTRICTED_POLICY) as box:
        await box.code("Install system packages with sudo")
```

---

### 2. STANDARD_POLICY (Default)

**Purpose:** Balanced security for general use

**Configuration:**
```python
STANDARD_POLICY = SecurityPolicy(
    network_access="full",
    file_system="full",
    allow_sudo=False,
    allow_root=False,
    blocked_commands=["rm -rf /", "dd if=/dev/zero", "mkfs", "fdisk"]
)
```

**Blocked commands:**
- `rm -rf /` - Prevent system-wide deletion
- `dd if=/dev/zero` - Prevent disk wiping
- `mkfs` - Prevent filesystem formatting
- `fdisk` - Prevent disk partitioning

**When to use:**
- Default for most tasks
- General development
- Untrusted code with basic safety

**Example:**
```python
from claudebox import ClaudeBox, STANDARD_POLICY

async def safe_development():
    async with ClaudeBox(security_policy=STANDARD_POLICY) as box:
        await box.code("Build web app")
```

---

### 3. RESTRICTED_POLICY

**Purpose:** Strict isolation for sensitive workloads

**Configuration:**
```python
RESTRICTED_POLICY = SecurityPolicy(
    network_access="restricted",      # Limited network
    file_system="workspace_only",     # Workspace only
    allow_sudo=False,
    allow_root=False,
    blocked_commands=[
        "rm -rf", "dd", "mkfs", "fdisk",
        "sudo", "su", "chmod 777"
    ],
    blocked_domains=["*.internal", "localhost", "127.0.0.1"]
)
```

**Restrictions:**
- Network: Can't access internal networks or localhost
- Filesystem: Only `/config/workspace/` accessible
- Commands: Blocks destructive and privilege escalation commands

**When to use:**
- Processing sensitive data
- Running untrusted code
- Production workloads
- Compliance requirements

**Example:**
```python
from claudebox import ClaudeBox, RESTRICTED_POLICY

async def process_sensitive_data():
    async with ClaudeBox(security_policy=RESTRICTED_POLICY) as box:
        await box.code("Process customer_data.csv (stays in workspace)")
```

---

### 4. READONLY_POLICY

**Purpose:** Analysis only, no modifications

**Configuration:**
```python
READONLY_POLICY = SecurityPolicy(
    network_access="none",
    file_system="readonly",
    allow_sudo=False,
    allow_root=False,
    blocked_commands=["*"]  # Block all write operations
)
```

**Restrictions:**
- Network: Completely disabled
- Filesystem: Read-only access
- Commands: All modification commands blocked

**When to use:**
- Code review and analysis
- Security audits
- Read-only data exploration
- Compliance reporting

**Example:**
```python
from claudebox import ClaudeBox, READONLY_POLICY

async def audit_code():
    async with ClaudeBox(security_policy=READONLY_POLICY) as box:
        await box.code("Analyze codebase for security vulnerabilities")
```

---

### 5. RESEARCH_POLICY

**Purpose:** Research with curated external access

**Configuration:**
```python
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
        "*.arxiv.org"
    ]
)
```

**Allowed domains:**
- GitHub (code repositories)
- PyPI (Python packages)
- npm (JavaScript packages)
- arXiv (research papers)

**Resource limits:**
- Disk: 10GB max
- Memory: 8GB max

**When to use:**
- Academic research
- ML experiments
- Package/dependency research
- Limited external access needed

**Example:**
```python
from claudebox import ClaudeBox, RESEARCH_POLICY

async def research_experiment():
    async with ClaudeBox(security_policy=RESEARCH_POLICY) as box:
        await box.code(
            "Download research dataset from arXiv, "
            "install analysis packages from PyPI"
        )
```

---

## Creating Custom Policies

### Basic Custom Policy

```python
from claudebox import SecurityPolicy, ClaudeBox

# Define custom policy
CUSTOM_POLICY = SecurityPolicy(
    network_access="restricted",
    file_system="workspace_only",
    allowed_domains=["*.api.mycompany.com"],
    blocked_commands=["rm", "dd"],
    max_disk_usage_gb=5,
    max_memory_mb=4096
)

async def main():
    async with ClaudeBox(security_policy=CUSTOM_POLICY) as box:
        await box.code("Call company API")
```

### Policy with Resource Limits

```python
RESOURCE_LIMITED_POLICY = SecurityPolicy(
    network_access="full",
    file_system="full",
    max_disk_usage_gb=5,        # 5GB disk limit
    max_memory_mb=2048,          # 2GB RAM limit
    max_cpu_percent=50,          # 50% CPU limit
    max_execution_time_s=3600    # 1 hour timeout
)
```

### Policy with Domain Whitelist

```python
API_ONLY_POLICY = SecurityPolicy(
    network_access="restricted",
    allowed_domains=[
        "api.openai.com",
        "*.anthropic.com",
        "*.github.com"
    ],
    blocked_commands=["sudo", "su"]
)
```

### Policy with Path Restrictions

```python
LIMITED_PATH_POLICY = SecurityPolicy(
    file_system="full",
    allowed_paths=[
        "/config/workspace/data",
        "/config/workspace/output"
    ],
    blocked_paths=[
        "/config/workspace/secrets"
    ]
)
```

---

## Security Policy Enforcement

### Command Checking

```python
from claudebox.security import SecurityPolicyEnforcer, RESTRICTED_POLICY

enforcer = SecurityPolicyEnforcer(RESTRICTED_POLICY)

# Check if command is allowed
allowed, reason = enforcer.check_command("rm -rf temp/")
if not allowed:
    print(f"Command blocked: {reason}")
```

### Network Access Checking

```python
# Check if domain access is allowed
allowed, reason = enforcer.check_network_access("malicious.com")
if not allowed:
    print(f"Network access blocked: {reason}")

# Check allowed domain
allowed, reason = enforcer.check_network_access("github.com")
assert allowed  # Should be allowed
```

### File Access Checking

```python
# Check file read access
allowed, reason = enforcer.check_file_access("/config/workspace/data.csv", write=False)

# Check file write access
allowed, reason = enforcer.check_file_access("/etc/passwd", write=True)
if not allowed:
    print(f"File write blocked: {reason}")
```

---

## Advanced Security Patterns

### Pattern 1: Layered Security (Template + Policy)

```python
from claudebox import ClaudeBox, SandboxTemplate, RESTRICTED_POLICY

async def layered_security():
    """Combine security template with strict policy."""
    async with ClaudeBox(
        template=SandboxTemplate.SECURITY,  # Security tools
        security_policy=RESTRICTED_POLICY    # Strict restrictions
    ) as box:
        await box.code("Authorized security scan of localhost")
```

### Pattern 2: Progressive Security Levels

```python
async def progressive_security(trust_level: str):
    """Adjust security based on trust level."""
    policies = {
        "untrusted": READONLY_POLICY,
        "low": RESTRICTED_POLICY,
        "medium": STANDARD_POLICY,
        "high": UNRESTRICTED_POLICY
    }

    policy = policies.get(trust_level, RESTRICTED_POLICY)

    async with ClaudeBox(security_policy=policy) as box:
        await box.code("Execute task with appropriate restrictions")
```

### Pattern 3: Environment-Specific Policies

```python
import os

async def environment_policy():
    """Use different policies for dev/staging/prod."""
    env = os.environ.get("ENV", "dev")

    if env == "production":
        policy = RESTRICTED_POLICY
    elif env == "staging":
        policy = STANDARD_POLICY
    else:
        policy = UNRESTRICTED_POLICY

    async with ClaudeBox(security_policy=policy) as box:
        await box.code("Deploy application")
```

### Pattern 4: Custom Policy Factory

```python
def create_api_policy(allowed_apis: list[str]) -> SecurityPolicy:
    """Create policy that allows specific API domains."""
    return SecurityPolicy(
        network_access="restricted",
        file_system="workspace_only",
        allowed_domains=[f"*.{api}" for api in allowed_apis],
        blocked_commands=["sudo", "su", "rm -rf"],
        max_memory_mb=4096
    )

# Usage
policy = create_api_policy(["github.com", "api.openai.com"])
async with ClaudeBox(security_policy=policy) as box:
    await box.code("Call allowed APIs")
```

---

## Security Best Practices

### 1. Default to Restrictive

```python
# ✅ Good: Start restrictive, loosen as needed
async with ClaudeBox(security_policy=RESTRICTED_POLICY) as box:
    ...

# ❌ Bad: Default to unrestricted
async with ClaudeBox(security_policy=UNRESTRICTED_POLICY) as box:
    ...
```

### 2. Use Allowlists Over Blocklists

```python
# ✅ Good: Allowlist (only these allowed)
policy = SecurityPolicy(
    allowed_domains=["github.com", "pypi.org"]
)

# ❌ Bad: Blocklist (everything except these)
policy = SecurityPolicy(
    blocked_domains=["malicious.com"]  # Too permissive
)
```

### 3. Combine Multiple Controls

```python
# ✅ Good: Defense in depth
MULTI_LAYER_POLICY = SecurityPolicy(
    network_access="restricted",       # Layer 1: Network
    file_system="workspace_only",      # Layer 2: Filesystem
    blocked_commands=["sudo"],         # Layer 3: Commands
    max_disk_usage_gb=5,               # Layer 4: Resources
    allowed_domains=["*.github.com"]   # Layer 5: Domain whitelist
)
```

### 4. Log Policy Violations

```python
from claudebox.security import SecurityPolicyEnforcer

async def logged_enforcement():
    enforcer = SecurityPolicyEnforcer(RESTRICTED_POLICY)

    command = "sudo rm -rf /"
    allowed, reason = enforcer.check_command(command)

    if not allowed:
        # Log violation
        print(f"SECURITY VIOLATION: Command '{command}' blocked: {reason}")
        # Could also write to audit log, send alert, etc.
```

### 5. Document Policy Rationale

```python
# ✅ Good: Documented policy
CUSTOMER_DATA_POLICY = SecurityPolicy(
    """
    Policy for processing customer data.

    Rationale:
    - workspace_only: Keep customer data isolated
    - No network: Prevent data exfiltration
    - Resource limits: Prevent DoS

    Compliance: GDPR Article 32 (Security of processing)
    """
    network_access="none",
    file_system="workspace_only",
    max_disk_usage_gb=10
)
```

---

## Domain Wildcard Patterns

```python
policy = SecurityPolicy(
    allowed_domains=[
        "github.com",          # Exact match
        "*.github.com",        # Subdomain wildcard
        "api.example.com",     # Specific subdomain
        "*.s3.amazonaws.com"   # AWS S3 buckets
    ]
)

# Matches:
# - github.com ✅
# - api.github.com ✅
# - raw.githubusercontent.com ❌ (different domain)

# - api.example.com ✅
# - example.com ❌ (not a wildcard match)

# - bucket.s3.amazonaws.com ✅
# - s3.amazonaws.com ✅ (wildcard also matches root)
```

---

## Policy Serialization

### Save Policy to JSON

```python
import json

policy = RESTRICTED_POLICY
policy_dict = policy.to_dict()

# Save to file
with open("policy.json", "w") as f:
    json.dump(policy_dict, f, indent=2)
```

### Load Policy from JSON

```python
import json

# Load from file
with open("policy.json", "r") as f:
    policy_dict = json.load(f)

# Create policy from dict
policy = SecurityPolicy(**policy_dict)
```

---

## Troubleshooting

### Issue: Command Blocked Unexpectedly

**Error:**
```
Command contains blocked pattern: sudo
```

**Solution:** Check blocked_commands list
```python
# Review policy
print(policy.blocked_commands)

# Create less restrictive policy
policy = SecurityPolicy(
    blocked_commands=[]  # Remove sudo block
)
```

### Issue: Network Access Denied

**Error:**
```
Domain not in allowed list
```

**Solution:** Add domain to allowlist
```python
policy = SecurityPolicy(
    network_access="restricted",
    allowed_domains=[
        "*.github.com",
        "needed-domain.com"  # Add this
    ]
)
```

### Issue: Filesystem Access Denied

**Error:**
```
Only workspace access allowed
```

**Solution:** Change filesystem policy
```python
# Option 1: Allow full access
policy = SecurityPolicy(file_system="full")

# Option 2: Add to allowed paths
policy = SecurityPolicy(
    file_system="workspace_only",
    allowed_paths=["/config/workspace", "/tmp"]
)
```

---

## Security Threat Model

### What Security Policies Protect Against

✅ **Protects against:**
- Accidental destructive commands (`rm -rf /`)
- Data exfiltration (network restrictions)
- Resource exhaustion (disk/memory/CPU limits)
- Privilege escalation (sudo/su blocking)
- Unauthorized network access (domain filtering)

⚠️ **Does NOT protect against:**
- Vulnerabilities in Claude Code itself
- Malicious code within allowed commands
- Sophisticated evasion techniques
- Zero-day exploits in dependencies

**Defense in depth:** Always use multiple security layers (hardware isolation + policies + monitoring).

---

## Next Steps

- **[Sessions Guide](sessions.md)** - Manage isolated sessions
- **[Workspace Guide](workspace.md)** - Understand filesystem structure
- **[Examples](../../examples/05_security.py)** - 15 security examples

---

**Secure ClaudeBox, protect your systems!**
