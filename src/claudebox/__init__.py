"""
ClaudeBox - Run Claude Code CLI in isolated micro-VMs.

Example:
    >>> from claudebox import ClaudeBox
    >>>
    >>> async with ClaudeBox() as box:
    ...     result = await box.code("Create a hello world Python script")
    ...     print(result.response)
"""

from claudebox.box import ClaudeBox
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
from claudebox.logging import ActionLogger
from claudebox.results import ActionLog, CodeResult, ResourceMetrics, SessionMetadata
from claudebox.rewards import (
    BuiltinRewards,
    CodeQualityReward,
    CustomReward,
    EfficiencyReward,
    RewardFunction,
    SafetyReward,
    SuccessOnlyReward,
    combine_rewards,
)
from claudebox.security import (
    READONLY_POLICY,
    RESEARCH_POLICY,
    RESTRICTED_POLICY,
    STANDARD_POLICY,
    UNRESTRICTED_POLICY,
    SecurityPolicy,
    SecurityPolicyEnforcer,
)
from claudebox.session import SessionManager
from claudebox.trajectory import TrajectoryExporter
from claudebox.skills import (
    API_SKILL,
    AWS_SKILL,
    DATA_SCIENCE_SKILL,
    DOCKER_SKILL,
    EMAIL_SKILL,
    MYSQL_SKILL,
    POSTGRES_SKILL,
    REDIS_SKILL,
    SCRAPING_SKILL,
    Skill,
    SkillRegistry,
    get_skill,
    list_skills,
    register_skill,
)
from claudebox.templates import (
    SandboxTemplate,
    get_template_description,
    get_template_image,
    list_templates,
)
from claudebox.workspace import SessionInfo, SessionWorkspace, WorkspaceManager

__version__ = "0.2.0"

__all__ = [
    # Core
    "ClaudeBox",
    "CodeResult",
    "__version__",
    # Results and metadata
    "ActionLog",
    "SessionMetadata",
    "ResourceMetrics",
    # Logging
    "ActionLogger",
    # Rewards (RL)
    "RewardFunction",
    "SuccessOnlyReward",
    "CodeQualityReward",
    "SafetyReward",
    "EfficiencyReward",
    "CustomReward",
    "BuiltinRewards",
    "combine_rewards",
    # Trajectory (RL)
    "TrajectoryExporter",
    # Security
    "SecurityPolicy",
    "SecurityPolicyEnforcer",
    "UNRESTRICTED_POLICY",
    "STANDARD_POLICY",
    "RESTRICTED_POLICY",
    "READONLY_POLICY",
    "RESEARCH_POLICY",
    # Skills
    "Skill",
    "SkillRegistry",
    "register_skill",
    "get_skill",
    "list_skills",
    # Built-in skills
    "EMAIL_SKILL",
    "POSTGRES_SKILL",
    "MYSQL_SKILL",
    "REDIS_SKILL",
    "API_SKILL",
    "AWS_SKILL",
    "DOCKER_SKILL",
    "SCRAPING_SKILL",
    "DATA_SCIENCE_SKILL",
    # Templates
    "SandboxTemplate",
    "get_template_image",
    "get_template_description",
    "list_templates",
    # Workspace management
    "WorkspaceManager",
    "SessionWorkspace",
    "SessionInfo",
    "SessionManager",
    # Exceptions
    "ClaudeBoxError",
    "SessionNotFoundError",
    "SessionAlreadyExistsError",
    "WorkspaceError",
    "SkillError",
    "SkillNotFoundError",
    "SkillInstallationError",
    "TemplateError",
    "LoggingError",
]
