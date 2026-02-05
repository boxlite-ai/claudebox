"""ClaudeBox - Run Claude Code CLI in isolated micro-VMs."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from collections.abc import AsyncGenerator, Callable
from typing import TYPE_CHECKING, Any

from claudebox.results import CodeResult, SessionMetadata
from claudebox.session import SessionManager
from claudebox.workspace import SessionInfo, WorkspaceManager

if TYPE_CHECKING:
    from boxlite import Box, Boxlite, Execution

logger = logging.getLogger("claudebox")


class ClaudeBox:
    """
    Run Claude Code CLI in isolated micro-VMs.

    Example:
        >>> async with ClaudeBox() as box:
        ...     result = await box.code("Create a hello world script")
        ...     print(result.response)
    """

    DEFAULT_IMAGE = "ghcr.io/boxlite-ai/claudebox-runtime:latest"

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
                self._session_workspace = self._workspace_manager.get_session_workspace(session_id)
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
        volumes_list.append((self._session_workspace.workspace_dir, "/config/workspace"))

        # Mount metadata directory
        volumes_list.append((self._session_workspace.metadata_dir, "/config/.claudebox"))

        self._runtime = runtime or Boxlite.default()

        # Determine image from template or use explicit image
        final_image = image
        if not final_image and template:
            from claudebox.templates import get_template_image

            final_image = get_template_image(template)
        if not final_image:
            final_image = self.DEFAULT_IMAGE

        # Store BoxOptions for deferred creation in __aenter__
        # (BoxLite's runtime.create() is async, so we can't call it in __init__)
        self._box_options = BoxOptions(
            image=final_image,
            cpus=cpus,
            memory_mib=memory_mib,
            disk_size_gb=disk_size_gb,
            env=env_list,
            volumes=volumes_list,
            ports=ports or [],
            auto_remove=auto_remove,
        )
        self._box: Box | None = None  # Created in __aenter__

        # Save env for exec() calls (auth + skill vars)
        self._claude_env = env_list or None

        # Claude CLI persistent process state (for stream())
        self._execution: Execution | None = None
        self._stdin: Any = None
        self._stdout: Any = None
        self._stderr: Any = None
        self._stderr_lines: list[str] = []
        self._stderr_task: asyncio.Task | None = None
        self._claude_session_id = "default"
        self._buffer = ""

        # Store session metadata (will be updated on first code() call)
        self._session_metadata: SessionMetadata | None = None

    async def __aenter__(self) -> ClaudeBox:
        # Create box now (deferred from __init__ since runtime.create() is async)
        self._box = await self._runtime.create(self._box_options)
        await self._box.__aenter__()

        # Setup non-root user (Claude CLI rejects --dangerously-skip-permissions as root)
        await self._setup_claude_user()

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
        # Close Claude CLI persistent process if running
        if self._stdin:
            await self._stdin.close()
        if self._execution:
            await self._execution.wait()
        if self._stderr_task and not self._stderr_task.done():
            self._stderr_task.cancel()
        self._execution = None
        self._stdin = None
        self._stdout = None

        # Update session metadata before exit
        if self._session_metadata:
            self._session_manager.update_session(self._session_metadata)

        # Clean up ephemeral workspace
        if not self._is_persistent:
            self._workspace_manager.cleanup_session(self._session_id, remove_workspace=True)

        return await self._box.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def id(self) -> str:
        if self._box is None:
            raise RuntimeError(
                "ClaudeBox not started. Use 'async with ClaudeBox() as box:' "
                "or call 'await box.__aenter__()' first."
            )
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

    async def _setup_claude_user(self) -> None:
        """Create non-root user for Claude CLI.

        Claude CLI rejects --dangerously-skip-permissions when running as root.
        We create a 'claude' user and run all CLI invocations via 'su -c'.
        """
        assert self._box is not None
        setup_script = (
            "id -u claude >/dev/null 2>&1 || useradd -m -s /bin/bash claude; "
            "mkdir -p /home/claude; "
            "chown -R claude:claude /home/claude; "
            "chmod -R 777 /config/workspace"
        )
        execution = await self._box.exec("sh", ["-c", setup_script], None)
        try:
            async for _ in execution.stdout():
                pass
        except Exception:
            pass
        result = await execution.wait()
        if result.exit_code == 0:
            logger.debug("Non-root user 'claude' ready")
        else:
            logger.warning("Failed to setup non-root user (exit %d)", result.exit_code)

    def _build_claude_cmd(self, claude_args: list[str]) -> tuple[str, list[str]]:
        """Build su -c command to run Claude CLI as non-root user."""
        import shlex

        parts = []
        if self._claude_env:
            for key, value in self._claude_env:
                parts.append(f"{key}={shlex.quote(value)}")
        parts.append("claude")
        parts.extend(claude_args)
        cmd_str = " ".join(parts)
        return "su", ["-c", cmd_str, "claude"]

    async def code(
        self,
        prompt: str,
        max_turns: int | None = None,
        allowed_tools: list[str] | None = None,
        disallowed_tools: list[str] | None = None,
    ) -> CodeResult:
        """Run Claude Code CLI with a prompt.

        Uses interactive stream-json mode (stdin/stdout) to send the prompt
        and receive streamed NDJSON responses. Runs as non-root user via su.
        """
        assert self._box is not None
        claude_args = [
            "--input-format",
            "stream-json",
            "--output-format",
            "stream-json",
            "--dangerously-skip-permissions",
            "--verbose",
        ]
        if max_turns is not None:
            claude_args.extend(["--max-turns", str(max_turns)])
        if allowed_tools:
            for tool in allowed_tools:
                claude_args.extend(["--allowedTools", tool])
        if disallowed_tools:
            for tool in disallowed_tools:
                claude_args.extend(["--disallowedTools", tool])

        mcp_config_path = getattr(self, "_mcp_config_path", None)
        if mcp_config_path:
            claude_args.extend(["--mcp-config", mcp_config_path])

        cmd, cmd_args = self._build_claude_cmd(claude_args)
        logger.debug("Starting Claude CLI: %s %s", cmd, cmd_args[:2])

        execution = await self._box.exec(cmd, cmd_args, None)
        stdin = execution.stdin()
        stdout = execution.stdout()
        stderr = execution.stderr()

        # Drain stderr in background
        stderr_lines: list[str] = []

        async def _drain_stderr():
            if stderr:
                try:
                    async for chunk in stderr:
                        text = (
                            chunk.decode("utf-8", errors="replace")
                            if isinstance(chunk, bytes)
                            else chunk
                        )
                        stderr_lines.append(text)
                        logger.debug("[stderr] %s", text.strip())
                except Exception:
                    pass

        stderr_task = asyncio.create_task(_drain_stderr())

        # Send prompt as NDJSON on stdin (interactive mode)
        msg = {
            "type": "user",
            "message": {"role": "user", "content": prompt},
            "session_id": "default",
            "parent_tool_use_id": None,
        }
        payload = json.dumps(msg) + "\n"
        logger.debug("Sending prompt (%d bytes)", len(payload))
        await stdin.send_input(payload.encode())

        # Read NDJSON stream, log each message, collect result
        buffer = ""
        result_data = None
        response_text = ""

        while True:
            try:
                chunk = await asyncio.wait_for(stdout.__anext__(), timeout=120)
            except StopAsyncIteration:
                break
            except asyncio.TimeoutError:
                logger.warning("Claude CLI timed out after 120s")
                break

            chunk_str = (
                chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else chunk
            )
            buffer += chunk_str

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = parsed.get("type")

                if msg_type == "assistant":
                    for block in parsed.get("message", {}).get("content", []):
                        if block.get("type") == "text":
                            logger.info("[claude] %s", block["text"])
                        elif block.get("type") == "tool_use":
                            logger.info("[tool_use] %s", block.get("name"))

                elif msg_type == "user":
                    for block in parsed.get("message", {}).get("content", []):
                        if block.get("type") == "tool_result" and block.get("is_error"):
                            logger.warning("[tool_error] %s", str(block.get("content", ""))[:200])

                elif msg_type == "result":
                    result_data = parsed
                    response_text = parsed.get("result", "")
                    cost = parsed.get("total_cost_usd", 0)
                    duration = parsed.get("duration_ms", 0)
                    logger.info("[done] cost=$%.4f duration=%.1fs", cost, duration / 1000)
                    break

            if result_data is not None:
                break

        # Close stdin and wait for process
        await stdin.close()
        exec_result = await execution.wait()
        stderr_task.cancel()

        # Build CodeResult from stream data
        is_error = (result_data or {}).get("is_error", False)
        success = exec_result.exit_code == 0 and not is_error
        error = None
        if is_error:
            error = response_text or "Unknown error"
        elif exec_result.exit_code != 0:
            error = "".join(stderr_lines) or f"Exit code {exec_result.exit_code}"
            if not response_text:
                response_text = error

        code_result = CodeResult(
            success=success,
            response=response_text,
            exit_code=exec_result.exit_code,
            raw_output=response_text,
            error=error,
        )

        # Calculate reward if reward function provided
        if self._reward_fn:
            code_result.reward = self._reward_fn(code_result)

        return code_result

    async def stream(
        self,
        prompt: str,
    ) -> AsyncGenerator[dict, None]:
        """Stream Claude Code responses using a persistent process.

        Uses the stream-json NDJSON protocol for real-time streaming
        and multi-turn context preservation. The Claude CLI process
        is started on first call and reused for subsequent messages.

        Args:
            prompt: The message to send to Claude.

        Yields:
            Parsed JSON messages as they arrive from Claude CLI.

        Example:
            >>> async with ClaudeBox() as box:
            ...     async for msg in box.stream("Create hello.py"):
            ...         if msg.get("type") == "assistant":
            ...             print(msg)
        """
        if not self._execution:
            await self._start_claude()
        async for msg in self._send_message(prompt):
            yield msg

    async def _start_claude(self) -> None:
        """Start Claude CLI in stream-json mode for multi-turn streaming."""
        assert self._box is not None
        claude_args = [
            "--input-format",
            "stream-json",
            "--output-format",
            "stream-json",
            "--dangerously-skip-permissions",
            "--verbose",
        ]
        mcp_config_path = getattr(self, "_mcp_config_path", None)
        if mcp_config_path:
            claude_args.extend(["--mcp-config", mcp_config_path])

        cmd, cmd_args = self._build_claude_cmd(claude_args)
        logger.debug("Starting Claude CLI (persistent): %s", cmd)

        self._execution = await self._box.exec(cmd, cmd_args, None)
        self._stdin = self._execution.stdin()
        self._stdout = self._execution.stdout()
        self._stderr = self._execution.stderr()
        self._buffer = ""
        self._stderr_lines = []

        # Drain stderr in background so errors are captured
        if self._stderr:
            self._stderr_task = asyncio.create_task(self._drain_stderr())

    async def _drain_stderr(self) -> None:
        """Collect stderr output in the background."""
        assert self._stderr is not None
        try:
            async for chunk in self._stderr:
                text = (
                    chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else chunk
                )
                self._stderr_lines.append(text)
        except Exception:
            pass

    async def _send_message(self, content: str) -> AsyncGenerator[dict, None]:
        """Send a message via NDJSON and yield streamed responses.

        BoxLite streams stdout in fixed-size chunks (not line-buffered),
        so we buffer data and parse complete JSON lines delimited by newlines.
        Uses explicit __anext__() with timeout matching the boxlite example.
        """
        if not self._stdin or not self._stdout:
            raise RuntimeError("Claude CLI not started")

        msg = {
            "type": "user",
            "message": {"role": "user", "content": content},
            "session_id": self._claude_session_id,
            "parent_tool_use_id": None,
        }
        payload = json.dumps(msg) + "\n"
        await self._stdin.send_input(payload.encode())

        while True:
            try:
                chunk = await asyncio.wait_for(self._stdout.__anext__(), timeout=120)
            except StopAsyncIteration:
                self._execution = None
                break
            except asyncio.TimeoutError:
                break

            chunk_str = (
                chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else chunk
            )
            self._buffer += chunk_str

            while "\n" in self._buffer:
                line, self._buffer = self._buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if parsed.get("session_id"):
                    self._claude_session_id = parsed["session_id"]

                yield parsed

                if parsed.get("type") == "result":
                    return

    @property
    def stderr_output(self) -> str:
        """Get captured stderr output (useful for debugging failures)."""
        return "".join(self._stderr_lines)

    def __repr__(self) -> str:
        box_id = self._box.id if self._box else "<not started>"
        return f"ClaudeBox(id={box_id}, session_id={self.session_id})"

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
