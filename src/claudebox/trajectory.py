"""Trajectory export for reinforcement learning training."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from claudebox.session import SessionManager
    from claudebox.workspace import SessionWorkspace


class TrajectoryExporter:
    """Export session trajectories for RL training."""

    def __init__(self, workspace: SessionWorkspace, session_manager: SessionManager):
        """
        Initialize trajectory exporter.

        Args:
            workspace: Session workspace
            session_manager: Session manager instance
        """
        self._workspace = workspace
        self._session_manager = session_manager

    def export_trajectory(self, format: str = "json") -> dict:
        """
        Export trajectory in specified format.

        Args:
            format: Export format ("json", "jsonl", "dict")

        Returns:
            Trajectory data

        Format:
            {
                "session_id": "...",
                "created_at": "...",
                "total_turns": 10,
                "total_duration_ms": 12345,
                "steps": [
                    {
                        "turn": 1,
                        "timestamp": "2025-01-01T10:00:00Z",
                        "action": {
                            "tool": "bash",
                            "input": {"command": "ls"},
                        },
                        "observation": {
                            "output": "file1.txt file2.txt",
                            "exit_code": 0,
                        },
                        "reward": 1.0,
                        "done": False,
                    },
                    ...
                ],
                "final_reward": 1.0,
                "success": True,
            }
        """
        # Load session metadata
        if not self._session_manager.session_exists():
            return {"error": "Session not found"}

        metadata = self._session_manager.load_session()

        # Load action logs
        from claudebox.logging import ActionLogger

        logger = ActionLogger(self._workspace.history_file)
        logs = logger.get_logs()

        # Build trajectory steps
        steps = []
        for i, log in enumerate(logs):
            step = {
                "turn": i + 1,
                "timestamp": log.timestamp,
                "action": {"tool": log.tool, "input": log.input},
                "observation": {"output": log.output, "duration_ms": log.duration_ms},
                "reward": None,  # Reward calculated separately
                "done": False,
            }
            steps.append(step)

        # Mark last step as done
        if steps:
            steps[-1]["done"] = True

        trajectory = {
            "session_id": metadata.session_id,
            "created_at": metadata.created_at,
            "total_turns": metadata.total_turns,
            "total_duration_ms": metadata.total_duration_ms,
            "steps": steps,
            "final_reward": None,  # To be calculated
            "success": True,  # Can be determined from last step
        }

        return trajectory

    def save_to_file(self, path: str, format: str = "json"):
        """
        Save trajectory to file.

        Args:
            path: Output file path
            format: Export format ("json", "jsonl")
        """
        trajectory = self.export_trajectory(format=format)

        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        if format == "jsonl":
            # Save steps as JSON Lines
            with open(path, "w") as f:
                for step in trajectory["steps"]:
                    f.write(json.dumps(step) + "\n")
        else:
            # Save as JSON
            with open(path, "w") as f:
                json.dump(trajectory, f, indent=2)

    def get_state_action_pairs(self) -> list[tuple[dict, dict, dict]]:
        """
        Get (state, action, next_state) tuples for RL training.

        Returns:
            List of (state, action, next_state) tuples

        Example state representation:
            {
                "working_dir": "/config/workspace",
                "files": ["file1.txt", "file2.txt"],
                "last_output": "...",
                "turn": 1,
            }
        """
        trajectory = self.export_trajectory()
        pairs = []

        steps = trajectory.get("steps", [])
        for i in range(len(steps) - 1):
            current_step = steps[i]
            next_step = steps[i + 1]

            state = {
                "turn": current_step["turn"],
                "last_output": current_step["observation"].get("output", ""),
                "working_dir": current_step.get("context", {}).get("working_dir", ""),
            }

            action = current_step["action"]

            next_state = {
                "turn": next_step["turn"],
                "last_output": next_step["observation"].get("output", ""),
                "working_dir": next_step.get("context", {}).get("working_dir", ""),
            }

            pairs.append((state, action, next_state))

        return pairs

    def calculate_trajectory_reward(self, reward_fn) -> float:
        """
        Calculate total reward for trajectory using reward function.

        Args:
            reward_fn: Reward function to apply to each step

        Returns:
            Total trajectory reward (sum or discounted sum)
        """
        trajectory = self.export_trajectory()
        total_reward = 0.0

        for step in trajectory.get("steps", []):
            # Create minimal CodeResult for reward calculation
            from claudebox.results import CodeResult

            result = CodeResult(
                success=step["observation"].get("exit_code") == 0
                if "exit_code" in step["observation"]
                else True,
                response=step["observation"].get("output", ""),
                exit_code=step["observation"].get("exit_code", 0),
                raw_output=step["observation"].get("output", ""),
                error=None,
            )

            reward = reward_fn(result)
            step["reward"] = reward
            total_reward += reward

        return total_reward

    def export_for_training(
        self, output_dir: str, reward_fn=None, include_metadata: bool = True
    ) -> str:
        """
        Export trajectory in format suitable for RL training frameworks.

        Args:
            output_dir: Output directory for training data
            reward_fn: Optional reward function to calculate rewards
            include_metadata: Include session metadata

        Returns:
            Path to exported file
        """
        trajectory = self.export_trajectory()

        if reward_fn:
            # Calculate rewards
            total_reward = self.calculate_trajectory_reward(reward_fn)
            trajectory["final_reward"] = total_reward

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save trajectory
        session_id = trajectory.get("session_id", "unknown")
        filename = output_path / f"trajectory_{session_id}.json"

        with open(filename, "w") as f:
            json.dump(trajectory, f, indent=2)

        return str(filename)

    @staticmethod
    def load_trajectory(path: str) -> dict:
        """
        Load trajectory from file.

        Args:
            path: Path to trajectory file

        Returns:
            Trajectory data
        """
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def merge_trajectories(trajectories: list[dict]) -> dict:
        """
        Merge multiple trajectories into a single dataset.

        Args:
            trajectories: List of trajectory dicts

        Returns:
            Merged trajectory dataset
        """
        all_steps = []
        total_turns = 0
        total_duration = 0

        for traj in trajectories:
            all_steps.extend(traj.get("steps", []))
            total_turns += traj.get("total_turns", 0)
            total_duration += traj.get("total_duration_ms", 0)

        return {
            "trajectories_count": len(trajectories),
            "total_turns": total_turns,
            "total_duration_ms": total_duration,
            "steps": all_steps,
        }
