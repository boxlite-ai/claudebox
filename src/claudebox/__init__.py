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
from claudebox.results import CodeResult

__version__ = "0.1.0"

__all__ = [
    "ClaudeBox",
    "CodeResult",
    "__version__",
]
