"""Result types for ClaudeBox."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

# Strip ANSI escape codes
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\][^\x07]*\x07|\x1b\[\?[0-9]+[hl]")


@dataclass
class CodeResult:
    """Result from Claude Code CLI execution."""

    success: bool
    response: str
    exit_code: int
    raw_output: str = ""
    error: str | None = None

    @classmethod
    def from_exec(cls, exit_code: int, stdout: str, stderr: str) -> CodeResult:
        """Create CodeResult from execution output."""
        output = ANSI_ESCAPE.sub("", stdout + stderr).strip()
        success = exit_code == 0
        response = output
        error = None

        try:
            if "{" in output:
                json_str = output[output.index("{") : output.rindex("}") + 1]
                data = json.loads(json_str)
                response = data.get("result", data.get("response", output))
                if data.get("is_error"):
                    error = data.get("error", "Unknown error")
                    success = False
        except (json.JSONDecodeError, ValueError):
            if not success:
                error = output

        return cls(
            success=success,
            response=response,
            exit_code=exit_code,
            raw_output=output,
            error=error,
        )
