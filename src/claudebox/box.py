"""ClaudeBox - Run Claude Code CLI in isolated micro-VMs."""

from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING, Callable

from claudebox.results import CodeResult, SessionMetadata
from claudebox.session import SessionManager
from claudebox.workspace import SessionInfo, WorkspaceManager

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
        auto_remove: bool | None = None,
        # Phase 1: Workspace & session management
        session_id: str | None = None,
        workspace_dir: str | None = None,
        enable_logging: bool = True,
        # Phase 2: Skills & Templates
        skills: list | None = None,
        template: str | None = None,
        # Phase 3: RL Support & Security
        reward_fn: Callable[[CodeResult], float] | None = None,
        security_policy: object | None = None,
    ):
        from boxlite import Boxlite, BoxOptions

        # Initialize workspace manager
        self._workspace_manager = WorkspaceManager(workspace_dir)

        # Generate session ID if persistent mode
        if session_id:
            self._session_id = session_id
            self._is_persistent = True

            # Check if session already exists (reconnecting)
            if self._workspace_manager.session_exists(session_id):
                # Reconnecting to existing session
                self._session_workspace = self._workspace_manager.get_session_workspace(
                    session_id
                )
            else:
                # Creating new persistent session
                self._session_workspace = self._workspace_manager.create_session_workspace(
                    session_id
                )

            # Create session manager
            self._session_manager = SessionManager(self._session_workspace)
        else:
            # Ephemeral mode: generate temporary session ID
            self._session_id = f"ephemeral-{uuid.uuid4().hex[:8]}"
            self._is_persistent = False
            self._session_workspace = self._workspace_manager.create_session_workspace(
                self._session_id, force=True
            )
            self._session_manager = SessionManager(self._session_workspace)

        # Auto-detect auto_remove based on persistence
        if auto_remove is None:
            auto_remove = not self._is_persistent  # Remove ephemeral boxes, keep persistent ones

        self._auto_remove = auto_remove
        self._enable_logging = enable_logging
        self._skills = skills or []
        self._reward_fn = reward_fn
        self._security_policy = security_policy

        env_list = list(env or [])

        # Add skill environment variables
        for skill in self._skills:
            for key, value in skill.env_vars.items():
                env_list.append((key, value))

        # Auth: prefer OAuth token, fallback to API key
        self._oauth_token = oauth_token or os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if self._oauth_token:
            env_list.append(("CLAUDE_CODE_OAUTH_TOKEN", self._oauth_token))
        elif self._api_key:
            env_list.append(("ANTHROPIC_API_KEY", self._api_key))

        # Prepare volumes: add workspace mounts
        volumes_list = list(volumes or [])

        # Mount workspace directory
        volumes_list.append(
            (self._session_workspace.workspace_dir, "/config/workspace")
        )

        # Mount metadata directory
        volumes_list.append(
            (self._session_workspace.metadata_dir, "/config/.claudebox")
        )

        self._runtime = runtime or Boxlite.default()

        # Determine image from template or use explicit image
        final_image = image
        if not final_image and template:
            from claudebox.templates import get_template_image

            final_image = get_template_image(template)
        if not final_image:
            final_image = self.DEFAULT_IMAGE

        # Note: Not using named boxes for now due to BoxLite naming issues
        # Boxes are tracked by workspace path instead
        self._box = self._runtime.create(
            BoxOptions(
                image=final_image,
                cpus=cpus,
                memory_mib=memory_mib,
                disk_size_gb=disk_size_gb,
                env=env_list,
                volumes=volumes_list,
                ports=ports or [],
                auto_remove=auto_remove,
            ),
        )

        # Store session metadata (will be updated on first code() call)
        self._session_metadata: SessionMetadata | None = None

    async def __aenter__(self) -> ClaudeBox:
        await self._box.__aenter__()

        # Create or load session metadata
        if self._session_manager.session_exists():
            self._session_metadata = self._session_manager.load_session()
        else:
            self._session_metadata = self._session_manager.create_session(self._box.id)

        # Install skills if provided
        if self._skills:
            from claudebox.skill_loader import SkillLoader

            loader = SkillLoader(self._box, self._session_workspace)
            await loader.load_skills(self._skills)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Update session metadata before exit
        if self._session_metadata:
            self._session_manager.update_session(self._session_metadata)

        # Clean up ephemeral workspace
        if not self._is_persistent:
            self._workspace_manager.cleanup_session(
                self._session_id, remove_workspace=True
            )

        return await self._box.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def id(self) -> str:
        return self._box.id

    @property
    def session_id(self) -> str:
        """Get the session ID for this box."""
        return self._session_id

    @property
    def workspace_path(self) -> str:
        """Get the host path to the workspace directory."""
        return self._session_workspace.workspace_dir

    @property
    def is_persistent(self) -> bool:
        """Check if this is a persistent session."""
        return self._is_persistent

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

        # Execute claude command directly
        # Note: script command for TTY emulation has different syntax on macOS vs Linux
        cmd = "claude " + " ".join(f'"{arg}"' for arg in args)
        result = await self._exec("/bin/sh", "-c", cmd)
        code_result = CodeResult.from_exec(result.exit_code, result.stdout, result.stderr)

        # Calculate reward if reward function provided
        if self._reward_fn:
            code_result.reward = self._reward_fn(code_result)

        return code_result

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
        return f"ClaudeBox(id={self.id}, session_id={self.session_id})"

    # Enhanced observability methods (Phase 3 Week 7)

    async def get_metrics(self):
        """
        Get current resource usage metrics from BoxLite.

        Returns:
            ResourceMetrics instance with current metrics

        Note: BoxLite metrics integration depends on BoxLite API availability.
        """
        from claudebox.results import ResourceMetrics

        # Placeholder for BoxLite metrics integration
        # When BoxLite exposes metrics API, this will return real data
        return ResourceMetrics(
            cpu_percent=0.0,
            memory_mb=0,
            disk_mb=0,
            commands_executed=0,
            network_bytes_sent=0,
            network_bytes_received=0,
        )

    async def get_history_metrics(self) -> list:
        """
        Get metrics over time from session history.

        Returns:
            List of ResourceMetrics from action log
        """
        from claudebox.logging import ActionLogger

        logger = ActionLogger(self._session_workspace.history_file)
        logs = logger.get_logs()

        # Extract metrics from logs if available
        metrics = []
        for log in logs:
            if "metrics" in log.context:
                from claudebox.results import ResourceMetrics

                m = log.context["metrics"]
                metrics.append(
                    ResourceMetrics(
                        cpu_percent=m.get("cpu_percent", 0.0),
                        memory_mb=m.get("memory_mb", 0),
                        disk_mb=m.get("disk_mb", 0),
                        commands_executed=m.get("commands_executed", 0),
                        network_bytes_sent=m.get("network_bytes_sent", 0),
                        network_bytes_received=m.get("network_bytes_received", 0),
                    )
                )

        return metrics

    # Session management class methods (Phase 1)

    @classmethod
    async def reconnect(
        cls,
        session_id: str,
        runtime: Boxlite | None = None,
        workspace_dir: str | None = None,
    ) -> ClaudeBox:
        """
        Reconnect to an existing persistent session.

        Args:
            session_id: Session identifier from previous ClaudeBox instance
            runtime: Optional BoxLite runtime instance
            workspace_dir: Optional workspace directory (default: ~/.claudebox)

        Returns:
            ClaudeBox instance connected to existing session

        Raises:
            SessionNotFoundError: If session doesn't exist

        Example:
            # First session
            async with ClaudeBox(session_id="dev") as box:
                await box.code("npm install")

            # Later, reconnect
            async with ClaudeBox.reconnect("dev") as box:
                await box.code("npm test")
        """
        from claudebox.exceptions import SessionNotFoundError

        # Check if session exists
        workspace_manager = WorkspaceManager(workspace_dir)
        if not workspace_manager.session_exists(session_id):
            raise SessionNotFoundError(session_id)

        # Note: Not using named boxes, so we just create a new box
        # that reuses the existing session workspace
        # The workspace persistence is what matters, not the box itself
        return cls(
            session_id=session_id,
            workspace_dir=workspace_dir,
            runtime=runtime,
        )

    @classmethod
    def list_sessions(
        cls, runtime: Boxlite | None = None, workspace_dir: str | None = None
    ) -> list[SessionInfo]:
        """
        List all ClaudeBox sessions (both active and stopped).

        Args:
            runtime: Optional BoxLite runtime instance
            workspace_dir: Optional workspace directory (default: ~/.claudebox)

        Returns:
            List of SessionInfo with id, status, created_at, workspace_path

        Example:
            sessions = ClaudeBox.list_sessions()
            for session in sessions:
                print(f"{session.session_id}: {session.status} ({session.created_at})")
        """
        workspace_manager = WorkspaceManager(workspace_dir)
        sessions = workspace_manager.list_sessions()

        # Optionally enhance with runtime status
        if runtime:
            runtime_boxes = {box.name: box for box in runtime.list_info()}
            for session in sessions:
                box_name = SessionManager.get_box_name(session.session_id)
                if box_name in runtime_boxes:
                    box_info = runtime_boxes[box_name]
                    session.status = box_info.state  # "running", "stopped", etc.

        return sessions

    @classmethod
    async def cleanup_session(
        cls,
        session_id: str,
        remove_workspace: bool = False,
        runtime: Boxlite | None = None,
        workspace_dir: str | None = None,
    ):
        """
        Remove a session and optionally its workspace data.

        Args:
            session_id: Session to remove
            remove_workspace: If True, delete ~/.claudebox/sessions/{id}/ directory
            runtime: Optional BoxLite runtime instance
            workspace_dir: Optional workspace directory (default: ~/.claudebox)

        Example:
            # Remove box but keep workspace/logs
            await ClaudeBox.cleanup_session("old-project")

            # Remove everything
            await ClaudeBox.cleanup_session("temp-task", remove_workspace=True)
        """
        from claudebox.exceptions import SessionNotFoundError

        workspace_manager = WorkspaceManager(workspace_dir)

        if not workspace_manager.session_exists(session_id):
            raise SessionNotFoundError(session_id)

        # Stop and remove box if it exists
        runtime_instance = runtime or __import__("boxlite").Boxlite.default()
        box_name = SessionManager.get_box_name(session_id)

        try:
            # Try to remove box from runtime
            runtime_instance.remove(box_name)
        except Exception:
            # Box doesn't exist or already removed
            pass

        # Clean up workspace
        workspace_manager.cleanup_session(session_id, remove_workspace=remove_workspace)
