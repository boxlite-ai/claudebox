"""ClaudeBox - Run Claude Code CLI in isolated micro-VMs."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from claudebox.results import CodeResult

if TYPE_CHECKING:
    from boxlite import Boxlite


class ClaudeBox:
    """
    Run Claude Code CLI in isolated micro-VMs.

    Example:
        >>> async with ClaudeBox() as box:
        ...     result = await box.code("Create a hello world script")
        ...     print(result.response)
    """

    DEFAULT_IMAGE = "ghcr.io/boxlite-labs/claudebox-runtime:latest"

    def __init__(
        self,
        oauth_token: str | None = None,
        api_key: str | None = None,
        image: str | None = None,
        cpus: int = 4,
        memory_mib: int = 4096,
        disk_size_gb: int = 8,
        runtime: Boxlite | None = None,
        volumes: list[tuple[str, str]] | None = None,
        ports: list[tuple[int, int]] | None = None,
        env: list[tuple[str, str]] | None = None,
        auto_remove: bool = True,
    ):
        from boxlite import Boxlite, BoxOptions

        env_list = list(env or [])

        # Auth: prefer OAuth token, fallback to API key
        self._oauth_token = oauth_token or os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if self._oauth_token:
            env_list.append(("CLAUDE_CODE_OAUTH_TOKEN", self._oauth_token))
        elif self._api_key:
            env_list.append(("ANTHROPIC_API_KEY", self._api_key))

        self._runtime = runtime or Boxlite.default()
        self._box = self._runtime.create(
            BoxOptions(
                image=image or self.DEFAULT_IMAGE,
                cpus=cpus,
                memory_mib=memory_mib,
                disk_size_gb=disk_size_gb,
                env=env_list,
                volumes=volumes or [],
                ports=ports or [],
                auto_remove=auto_remove,
            )
        )

    async def __aenter__(self) -> ClaudeBox:
        await self._box.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._box.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def id(self) -> str:
        return self._box.id

    async def code(
        self,
        prompt: str,
        max_turns: int | None = None,
        allowed_tools: list[str] | None = None,
        disallowed_tools: list[str] | None = None,
    ) -> CodeResult:
        """Run Claude Code CLI with a prompt."""
        args = ["-p", prompt, "--output-format", "json"]
        if max_turns is not None:
            args.extend(["--max-turns", str(max_turns)])
        if allowed_tools:
            for tool in allowed_tools:
                args.extend(["--allowedTools", tool])
        if disallowed_tools:
            for tool in disallowed_tools:
                args.extend(["--disallowedTools", tool])

        # Use script for TTY emulation (required for claude CLI)
        cmd = "claude " + " ".join(f'"{arg}"' for arg in args)
        result = await self._exec("/bin/sh", "-c", f"script -q -c '{cmd}' /dev/null")
        return CodeResult.from_exec(result.exit_code, result.stdout, result.stderr)

    async def _exec(self, cmd: str, *args: str):
        """Execute command in box."""
        execution = await self._box.exec(cmd, list(args) if args else None, None)

        stdout_lines = []
        if stdout := execution.stdout():
            async for line in stdout:
                stdout_lines.append(
                    line.decode("utf-8", errors="replace") if isinstance(line, bytes) else line
                )

        stderr_lines = []
        if stderr := execution.stderr():
            async for line in stderr:
                stderr_lines.append(
                    line.decode("utf-8", errors="replace") if isinstance(line, bytes) else line
                )

        exec_result = await execution.wait()

        class Result:
            def __init__(self, exit_code, stdout, stderr):
                self.exit_code = exit_code
                self.stdout = stdout
                self.stderr = stderr

        return Result(exec_result.exit_code, "".join(stdout_lines), "".join(stderr_lines))

    def __repr__(self) -> str:
        return f"ClaudeBox(id={self.id})"
