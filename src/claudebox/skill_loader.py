"""Skill loading and installation for ClaudeBox."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from claudebox.exceptions import SkillInstallationError
from claudebox.skills import Skill

if TYPE_CHECKING:
    from boxlite import Box

    from claudebox.workspace import SessionWorkspace


class SkillLoader:
    """Load and install skills into a BoxLite VM."""

    def __init__(self, box: Box, workspace: SessionWorkspace):
        """
        Initialize skill loader.

        Args:
            box: BoxLite Box instance
            workspace: Session workspace for file storage
        """
        self._box = box
        self._workspace = workspace
        self._installed_skills: list[str] = []

    async def install_skill(self, skill: Skill):
        """
        Install a single skill into the VM.

        Args:
            skill: Skill to install

        Raises:
            SkillInstallationError: If installation fails
        """
        print(f"Installing skill: {skill.name}")

        try:
            # 1. Install system packages
            if skill.system_packages:
                await self._install_system_packages(skill.system_packages, skill.name)

            # 2. Install Python packages
            if skill.install_cmd:
                await self._run_install_cmd(skill.install_cmd, skill.name)

            # 3. Create skill directory and inject files
            await self._inject_files(skill.files, skill.name)

            # 4. Write skill config
            if skill.config:
                self._write_skill_config(skill)

            # 5. Set environment variables (if supported)
            if skill.env_vars:
                # Note: env vars should be set at box creation time
                # This is for documentation/config purposes
                print(
                    f"  Note: Skill {skill.name} requires env vars: {list(skill.env_vars.keys())}"
                )

            self._installed_skills.append(skill.name)
            print(f"✓ Skill {skill.name} installed successfully")

        except Exception as e:
            raise SkillInstallationError(skill.name, str(e)) from e

    async def load_skills(self, skills: list[Skill]):
        """
        Load multiple skills.

        Args:
            skills: List of skills to install
        """
        for skill in skills:
            await self.install_skill(skill)

    async def _install_system_packages(self, packages: list[str], skill_name: str):
        """Install system packages via apt."""
        packages_str = " ".join(packages)
        cmd = f"apt-get update && apt-get install -y {packages_str}"

        print(f"  Installing system packages for {skill_name}: {packages}")

        # Execute in VM
        execution = await self._box.exec("/bin/sh", ["-c", cmd], None)

        # Wait for completion
        result = await execution.wait()

        if result.exit_code != 0:
            raise SkillInstallationError(
                skill_name, f"System package installation failed with exit code {result.exit_code}"
            )

    async def _run_install_cmd(self, install_cmd: str, skill_name: str):
        """Run skill installation command."""
        print(f"  Running install command for {skill_name}")

        # Execute in VM
        execution = await self._box.exec("/bin/sh", ["-c", install_cmd], None)

        # Wait for completion
        result = await execution.wait()

        if result.exit_code != 0:
            raise SkillInstallationError(
                skill_name, f"Install command failed with exit code {result.exit_code}"
            )

    async def _inject_files(self, files: dict[str, str], skill_name: str):
        """Inject skill files into workspace."""
        skills_dir = Path(self._workspace.skills_dir)
        skill_dir = skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        if files:
            print(f"  Injecting files for {skill_name}")
            for filename, content in files.items():
                file_path = skill_dir / filename
                file_path.write_text(content)
                print(f"    - {filename}")

    def _write_skill_config(self, skill: Skill):
        """Write skill configuration to metadata directory."""
        config_file = (
            Path(self._workspace.metadata_dir) / f"skill_{skill.name}_config.json"
        )

        config_data = {
            "name": skill.name,
            "description": skill.description,
            "config": skill.config,
            "env_vars": skill.env_vars,
        }

        config_file.write_text(json.dumps(config_data, indent=2))

    def get_installed_skills(self) -> list[str]:
        """Get list of installed skill names."""
        return self._installed_skills.copy()
