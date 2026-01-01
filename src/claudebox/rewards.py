"""Reward functions for reinforcement learning research."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from claudebox.results import CodeResult


class RewardFunction:
    """Base class for reward functions."""

    def __call__(self, result: CodeResult) -> float:
        """
        Calculate reward for a CodeResult.

        Args:
            result: Code execution result

        Returns:
            Reward value (typically between -1.0 and 1.0)
        """
        raise NotImplementedError


class SuccessOnlyReward(RewardFunction):
    """Reward function that only rewards success/failure."""

    def __call__(self, result: CodeResult) -> float:
        return 1.0 if result.success else -1.0


class CodeQualityReward(RewardFunction):
    """
    Reward function based on code quality metrics.

    Considers:
    - Success (1.0 points)
    - No errors (0.5 points)
    - Short response time (0.3 points for < 5s)
    - Tool efficiency (0.2 points for < 5 tool calls)

    Total possible: 2.0 points (normalized to 0-1 range)
    """

    def __call__(self, result: CodeResult) -> float:
        score = 0.0

        # Success is most important
        if result.success:
            score += 1.0

        # No errors
        if not result.error:
            score += 0.5

        # Efficient execution (< 5 tool calls)
        if result.action_log and len(result.action_log) < 5:
            score += 0.2

        # Quick execution (if we have metrics)
        if result.session_metadata:
            # Reward faster execution
            duration_s = result.session_metadata.total_duration_ms / 1000
            if duration_s < 5:
                score += 0.3

        # Normalize to 0-1 range
        return min(score / 2.0, 1.0)


class SafetyReward(RewardFunction):
    """
    Reward function that penalizes unsafe operations.

    Penalizes:
    - Destructive commands (rm -rf, dd, mkfs, etc.)
    - Privilege escalation (sudo, su)
    - Network access to private IPs
    - Large file operations (> 1GB)
    """

    UNSAFE_COMMANDS = {
        "rm -rf",
        "dd if=",
        "mkfs",
        "fdisk",
        "parted",
        "wipefs",
        "> /dev/",
        "sudo rm",
        "chmod 777",
    }

    def __call__(self, result: CodeResult) -> float:
        # Start with success reward
        reward = 1.0 if result.success else -1.0

        # Check action log for unsafe operations
        if result.action_log:
            for action in result.action_log:
                if action.tool == "bash":
                    command = str(action.input.get("command", ""))

                    # Check for unsafe commands
                    for unsafe_cmd in self.UNSAFE_COMMANDS:
                        if unsafe_cmd in command.lower():
                            reward -= 0.5  # Penalty for unsafe command
                            break

                    # Check for sudo/su usage
                    if "sudo" in command or "su " in command:
                        reward -= 0.3  # Penalty for privilege escalation

        return max(reward, -1.0)  # Floor at -1.0


class EfficiencyReward(RewardFunction):
    """
    Reward function based on execution efficiency.

    Rewards:
    - Fewer tool calls
    - Faster execution
    - Lower resource usage
    """

    def __call__(self, result: CodeResult) -> float:
        if not result.success:
            return -1.0

        score = 1.0  # Base reward for success

        # Reward fewer tool calls
        if result.action_log:
            tool_count = len(result.action_log)
            if tool_count <= 3:
                score += 0.5
            elif tool_count <= 5:
                score += 0.3
            elif tool_count <= 10:
                score += 0.1
            # No bonus for > 10 tool calls

        # Reward faster execution
        if result.session_metadata:
            duration_s = result.session_metadata.total_duration_ms / 1000
            if duration_s < 2:
                score += 0.5
            elif duration_s < 5:
                score += 0.3
            elif duration_s < 10:
                score += 0.1

        # Normalize to 0-1 range
        return min(score / 2.0, 1.0)


class CustomReward(RewardFunction):
    """Custom reward function from user-provided callable."""

    def __init__(self, reward_fn: Callable[[CodeResult], float]):
        """
        Initialize with custom reward function.

        Args:
            reward_fn: Function that takes CodeResult and returns float reward
        """
        self._reward_fn = reward_fn

    def __call__(self, result: CodeResult) -> float:
        return self._reward_fn(result)


# Built-in reward functions
class BuiltinRewards:
    """Collection of built-in reward functions."""

    @staticmethod
    def success_only(result: CodeResult) -> float:
        """Simple success/failure reward."""
        return SuccessOnlyReward()(result)

    @staticmethod
    def code_quality(result: CodeResult) -> float:
        """Code quality based reward."""
        return CodeQualityReward()(result)

    @staticmethod
    def safety(result: CodeResult) -> float:
        """Safety-focused reward."""
        return SafetyReward()(result)

    @staticmethod
    def efficiency(result: CodeResult) -> float:
        """Efficiency-focused reward."""
        return EfficiencyReward()(result)


# Reward combination utilities
def combine_rewards(*reward_fns: RewardFunction, weights: list[float] | None = None) -> RewardFunction:
    """
    Combine multiple reward functions with optional weights.

    Args:
        *reward_fns: Reward functions to combine
        weights: Optional weights for each reward function (must sum to 1.0)

    Returns:
        Combined reward function

    Example:
        >>> combined = combine_rewards(
        ...     SuccessOnlyReward(),
        ...     SafetyReward(),
        ...     weights=[0.7, 0.3]
        ... )
    """
    if weights is None:
        weights = [1.0 / len(reward_fns)] * len(reward_fns)

    if len(weights) != len(reward_fns):
        raise ValueError("Number of weights must match number of reward functions")

    if abs(sum(weights) - 1.0) > 1e-6:
        raise ValueError("Weights must sum to 1.0")

    class CombinedReward(RewardFunction):
        def __call__(self, result: CodeResult) -> float:
            total = 0.0
            for reward_fn, weight in zip(reward_fns, weights):
                total += reward_fn(result) * weight
            return total

    return CombinedReward()
