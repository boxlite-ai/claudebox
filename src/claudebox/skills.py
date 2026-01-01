"""Skill and plugin system for ClaudeBox."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class Skill:
    """
    A skill that can be pre-loaded into a ClaudeBox session.

    Skills provide modular capabilities that extend Claude Code's functionality.
    They can install packages, inject files, and configure environment variables.

    Example:
        >>> email_skill = Skill(
        ...     name="email",
        ...     description="Send emails via SMTP",
        ...     install_cmd="pip install sendgrid",
        ...     config={"api_key": "your-key"},
        ...     env_vars={"SENDGRID_API_KEY": "your-key"}
        ... )
    """

    name: str
    description: str
    install_cmd: str | None = None
    config: dict = field(default_factory=dict)
    files: dict[str, str] = field(default_factory=dict)  # filename -> content
    requirements: list[str] = field(default_factory=list)  # Dependencies
    env_vars: dict[str, str] = field(default_factory=dict)  # Environment variables
    system_packages: list[str] = field(default_factory=list)  # apt packages

    def __post_init__(self):
        """Validate skill definition."""
        if not self.name:
            raise ValueError("Skill name cannot be empty")
        if not self.name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                f"Skill name '{self.name}' must be alphanumeric (with - or _)"
            )


class SkillRegistry:
    """Global registry for skills."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill):
        """
        Register a skill.

        Args:
            skill: Skill to register

        Raises:
            ValueError: If skill with same name already registered
        """
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' is already registered")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        """
        Get a skill by name.

        Args:
            name: Skill name

        Returns:
            Skill instance

        Raises:
            KeyError: If skill not found
        """
        if name not in self._skills:
            raise KeyError(f"Skill '{name}' not found in registry")
        return self._skills[name]

    def list_available(self) -> list[str]:
        """
        List all registered skill names.

        Returns:
            List of skill names
        """
        return list(self._skills.keys())

    def unregister(self, name: str):
        """
        Unregister a skill.

        Args:
            name: Skill name to remove
        """
        if name in self._skills:
            del self._skills[name]


# Global registry instance
_global_registry = SkillRegistry()


def register_skill(skill: Skill):
    """Register a skill in the global registry."""
    _global_registry.register(skill)


def get_skill(name: str) -> Skill:
    """Get a skill from the global registry."""
    return _global_registry.get(name)


def list_skills() -> list[str]:
    """List all registered skills."""
    return _global_registry.list_available()


# Built-in skills

# Email skill
EMAIL_SKILL = Skill(
    name="email",
    description="Send emails via SMTP using sendgrid",
    install_cmd="pip3 install sendgrid",
    requirements=["sendgrid"],
    config={
        "smtp_server": "smtp.sendgrid.net",
        "smtp_port": 587,
    },
)

# Database skill - PostgreSQL
POSTGRES_SKILL = Skill(
    name="postgres",
    description="Connect to PostgreSQL databases",
    install_cmd="pip3 install psycopg2-binary",
    system_packages=["postgresql-client"],
    requirements=["psycopg2-binary"],
)

# Database skill - MySQL
MYSQL_SKILL = Skill(
    name="mysql",
    description="Connect to MySQL databases",
    install_cmd="pip3 install mysql-connector-python",
    system_packages=["mysql-client"],
    requirements=["mysql-connector-python"],
)

# Redis skill
REDIS_SKILL = Skill(
    name="redis",
    description="Connect to Redis cache",
    install_cmd="pip3 install redis",
    system_packages=["redis-tools"],
    requirements=["redis"],
)

# HTTP API skill
API_SKILL = Skill(
    name="api",
    description="Make HTTP API requests with advanced features",
    install_cmd="pip3 install requests httpx",
    requirements=["requests", "httpx"],
)

# AWS skill
AWS_SKILL = Skill(
    name="aws",
    description="AWS SDK and CLI tools",
    install_cmd="pip3 install boto3 awscli",
    requirements=["boto3", "awscli"],
)

# Docker skill
DOCKER_SKILL = Skill(
    name="docker",
    description="Docker CLI and SDK",
    system_packages=["docker.io"],
    install_cmd="pip3 install docker",
    requirements=["docker"],
)

# Web scraping skill
SCRAPING_SKILL = Skill(
    name="scraping",
    description="Web scraping with BeautifulSoup and Selenium",
    install_cmd="pip3 install beautifulsoup4 selenium lxml",
    requirements=["beautifulsoup4", "selenium", "lxml"],
)

# Data science skill
DATA_SCIENCE_SKILL = Skill(
    name="data_science",
    description="Data analysis with pandas, numpy, matplotlib",
    install_cmd="pip3 install pandas numpy matplotlib seaborn scikit-learn",
    requirements=["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn"],
)

# Register built-in skills
register_skill(EMAIL_SKILL)
register_skill(POSTGRES_SKILL)
register_skill(MYSQL_SKILL)
register_skill(REDIS_SKILL)
register_skill(API_SKILL)
register_skill(AWS_SKILL)
register_skill(DOCKER_SKILL)
register_skill(SCRAPING_SKILL)
register_skill(DATA_SCIENCE_SKILL)
