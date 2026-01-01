"""Sandbox templates for specialized ClaudeBox environments."""

from __future__ import annotations

from enum import Enum


class SandboxTemplate(str, Enum):
    """Pre-configured sandbox templates for different use cases."""

    DEFAULT = "ghcr.io/boxlite-labs/claudebox-runtime:latest"
    WEB_DEV = "ghcr.io/boxlite-labs/claudebox-runtime:web-dev"
    DATA_SCIENCE = "ghcr.io/boxlite-labs/claudebox-runtime:data-science"
    SECURITY = "ghcr.io/boxlite-labs/claudebox-runtime:security"
    DEVOPS = "ghcr.io/boxlite-labs/claudebox-runtime:devops"
    MOBILE = "ghcr.io/boxlite-labs/claudebox-runtime:mobile"

    def __str__(self) -> str:
        return self.value


# Template descriptions
TEMPLATE_DESCRIPTIONS = {
    SandboxTemplate.DEFAULT: "Base runtime with Claude Code CLI",
    SandboxTemplate.WEB_DEV: "Web development: Node.js, TypeScript, Docker, PostgreSQL, Redis",
    SandboxTemplate.DATA_SCIENCE: "Data science: Jupyter, pandas, numpy, scikit-learn, matplotlib",
    SandboxTemplate.SECURITY: "Security research: nmap, wireshark, tcpdump (authorized use only)",
    SandboxTemplate.DEVOPS: "DevOps: Docker, Kubernetes, Terraform, Ansible",
    SandboxTemplate.MOBILE: "Mobile development: Android SDK, iOS tools",
}


def get_template_image(template: SandboxTemplate | str) -> str:
    """
    Get Docker image for a template.

    Args:
        template: SandboxTemplate enum or string

    Returns:
        Docker image URL
    """
    if isinstance(template, str):
        # Allow custom image URLs
        if template.startswith("ghcr.io/") or template.startswith("docker.io/"):
            return template
        # Try to match to enum
        try:
            template = SandboxTemplate(template)
        except ValueError:
            # Return as-is if not a valid template
            return template

    return str(template)


def list_templates() -> dict[str, str]:
    """
    List all available templates.

    Returns:
        Dictionary mapping template names to descriptions
    """
    return {
        template.name: TEMPLATE_DESCRIPTIONS[template] for template in SandboxTemplate
    }


def get_template_description(template: SandboxTemplate) -> str:
    """
    Get description for a template.

    Args:
        template: SandboxTemplate enum

    Returns:
        Template description
    """
    return TEMPLATE_DESCRIPTIONS.get(template, "Custom template")
